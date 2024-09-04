from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.loggers.bot_logger import Logger
from ..keyboards import inline, reply

router = Router()


@router.message(Command("checklist"))
async def start(message: Message, state: FSMContext, log: Logger):
    log.button('/checklist')
    await message.answer("Выберите нужную операцию", reply_markup=inline.kb_checklist())
