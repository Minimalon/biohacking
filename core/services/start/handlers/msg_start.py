import re
from datetime import datetime
from pathlib import Path
import unicodedata

from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.payload import decode_payload
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import (
    Client,
    CardInfo,
    CardBalance,
    Asset,
    AssetType,
    AwardsType,
)
from core.commands.commands import set_command_for_user
from core.database.award_query import AwardQuery
from core.database.model import RegistrationAssets
from core.database.query import Database
from core.filters.is_contact import IsTrueContact
from core.loggers.bot_logger import Logger
from core.services.start.keyboards import inline, reply
from core.utils import texts
from core.utils.qr import generate_qr
from ..pd_models.profile_bonuses import Profile
from ..states import *
from ...account.keyboards.inline import kb_account

router = Router()
aq = AwardQuery()


async def get_phone(client_phone):
    client_phone = "".join(re.findall(r"[0-9]*", client_phone))
    if re.findall(r"^89", client_phone):
        return re.sub(r"^89", "79", client_phone)
    return client_phone


@router.message(CommandStart(deep_link=True))
async def deeplink_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    log: Logger,
    db: Database,
):
    deeplink_args = decode_payload(command.args)
    log.info(f'deeplink_start "{deeplink_args}"')
    cs = CS()
    cs_client = await cs.get_client_by_id(message.from_user.id)
    cs_client_card = await cs.get_card_by_id(message.from_user.id)
    db_client = await db.get_client(message.from_user.id)
    if not cs_client or not cs_client_card or not db_client:
        text = (
            f"{texts.auth_head}"
            "Для начала работы с ботом нажмите кнопку 'Регистрация'"
        )
        await message.bot.send_video(
            message.chat.id,
            FSInputFile(Path(config.dir_path, "files", "tutorial_registration.mp4")),
        )
        await message.answer(text, reply_markup=reply.kb_registration())
        log.error(f"Пользователь {message.from_user.id} не зарегистрирован")
        await state.update_data(deeplink=deeplink_args)
        return
    fullname = (
        f"{message.from_user.first_name} {message.from_user.last_name}"
        if message.from_user.last_name is not None
        else message.from_user.first_name
    )
    await set_command_for_user(message.bot, message.chat.id)
    await message.answer(await texts.account(fullname), reply_markup=kb_account())


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, log: Logger, db: Database):
    log.button("/start")
    cs = CS()
    cs_client = await cs.get_client_by_id(message.from_user.id)
    cs_client_card = await cs.get_card_by_id(message.from_user.id)
    db_client = await db.get_client(message.from_user.id)
    if not cs_client or not cs_client_card or not db_client:
        text = (
            f"{texts.auth_head}"
            "Для начала работы с ботом нажмите кнопку 'Регистрация'"
        )
        await message.bot.send_video(
            message.chat.id,
            FSInputFile(Path(config.dir_path, "files", "tutorial_registration.mp4")),
        )
        await message.answer(text, reply_markup=reply.kb_registration())
        log.error(f"Пользователь {message.from_user.id} не зарегистрирован")
        return
    fullname = (
        f"{message.from_user.first_name} {message.from_user.last_name}"
        if message.from_user.last_name is not None
        else message.from_user.first_name
    )
    await set_command_for_user(message.bot, message.chat.id)
    await message.answer(await texts.account(fullname), reply_markup=kb_account())


@router.message(F.contact, IsTrueContact())
async def get_true_contact(
    message: Message, state: FSMContext, log: Logger, db: Database
):
    log.info(f"Отправил свой сотовый '{message.contact.phone_number}'")
    if await db.get_client(message.from_user.id) is None:
        await db.add_client(
            phone_number=await get_phone(message.contact.phone_number),
            first_name=message.contact.first_name,
            last_name=message.contact.last_name,
            username=message.from_user.username,
            user_id=message.from_user.id,
            chat_id=message.chat.id,
        )
    await state.set_state(RegistrationStates.birthday)
    await message.answer(
        "Введите день рождения\nПример: 01.01.1990", reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.contact)
async def get_fake_contact(message: Message, log_e: Logger):
    log_e.error(f'Отправили чужой сотовый "{message.contact.phone_number}"')
    await message.answer(texts.fake_phone)


@router.message(RegistrationStates.birthday)
async def get_birthday(message: Message, state: FSMContext, log: Logger):
    log.info(f"Отправил дату рождения '{message.text}'")
    try:
        bd = datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        log.error(f"Неверный формат дня рождения '{message.text}'")
        await message.answer(
            f"{texts.error_head}"
            f"Неверный формат дня рождения\nПример: 01.01.1990\n"
            f"Отправьте ответным сообщением дату рождения."
        )
        return
    await state.update_data(reg_birthday=bd.strftime("%Y-%m-%d"))
    await state.set_state(RegistrationStates.wait_name)
    await message.answer(
        f"Ваше имя: <b>{message.from_user.first_name}</b>",
        reply_markup=inline.kb_name(),
    )


