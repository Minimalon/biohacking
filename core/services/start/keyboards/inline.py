from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.services.start.callback_data import Sex


def kb_name() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Завершить регистрацию➡️', callback_data='complete_registration')
    keyboard.button(text='Ввести имя самому', callback_data='registration_name')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_sex() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Мужчина', callback_data=Sex(sex=0))
    keyboard.button(text='Женщина', callback_data=Sex(sex=1))
    keyboard.adjust(2)
    return keyboard.as_markup()


def kb_start() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='История операций📋', callback_data='client_history_assets')
    keyboard.button(text='Обновить информацию🔄', callback_data='update_start_menu')
    keyboard.adjust(1)
    return keyboard.as_markup()
