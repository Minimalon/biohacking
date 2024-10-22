from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..keyboards import inline, reply

router = Router()


@router.message(Command("admin"))
async def admin(message: Message, state: FSMContext, log: Logger, db: Database):
    log.button("/admin")
    client = await db.get_client(message.from_user.id)
    log.debug(client.role.rolename)
    if not client.role.rolename in [ClientRolesEnum.ADMIN, ClientRolesEnum.SUPERADMIN]:
        await message.answer(texts.no_access)
        log.error('Пользователь не является админом')
        return
    await message.answer("Админ панель", reply_markup=inline.kb_admin_panel(client))


@router.callback_query(F.data == 'operation_catalogs')
async def operation_catalogs(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Операции с каталогом')
    await call.message.edit_text("Выберите действие", reply_markup=inline.kb_catalogs_panel())


@router.callback_query(F.data == "operations_with_catalogs")
async def operations_with_catalogs(call: CallbackQuery, log: Logger):
    log.button("Операции с каталогами")
    await call.message.edit_text("Выберите операцию", reply_markup=inline.kb_operations_with_catalogs())


@router.callback_query(F.data == "operations_with_products")
async def operations_with_products(call: CallbackQuery, log: Logger):
    log.button("Операции с товарами")
    await call.message.edit_text("Выберите операцию", reply_markup=inline.kb_operations_with_products())
