from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def kb_checklist() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Открытие смены', callback_data='openshift_checklist')
    keyboard.button(text='Закртытие смены', callback_data='closeshift_checklist')
    keyboard.adjust(1)
    return keyboard.as_markup()
