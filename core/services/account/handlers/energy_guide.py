from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.bonus_query import BonusQuery
from core.loggers.bot_logger import Logger
from core.utils import texts

router = Router()

bonus_query = BonusQuery()


@router.callback_query(F.data == 'energy_guide')
async def need_help(call: CallbackQuery, log: Logger):
    log.button('Получить подарок!')
    await call.message.edit_text(await texts.energy_awards())
