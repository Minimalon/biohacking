from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.utils import texts
from ..keyboards import inline, reply

router = Router()


@router.callback_query(F.data == 'analytics')
async def analytics(call: CallbackQuery, state: FSMContext):
    await call.answer(texts.is_develope)
