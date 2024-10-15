from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def kb_ref_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Создать реферальную ссылку', callback_data='create_ref_link')
    keyboard.adjust(2)
    return keyboard.as_markup()
