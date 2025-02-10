from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.loggers.bot_logger import Logger
from core.utils import texts
from core.utils.chatgpt import ChatGPTIntegration, GPTMessage, GPTRole
from ..keyboards import inline
from ..states import GPTDialogState

router = Router()
chatgpt = ChatGPTIntegration()


@router.callback_query(F.data == 'dialog_gpt')
async def dialog_gpt(call: CallbackQuery, log: Logger, state: FSMContext):
    log.button('База знаний')
    await chatgpt.set_messages([
        GPTMessage(role=GPTRole.SYSTEM, content=texts.gpt_start_message)
    ])
    await state.update_data(gpt_messages=await chatgpt.get_messages())
    await state.set_state(GPTDialogState.wait_answer)
    await call.message.delete()
    await call.message.answer(texts.gpt_to_user_start_msg, reply_markup=inline.kb_gpt())


@router.message(GPTDialogState.wait_answer)
async def wait_answer(message: Message, log: Logger, state: FSMContext):
    log.info(f'Вопрос: {message.text}')
    await message.answer('Ожидание ответа может занять пару минут')
    data = await state.get_data()
    await chatgpt.set_messages(data.get('gpt_messages'))
    answer = await chatgpt.send_message(
        GPTMessage(
            role=GPTRole.USER,
            content=message.text
        )
    )
    log.info(f'Ответ: {answer}')
    await state.update_data(gpt_messages=await chatgpt.get_messages())
    await message.answer(texts.answer_gpt_head + answer, reply_markup=inline.kb_gpt(), parse_mode=ParseMode.MARKDOWN)
    await state.clear()


@router.callback_query(F.data == 'stop_gpt_dialog')
async def stop_gpt_dialog(call: CallbackQuery, log: Logger, state: FSMContext):
    log.info('Закончить диалог')
    await call.message.edit_text(f'Благодарю за беседу! Если возникнут вопросы, всегда рад помочь.')
    await state.clear()
