from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.database.model import ClientRolesEnum
from core.database.query import Database
from ..keyboards import inline, reply
from ..states import TestAcceptPhoto

router = Router()


@router.message(Command('test'))
async def test(message: Message, state: FSMContext, db: Database):
    await message.answer('Жду фоточку')
    await state.set_state(TestAcceptPhoto.photo)


@router.message(TestAcceptPhoto.photo, F.content_type.in_([ContentType.PHOTO]))
async def accept_photo(message: Message, state: FSMContext, db: Database):
    await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption)


