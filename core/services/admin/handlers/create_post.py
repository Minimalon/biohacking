import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramRetryAfter

from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..keyboards import inline, reply
from ..states import CreatePostState

router = Router()


@router.callback_query(F.data == 'create_post')
async def create_post(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Создать рекламную рассылку')
    await call.message.edit_text("Отправьте сообщение. В сообщение должно быть максимум 1 картинка")
    await state.set_state(CreatePostState.text)


@router.message(CreatePostState.text)
async def prepare_send_post(message: Message, state: FSMContext, log: Logger):
    log.info(f"Текст рекламной рассылки '{message.text}'")
    if message.caption is not None:
        if len(message.caption) > 1024:
            await message.answer(texts.error_head + f"Слишком длинное описание. Укоротите на {len(message.caption) - 1024} символов")
            return
    elif message.text is not None:
        if len(message.text) > 4096:
            await message.answer(texts.error_head + f"Слишком длинное сообщение. Укоротите на {len(message.caption) - 4096} символов")
            return
    await state.update_data(create_post_msg_id=message.message_id)
    await state.set_state(CreatePostState.prepared)
    await message.bot.copy_message(message.chat.id, message.from_user.id, message.message_id,
                                   reply_markup=inline.kb_send_post())


@router.callback_query(F.data == 'send_post')
async def send_post(call: CallbackQuery, state: FSMContext, log: Logger, db: Database):
    log.button('Отправить рекламную рассылку')
    data = await state.get_data()
    await call.message.delete()
    await call.message.answer("Рассылка началась. Ожидайте...")
    count = 0
    for client in await db.get_all_clients():
        try:
            await call.bot.copy_message(client.user_id, call.from_user.id, data['create_post_msg_id'])
            await asyncio.sleep(0.05)
            count += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            log.exception(e)
    await call.message.answer(f"Рассылка завершена. Отправлена {count} клиентам.")
    await state.clear()
