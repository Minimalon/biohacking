from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database.model import TmcCatalog, HelpTicketStatus, HelpTicket, Clients, OrderStatus, Orders, WorkHelpTicket
from .. import callback_data as cb_data
from ..callback_data import CbCloseHelpTicket
from ...admin.callback_data import cbCatalog
from ...start.callback_data import cbAddProductToCart, cbProduct


def kb_account() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    # keyboard.button(text='Заказы', callback_data='orders')
    keyboard.button(text='Получить подарок!', callback_data='energy_guide')
    keyboard.button(text='Бонусные баллы', callback_data='bonus_card')
    keyboard.button(text='Партнерская программа', callback_data='referals_program')
    keyboard.button(text='Оформить заказ', url='https://bogonaft.com')
    keyboard.button(text='Купить Франшизу!', url='https://bogonaft.com/franchise')
    keyboard.button(text='Информация о нашей команде', url='https://bogonaft.com/team')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_orders() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Оформить заказ🛍️', callback_data='start_shop')
    keyboard.button(text='Текущие заказы🛒', callback_data='current_orders')
    keyboard.button(text='История заказов📜', callback_data='history_orders')
    keyboard.button(text='Назад⬅️', callback_data='account')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_bonus_card() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='История операций📋', callback_data='client_history_assets')
    keyboard.button(text='Обновить информацию🔄', callback_data='update_start_menu')
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_history_assets() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад⬅️', callback_data='bonus_card')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_product_info(product: TmcCatalog) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить в корзину➕', callback_data=cbAddProductToCart(id=product.id))
    keyboard.button(text='Назад⬅️', callback_data=cbCatalog(id=product.catalogid))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_select_product(products: list[TmcCatalog]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.button(text=product.title, callback_data=cbProduct(id=product.id))
    keyboard.button(text='Назад⬅️', callback_data=cbCatalog(id=products[0].catalogid))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_product_to_cart() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить еще товар➕', callback_data='start_shop')
    keyboard.button(text='Создать заказ✅', callback_data='create_order')
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_confirm_need_help() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Подтвердить✅', callback_data='confirm_need_help')
    keyboard.button(text='Отменить❌', callback_data='cancel_need_help')
    keyboard.adjust(1)
    return keyboard.as_markup()

async def kb_create_ticket(ticket_id: int, visible_statuses: list[HelpTicketStatus]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for status in visible_statuses:
        keyboard.button(text=status.name, callback_data=cb_data.CbUpdateTicketStatus(ticket_id=ticket_id, status_id=status.id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_tickets_help() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Открытые заявки📂', callback_data='current_help_tickets')
    keyboard.button(text='История заявок📜', callback_data='history_help_tickets')
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_current_help_tickets(work_tickets: list[WorkHelpTicket], client: Clients) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for ticket in work_tickets:
        ticket_date = ticket.date.strftime('%d.%m.%Y %H:%M')
        keyboard.button(text=f'{ticket_date} {client.first_name}', callback_data=cb_data.CbHelpTicket(ticket_id=ticket.ticket_id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_close_help_ticket(ticket_id: int, status_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Закрыть заявку❌', callback_data=CbCloseHelpTicket(ticket_id=ticket_id, status_id=status_id))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def kb_create_order(order_id: int, visible_statuses: list[OrderStatus]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for status in visible_statuses:
        keyboard.button(text=status.name, callback_data=cb_data.CbCreateOrder(order_id=order_id, status_id=status.id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_current_orders(current_orders: list[Orders]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for order in current_orders:
        order_date = order.date.strftime('%d.%m.%Y %H:%M')
        keyboard.button(text=f'{order_date} | {order.id}', callback_data=cb_data.CbCurrentOrder(order_id=order.id))
    keyboard.button(text='Назад⬅️', callback_data='orders')
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_after_select_current_order() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад⬅️', callback_data='current_orders')
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_energy_guide() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='ПОЛУЧИТЬ!', url='https://docs.yandex.ru/docs/view?url=ya-disk-public%3A%2F%2F3RA%2FyJkTzZzhQMO7iUdyyinjiMbuKlU8lhJLaVLqoHq58QTtyyFWVbPNPv99oA5Zq%2FJ6bpmRyOJonT3VoXnDag%3D%3D%3A%2F%D0%93%D0%B0%D0%B8%CC%86%D0%B4_%D0%AD%D0%9D%D0%95%D0%A0%D0%93%D0%9E%D0%A3%D0%A2%D0%A0%D0%9E.pdf&name=%D0%93%D0%B0%D0%B8%CC%86%D0%B4_%D0%AD%D0%9D%D0%95%D0%A0%D0%93%D0%9E%D0%A3%D0%A2%D0%A0%D0%9E.pdf')
    keyboard.adjust(1)
    return keyboard.as_markup()

