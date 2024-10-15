
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.database.checklist_query import CheckListQuery
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..callback_data import CLDeleteMenu
from ..keyboards import inline

router = Router()
cl_query = CheckListQuery()


@router.callback_query(F.data == 'delete_checklist')
async def history_checklist(call: CallbackQuery, log: Logger):
    log.button('Удалить Чек-лист')
    menus = await cl_query.get_all_checklist_menus()

    if len(menus) == 0:
        await call.message.answer('Нет созданных чек-листов')
        log.error('Нет созданных чек-листов')
        return

    await call.message.edit_text('Выберите чек-лист', reply_markup=inline.kb_delete_checklist(menus))


@router.callback_query(CLDeleteMenu.filter())
async def delete_menu(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: CLDeleteMenu):
    menu = await cl_query.get_checklist_menu(callback_data.menu_id)
    await cl_query.delete_checklist_menu(menu.id)
    await call.message.edit_text(f'{texts.success_head}Чек-лист "{menu.name}" удален')
    log.success(f'Удалили чек-лист меню "{menu.name}" id: {menu.id}')
    await state.clear()
