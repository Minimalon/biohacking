from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database.model import ChecklistMenu, ChecklistContent
from .. import callback_data as cb_data
from ..pd_models import PDCLContent


def kb_checklist(menus: list[ChecklistMenu]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for menu in menus:
        keyboard.button(text=menu.name, callback_data=cb_data.CLMenu(id=menu.id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_content(pdcontent: PDCLContent) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Готово✅',
                    callback_data=cb_data.CLContent(
                        id=pdcontent.id,
                        menu_id=pdcontent.menu_id,
                        page=pdcontent.page
                    ))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_end_content() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Завершить✅', callback_data='checklist_content_end')
    keyboard.adjust(1)
    return keyboard.as_markup()