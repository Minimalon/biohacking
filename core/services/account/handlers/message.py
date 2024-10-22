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
    await message.answer(await texts.account(message.from_user.first_name),
                         reply_markup=inline.kb_account())


@router.callback_query(F.data == 'account')
async def back_account(call: CallbackQuery, log: Logger):
    log.button('Назад в личный кабинет')
    await call.message.edit_text(await texts.account(call.from_user.first_name),
                                 reply_markup=inline.kb_account())


@router.message(Command('tickets_help'))
async def tickets_help(message: Message, log: Logger):
    log.button('/tickets_help')
    await message.answer("Открытые заявки - заявки в работе\n"
                         "История заявок - посмотреть историю закрытых заявок\n",
                         reply_markup=inline.kb_tickets_help())
