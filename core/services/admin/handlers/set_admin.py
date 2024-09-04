from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.commands.admins import get_admin_commands
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..keyboards import inline, reply
from ..states import SetAdminState

router = Router()


@router.callback_query(F.data == 'set_admin')
async def enter_phone(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button("Дать права админа в боте")
    await call.message.edit_text('Введите сотовый пользователя зарегестрированого в боте\n'
                                 'Пример: 79279999999')
    await state.set_state(SetAdminState.phone)

@router.message(SetAdminState.phone)
async def set_phone(message: Message, state: FSMContext, db: Database, log: Logger):
    client = await db.get_client_by_phone(message.text)
    if not client:
        log.error(f'Пользователь с данным сотовым "{message.text}" не зарегестрирован в боте')
        await message.answer(f'Пользователь с данным сотовым "{message.text}" не зарегестрирован в боте')
        await state.clear()
        return
    await db.update_client(client.user_id, {'admin': True})
    await get_admin_commands(message.bot)
    await message.answer(
        f"{texts.success_head}"
        f"Пользователь <b>{client.first_name} {client.last_name}</b> добавлен в админ панель"
    )
    log.success(f'Пользователь "{client.first_name} {client.last_name}" "{message.text}" добавлен в админ панель')
    await state.clear()
