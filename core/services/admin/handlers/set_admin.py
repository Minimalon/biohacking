from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.commands.commands import set_command_for_user
from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..callback_data import SelectRole
from ..keyboards import inline
from ..states import SetAdminState

router = Router()


@router.callback_query(F.data == 'set_admin')
async def enter_phone(call: CallbackQuery, state: FSMContext, log: Logger, db: Database):
    log.button("Изменить роль пользователя")
    client = await db.get_client(call.from_user.id)
    await call.message.edit_text('Выберите роль пользователя', reply_markup=inline.kb_select_role(client))
    await state.set_state(SetAdminState.enter_phone)


@router.callback_query(SetAdminState.enter_phone, SelectRole.filter())
async def select_role(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: SelectRole):
    log.info(f'Выбрали роль: "{callback_data.role.value}"')
    await state.update_data(new_role=callback_data.role.value)
    await state.set_state(SetAdminState.accept_phone)
    await call.message.edit_text('Введите сотовый номер пользователя\n'
                                 'Например: 79271239999')



@router.message(SetAdminState.accept_phone)
async def set_phone(message: Message, state: FSMContext, db: Database, log: Logger):
    client = await db.get_client_by_phone(message.text)
    data = await state.get_data()
    if not client:
        log.error(f'Пользователь с данным сотовым "{message.text}" не зарегестрирован в боте')
        await message.answer(f'Пользователь с данным сотовым "{message.text}" не зарегестрирован в боте')
        await state.clear()
        return
    role = ClientRolesEnum(data.get('new_role'))
    await db.update_role_client(client.user_id, role)
    await set_command_for_user(message.bot, client.user_id)
    await message.answer(
        f"{texts.success_head}"
        f"Изменили роль пользователя <b>{client.first_name}</b> на <b>{role.value}</b>",
    )
    log.success(f"Изменили роль пользователя {client.user_id} на {role.value}")
    await state.clear()
