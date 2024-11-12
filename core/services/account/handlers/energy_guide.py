from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

import config
from core.database.bonus_query import BonusQuery
from core.loggers.bot_logger import Logger
from core.utils import texts

router = Router()

bonus_query = BonusQuery()


@router.callback_query(F.data == 'energy_guide')
async def need_help(call: CallbackQuery, log: Logger):
    log.button('Получить подарок!')
    await call.message.bot.send_photo(chat_id=call.message.chat.id,
                                      photo=FSInputFile(Path(config.dir_path, 'files', '9.jpg')),
                                      caption=await texts.energy_awards())
