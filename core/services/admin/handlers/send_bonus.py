from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.artix.CS.cs import CS
from core.artix.CS.pd_model import Asset, AssetType, AwardsType
from core.artix.cash.querys import Artix
from core.artix.foreman.foreman import get_cashes, get_cash
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..callback_data import ShopCreateUser
from ..keyboards import inline
from ..states import CreateUserState, SendBonusState

router = Router()


@router.callback_query(F.data == 'send_bonuses')
async def send_bonuses(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Зачислить бонусы')
    await call.message.edit_text('Введите номер карты пользователя')
    await state.set_state(SendBonusState.idcard)

@router.message(SendBonusState.idcard)
async def send_bonuses_idcard(message: Message, state: FSMContext, log: Logger):
    log.info(f'Номер карты {message.text}')
    if not message.text.isdigit():
        await message.answer(texts.error_head + 'Номер карты должен содержать только цифры\nВведите номер карты еще раз')
        log.error('Номер карты должен содержать только цифры')
        return
    await state.update_data(idcard_award=message.text)
    await message.answer('Введите сумму бонусов в рублях без копеек')
    await state.set_state(SendBonusState.award)

@router.message(SendBonusState.award)
async def send_bonuses_award(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    log.info(f'Сумма бонусов {message.text}')
    if not message.text.isdigit():
        await message.answer(
            texts.error_head + 'Сумма бонусов должна содержать только цифры\nВведите номер карты еще раз')
        log.error('Сумма бонусов должна содержать только цифры')
        return

    cs = CS()
    response = await cs.post_asset(Asset(
        cardNumber=data.get('idcard_award'),
        amount=message.text,
        type=AssetType.ADD,
        additionalInfo={
            'type': AwardsType.ADMIN_AWARD
        }
    ))
    if response.ok:
        await message.answer(texts.success_head + 'Бонусы успешно зачислены')
        log.success('Бонусы успешно зачислены')
    else:
        await message.answer(f"{texts.error_head}Бонусы не были зачислены\n{await response.text()}")
        log.error(await response.text())
    await state.clear()
