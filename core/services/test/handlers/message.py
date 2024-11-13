from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ContentType, ChatMemberStatus
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
    user_channel_status = await message.bot.get_chat_member(chat_id='@bogonaft', user_id=message.from_user.id)

    if user_channel_status.status != ChatMemberStatus.LEFT:
        await message.answer('Спасибо за подписку!')
    else:
        await message.answer('Для начала подпишись на наш канал')


@router.message(TestAcceptPhoto.photo, F.content_type.in_([ContentType.PHOTO]))
async def accept_photo(message: Message, state: FSMContext, db: Database):
    await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption)


