from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def kb_registration():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Регистрация', request_contact=True)
    keyboard.adjust(1)
    return keyboard.as_markup(one_time_keyboard=True)
