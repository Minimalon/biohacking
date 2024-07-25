from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def echo(message: Message, state: FSMContext):
    await message.answer(message.text)
