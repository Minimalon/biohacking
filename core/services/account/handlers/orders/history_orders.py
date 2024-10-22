from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from core.loggers.bot_logger import Logger
from core.utils import texts

router = Router()


@router.callback_query(F.data == 'history_orders')
async def bonus_card(call: CallbackQuery, log: Logger):
    log.button('История заказов')
    await call.answer(texts.is_develope)
