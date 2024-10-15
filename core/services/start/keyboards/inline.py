from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.services.start.callback_data import Sex


def kb_sex() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Мужчина', callback_data=Sex(sex=0))
    keyboard.button(text='Женщина', callback_data=Sex(sex=1))
    keyboard.adjust(2)
    return keyboard.as_markup()


def kb_start() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Обновить информацию🔄', callback_data='update_start_menu')
    keyboard.adjust(1)
    return keyboard.as_markup()