from datetime import datetime, date

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ChecklistMenu, ChecklistContent, Clients
from .. import callback_data as cb_data
from core.services.checklist.pd_models.pd_start import PDCLContent


def kb_checklist(menus: list[ChecklistMenu]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for menu in menus:
        keyboard.button(text=menu.name, callback_data=cb_data.CLMenu(id=menu.id))
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_content(clcontent: ChecklistContent) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Готово✅',
                    callback_data=cb_data.CLContent(
                        id=clcontent.id,
                        menu_id=clcontent.checklistmenuid,
                        page=clcontent.page
                    ))
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_end_content() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Завершить✅', callback_data='checklist_content_end')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_admins_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Список Чек-листов📋', callback_data='list_checklists')
    keyboard.button(text='Добавить Чек-лист➕', callback_data='new_checklist')
    keyboard.button(text='Удалить Чек-лист❌', callback_data='delete_checklist')
    keyboard.button(text='История выполнений📜', callback_data='history_checklist')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_after_create_checklist() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Список Чек-листов📋', callback_data='list_checklists')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_actions() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for action in EnumCheckListContentActions:
        if action == EnumCheckListContentActions.NONE:
            keyboard.button(text='Ничего не запрашивать', callback_data=cb_data.CLContentAction(action=action.value))
        elif action == EnumCheckListContentActions.GET_PHOTO:
            keyboard.button(text='Запросить фото', callback_data=cb_data.CLContentAction(action=action.value))
        elif action == EnumCheckListContentActions.GET_TEXT:
            keyboard.button(text='Запросить текстовое сообщение',
                            callback_data=cb_data.CLContentAction(action=action.value))
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_confirm_new_content() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Изменить🔄', callback_data='сhange_new_content')
    keyboard.button(text='Следующая страница➡️', callback_data='next_new_content')
    keyboard.button(text='Завершить✅', callback_data='confirm_new_content')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_history_clients(clients: list[Clients]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for client in clients:
        keyboard.button(text=f'{client.first_name} {client.phone_number}',
                        callback_data=cb_data.CLClient(user_id=client.user_id))
    keyboard.adjust(1)
    return keyboard.as_markup()
def kb_history_dates(dates: list[datetime]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for date_menu in dates:
        DATE = date(year=date_menu.year, month=date_menu.month, day=date_menu.day)
        keyboard.button(text=str(DATE),
                        callback_data=cb_data.CLHistoryDate(date_menu=DATE))
    keyboard.adjust(1)
    return keyboard.as_markup()
def kb_history_menus(menus: list[ChecklistMenu]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for menu in menus:
        keyboard.button(text=menu.name,
                        callback_data=cb_data.CLHistoryMenu(menu_id=menu.id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_delete_checklist(menus: list[ChecklistMenu]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for menu in menus:
        keyboard.button(text=menu.name,
                        callback_data=cb_data.CLDeleteMenu(menu_id=menu.id))
    keyboard.adjust(1)
    return keyboard.as_markup()