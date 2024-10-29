from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from ..keyboards import inline, reply
from core.loggers.bot_logger import Logger
from core.utils import texts

router = Router()


@router.message(Command('account'))
async def account(message: Message, log: Logger):
    log.button('/account')
    fullname = f'{message.from_user.first_name} {message.from_user.last_name}' if message.from_user.last_name is not None else message.from_user.first_name
    await message.answer(await texts.account(fullname),
                         reply_markup=inline.kb_account())


@router.callback_query(F.data == 'account')
async def back_account(call: CallbackQuery, log: Logger):
    log.button('Назад в личный кабинет')
    fullname = f'{call.from_user.first_name} {call.from_user.last_name}' if call.from_user.last_name is not None else call.from_user.first_name
    await call.message.edit_text(await texts.account(fullname),
                                 reply_markup=inline.kb_account())


@router.message(Command('tickets_help'))
async def tickets_help(message: Message, log: Logger):
    log.button('/tickets_help')
    await message.answer("Открытые заявки - заявки в работе\n"
                         "История заявок - посмотреть историю закрытых заявок\n",
                         reply_markup=inline.kb_tickets_help())
