from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.services.admin.callback_data import ShopCreateUser
from core.artix.foreman.pd_model import ForemanCash


def kb_admin_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Дать права админа в боте', callback_data='set_admin')
    keyboard.button(text='Создать пользователя на кассе', callback_data='create_user')
    keyboard.button(text='Аналитика', callback_data='analytics')
    keyboard.button(text='Публикация контента', callback_data='create_post')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_shop(cashes: list[ForemanCash]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for cash in cashes:
        keyboard.button(text=f'{cash.shopcode}',
                        callback_data=ShopCreateUser(shopcode=cash.shopcode))
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_send_post() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Отправить рассылку✅', callback_data='send_post')
    keyboard.button(text='Переделать🔄', callback_data='create_post')
    keyboard.adjust(1)
    return keyboard.as_markup()