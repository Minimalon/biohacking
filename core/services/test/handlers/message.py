from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove

import config
from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.utils import texts
from ..keyboards import inline, reply
from ..states import TestAcceptPhoto

router = Router()


@router.message(Command('test'))
async def test(message: Message, state: FSMContext, db: Database):
    await message.bot.send_photo(message.chat.id,
                                 photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                 caption=texts.success_head + f"Вам начислены приветственные {100 * 100} рублей за регистрацию.",
                                 reply_markup=ReplyKeyboardRemove())


@router.message(TestAcceptPhoto.photo, F.content_type.in_([ContentType.PHOTO]))
async def accept_photo(message: Message, state: FSMContext, db: Database):
    await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption)