@router.callback_query(F.data == "registration_name")
async def get_name(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button("Ввести имя самому")
    await state.set_state(RegistrationStates.name)
    await call.message.edit_text("Отправьте ответным сообщением ваше имя")


@router.message(RegistrationStates.name)
async def accept_name(message: Message, state: FSMContext, log: Logger, db: Database):
    log.info(f"Отправил имя '{message.text}'")
    await state.update_data(reg_name=message.text)
    await after_registaration(
        message.from_user.id, message.text, message, state, log, db
    )


@router.callback_query(F.data == "complete_registration")
async def complete_registration(
    call: CallbackQuery, state: FSMContext, log: Logger, db: Database
):
    log.button("Завершить регистрацию")
    await call.message.delete()
    await after_registaration(
        call.from_user.id, call.from_user.first_name, call.message, state, log, db
    )


@router.callback_query(F.data == "update_start_menu")
async def update_start_menu(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button("Обновить информацию о карте")
    cs = CS()
    cs_client = await cs.get_client_by_id(call.from_user.id)
    cs_client_card = await cs.get_card_by_id(call.from_user.id)
    cs_card_balance = await cs.get_card_balance(call.from_user.id)
    profile = Profile(
        cs_client=cs_client, cs_card=cs_client_card, cs_card_balance=cs_card_balance
    )
    await call.message.delete()
    await call.message.bot.send_photo(
        call.message.chat.id,
        photo=FSInputFile(await generate_qr(call.from_user.id)),
        caption=await texts.profile(profile),
        reply_markup=inline.kb_start(),
    )


async def after_registaration(
    user_id: int,
    user_name: str,
    message: Message,
    state: FSMContext,
    log: Logger,
    db: Database,
):
    data = await state.get_data()

    cs = CS()
    client = await db.get_client(message.chat.id)

    if data.get("reg_birthday") is None:
        await state.set_state(RegistrationStates.birthday)
        await message.answer(
            "Введите день рождения\nПример: 01.01.1990",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    cs_client = Client(
        idclient=user_id,
        birthday=data["reg_birthday"],
        phonenumber=client.phone_number,
        name="".join(c for c in user_name if unicodedata.category(c) != "So"),
    )
    cs_card = CardInfo(
        idcard=user_id,
        number=user_id,
        idclient=user_id,
    )
    client_response = await cs.create_client(cs_client)
    if not client_response.ok:
        log.error(f"Не получилось добавить клиента в бонусную систему")
        log.info("Напиши ответным сообщением ваше Имя без смайликов")
        await message.answer(
            texts.error_head + "Ваше имя не было добавлено в бонусную систему\n"
            "Напиши ответным сообщением ваше <b>Имя</b> без смайликов"
        )
        await state.set_state(RegistrationStates.name)
        return
    await cs.create_card(cs_card)

    succes_reg_asset = 100
    if await aq.get_reg_award_by_user_id(user_id) is None:
        log.debug(f"Пользователю {user_id} будут добавленны баллы за регистрацию")
        await aq.add_registration_award(
            RegistrationAssets(user_id=user_id, amount=succes_reg_asset * 100)
        )
        await message.bot.send_photo(
            message.chat.id,
            photo=FSInputFile(Path(config.dir_path, "files", "8.jpg")),
            caption=texts.information_head + f"Спасибо за регистрацию!\n"
            f"Завтра вам будет начислено {succes_reg_asset} баллов за регистрацию.\n"
            f"С нетерпением ждём вашего визита!",
            reply_markup=ReplyKeyboardRemove(),
        )
    if data.get("deeplink") is not None:
        log.debug(f'deeplink = {data.get("deeplink")}')
    if data.get("deeplink") is not None:
        log.debug(f'Пользователю {user_id} добавлен реферал {data["deeplink"]}')
        await db.add_referral(user_id, int(data["deeplink"]))
        await state.update_data(deeplink=None)

    log.success(f"Пользователь {user_id} зарегистрирован")
    await message.answer(await texts.account(user_name), reply_markup=kb_account())
    await set_command_for_user(message.bot, message.chat.id)
    await state.set_state(RegistrationStates.none)


@router.message(Command("clear"))
async def clear(message: Message, state: FSMContext, log: Logger):
    log.info(f"Пользователь {message.from_user.id} очистил бота")
    try:
        await message.answer(
            texts.success_head + "Бот был очищен", reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        pass
    await state.clear()
