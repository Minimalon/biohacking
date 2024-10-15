import re
from datetime import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.payload import decode_payload

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import Client, CardInfo, CardBalance
from core.database.query import Database
from core.filters.is_contact import IsTrueContact
from core.loggers.bot_logger import Logger
from core.services.start.keyboards import inline, reply
from core.utils import texts
from core.utils.qr import generate_qr
from ..callback_data import Sex
from ..pd_models import Profile
from ..states import *

router = Router()

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove


async def get_phone(client_phone):
    client_phone = ''.join(re.findall(r'[0-9]*', client_phone))
    if re.findall(r'^89', client_phone):
        return re.sub(r'^89', '79', client_phone)
    return client_phone


@router.message(CommandStart(deep_link=True))
async def deeplink_start(message: Message, command: CommandObject, state: FSMContext, log: Logger, db: Database):
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
        await message.bot.send_video(message.chat.id,
                                     FSInputFile(Path(config.dir_path, 'files', 'tutorial_registration.mp4')))
        await message.answer(text, reply_markup=reply.kb_registration())
        log.error(f"Пользователь {message.from_user.id} не зарегистрирован")
        return
    cs_card_balance = await cs.get_card_balance(message.from_user.id)
    profile = Profile(
        cs_client=cs_client,
        cs_card=cs_client_card,
        cs_card_balance=cs_card_balance
    )
    await message.bot.send_photo(
        message.chat.id,
        photo=FSInputFile(await generate_qr(message.from_user.id)),
        caption=await texts.profile(profile),
        reply_markup=inline.kb_start()
    )
    await state.update_data(deeplink=deeplink_args)



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
        await message.bot.send_video(message.chat.id,
                                     FSInputFile(Path(config.dir_path, 'files', 'tutorial_registration.mp4')))
        await message.answer(text, reply_markup=reply.kb_registration())
        log.error(f"Пользователь {message.from_user.id} не зарегистрирован")
        return
    cs_card_balance = await cs.get_card_balance(message.from_user.id)
    profile = Profile(
        cs_client=cs_client,
        cs_card=cs_client_card,
        cs_card_balance=cs_card_balance
    )
    await message.bot.send_photo(
        message.chat.id,
        photo=FSInputFile(await generate_qr(message.from_user.id)),
        caption=await texts.profile(profile),
        reply_markup=inline.kb_start()
    )


@router.message(F.contact, IsTrueContact())
async def get_true_contact(message: Message, state: FSMContext, log: Logger, db: Database):
    log.info(f"Отправил свой сотовый '{message.contact.phone_number}'")
    if not await db.get_client(message.from_user.id):
        await db.add_client(
            phone_number=await get_phone(message.contact.phone_number),
            first_name=message.contact.first_name,
            last_name=message.contact.last_name,
            username=message.from_user.username,
            user_id=message.from_user.id,
            chat_id=message.chat.id
        )
    await state.set_state(RegistrationStates.birthday)
    await message.answer('Введите день рождения\nПример: 01.01.1990', reply_markup=ReplyKeyboardRemove())


@router.message(F.contact)
async def get_fake_contact(message: Message, log_e: Logger):
    log_e.error(f'Отправили чужой сотовый "{message.contact.phone_number}"')
    await message.answer(texts.fake_phone)


@router.message(RegistrationStates.birthday)
async def get_birthday(message: Message, state: FSMContext, log: Logger):
    log.info(f"Отправил дату рождения '{message.text}'")
    try:
        bd = datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        log.error(f"Неверный формат дня рождения '{message.text}'")
        await message.answer(f'{texts.error_head}'
                             f'Неверный формат дня рождения\nПример: 01.01.1990')
        return
    await state.update_data(reg_birthday=bd.strftime('%Y-%m-%d'))
    await state.set_state(RegistrationStates.name)
    await message.answer('Напишите фамилию и имя')


@router.message(RegistrationStates.name)
async def get_name(message: Message, state: FSMContext, log: Logger):
    log.info(f"Отправил имя '{message.text}'")
    await state.update_data(reg_name=message.text)
    await state.set_state(RegistrationStates.sex)
    await message.answer('Выберите пол', reply_markup=inline.kb_sex())


@router.callback_query(RegistrationStates.sex, Sex.filter())
async def get_sex(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: Sex, db: Database):
    data = await state.get_data()
    await call.message.delete()
    sex_name = 'Мужчина' if callback_data.sex == 0 else 'Женщина'
    log.info(f"Выбрал пол '{sex_name}'")

    cs = CS()
    client = await db.get_client(call.from_user.id)
    cs_client = Client(
        idclient=call.from_user.id,
        sex=callback_data.sex,
        birthday=data['reg_birthday'],
        phonenumber=client.phone_number,
        name=data['reg_name']
    )
    cs_card = CardInfo(
        idcard=call.from_user.id,
        number=call.from_user.id,
        idclient=call.from_user.id
    )
    await cs.create_client(cs_client)
    await cs.create_card(cs_card)

    cs_client = await cs.get_client_by_id(call.from_user.id)
    cs_client_card = await cs.get_card_by_id(call.from_user.id)
    cs_card_balance = await cs.get_card_balance(call.from_user.id)
    profile = Profile(
        cs_client=cs_client,
        cs_card=cs_client_card,
        cs_card_balance=cs_card_balance
    )

    if data.get('deeplink'):
        await db.add_referral(call.from_user.id, int(data['deeplink']))

    log.success(f"Пользователь {call.from_user.id} зарегистрирован")
    await call.message.bot.send_photo(
        call.message.chat.id,
        photo=FSInputFile(await generate_qr(call.from_user.id)),
        caption=await texts.profile(profile)
    )
    await state.clear()


@router.callback_query(F.data == 'update_start_menu')
async def update_start_menu(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button("Обновить информацию о карте")
    cs = CS()
    cs_client = await cs.get_client_by_id(call.from_user.id)
    cs_client_card = await cs.get_card_by_id(call.from_user.id)
    cs_card_balance = await cs.get_card_balance(call.from_user.id)
    profile = Profile(
        cs_client=cs_client,
        cs_card=cs_client_card,
        cs_card_balance=cs_card_balance
    )
    await call.message.delete()
    await call.message.bot.send_photo(
        call.message.chat.id,
        photo=FSInputFile(await generate_qr(call.from_user.id)),
        caption=await texts.profile(profile),
        reply_markup=inline.kb_start()
    )
