from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

import config
from core.artix.CS.cs import CS
from core.database.award_query import AwardQuery
from core.database.model import ClientRolesEnum
from core.database.query import Database
from ..callback_data import CbUpdateTicketStatus, CbHelpTicket, CbCloseHelpTicket
from ..keyboards import inline, reply
from core.loggers.bot_logger import Logger
from core.utils import texts
from ...referals.keyboards.inline import kb_ref_menu
from ...start.pd_models.profile_bonuses import Profile

router = Router()

bonus_query = AwardQuery()


@router.callback_query(F.data == 'referals_program')
async def need_help(call: CallbackQuery, log: Logger):
    log.button('Парнерская программа')
    await call.message.bot.send_photo(chat_id=call.message.chat.id,
                                      photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                      caption=await texts.referals_program(),
                                      reply_markup=kb_ref_menu())
