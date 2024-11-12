from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.artix.cash.querys import Artix
from core.artix.foreman.foreman import get_cashes, get_cash
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..callback_data import ShopCreateUser
from ..keyboards import inline
from ..states import CreateUserState

router = Router()


@router.callback_query(F.data == 'create_user')
async def create_user(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Создать пользователя на кассе')
    cashes = await get_cashes('facts.artix_shopname ~ biohacking')
    log.debug(', '.join([str(cash.shopcode) for cash in cashes]))
    await call.message.edit_text('Выберите магазин', reply_markup=inline.kb_select_shop(cashes))
    await state.set_state(CreateUserState.select_shop)


@router.callback_query(ShopCreateUser.filter())
async def select_shop(call: CallbackQuery, state: FSMContext, callback_data: ShopCreateUser, log: Logger):
    log.info(f'Выбрал магазин {callback_data.shopcode}')
    await call.message.delete()
    await call.message.answer('Введите ФИО пользователя')
    await state.update_data(create_user_shopcode=callback_data.shopcode)
    await state.set_state(CreateUserState.fio)


@router.message(CreateUserState.fio)
async def fio(message: Message, state: FSMContext, log: Logger):
    log.info(f'ФИО пользователя {message.text}')
    data = await state.get_data()
    foreman_cash = await get_cash(data.get('create_user_shopcode'))
    artix = Artix(foreman_cash.ip())
    user_code = await artix.create_mol(message.text)
    await message.answer(await texts.create_user(
        fio=message.text,
        user_code=user_code,
        cash_code=data.get('create_user_shopcode'),
    ))
    log.success(f'Пользователь "{user_code}: {message.text}" создан')
    await state.clear()
