from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.database.model import ClientRolesEnum
from core.database.query import Database
from ..keyboards import inline, reply

router = Router()


@router.message(F.text == "test")
async def test(message: Message, state: FSMContext, db: Database):
    await db.create_role_client(message.from_user.id, ClientRolesEnum.ADMIN)


