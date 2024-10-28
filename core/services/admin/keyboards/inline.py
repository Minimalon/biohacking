from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database.model import ClientRolesEnum, Catalog, Clients, TmcCatalog, Orders, OrderWorks
from core.database.query import Database
from core.services.admin.callback_data import ShopCreateUser, SelectRole, cbCatalog
from core.artix.foreman.pd_model import ForemanCash
from core.services.start.callback_data import cbProduct
from .. import callback_data as cb_data

def kb_admin_panel(client: Clients) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Изменить роль пользователя', callback_data='set_admin')
    keyboard.button(text='Создать пользователя на кассе', callback_data='create_user')
    keyboard.button(text='Аналитика', callback_data='analytics')
    keyboard.button(text='Публикация контента', callback_data='create_post')
    keyboard.button(text='Операции с каталогом', callback_data='operation_catalogs')
    if client.role.rolename in [ClientRolesEnum.SUPERADMIN, ]:
        keyboard.button(text='Управление ботом⚙️', callback_data='bot_settings')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_catalogs_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Операции с каталогами📂', callback_data='operations_with_catalogs')
    keyboard.button(text='Операции с товаром🛒', callback_data='operations_with_products')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_role(client: Clients) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if client.role.rolename == ClientRolesEnum.ADMIN:
        keyboard.button(text=ClientRolesEnum.ADMIN.value, callback_data=SelectRole(role=ClientRolesEnum.ADMIN))
        keyboard.button(text=ClientRolesEnum.CLIENT.value, callback_data=SelectRole(role=ClientRolesEnum.CLIENT))
        keyboard.button(text=ClientRolesEnum.EMPLOYEE.value, callback_data=SelectRole(role=ClientRolesEnum.EMPLOYEE))
        keyboard.button(text=ClientRolesEnum.BLOGER.value, callback_data=SelectRole(role=ClientRolesEnum.BLOGER))
    elif client.role.rolename == ClientRolesEnum.SUPERADMIN:
        for role in ClientRolesEnum:
            keyboard.button(text=role.value, callback_data=SelectRole(role=role))
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


def kb_operations_with_catalogs() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить каталог➕', callback_data='create_catalog')
    keyboard.button(text='Изменить каталог🔄', callback_data='change_catalog')
    keyboard.button(text='Удалить каталог❌', callback_data='delete_catalog')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_after_create_catalog() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить еще➕', callback_data='create_catalog')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_operations_with_products() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить товар➕', callback_data='add_product_to_catalog')
    keyboard.button(text='Изменить товар🔄', callback_data='change_product_to_catalog')
    keyboard.button(text='Удалить товар❌', callback_data='delete_product_to_catalog')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_after_add_product() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить товар➕', callback_data='add_product_to_catalog')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_catalog(catalogs: list[Catalog]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for catalog in catalogs:
        keyboard.button(text=f'{catalog.title}',
                        callback_data=cbCatalog(id=catalog.id))
    keyboard.button(text='Назад⬅️', callback_data='orders')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_prepare_add_product() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Изменить описание товара🔄', callback_data='сhange_text_product')
    keyboard.button(text='Завершить✅', callback_data='confirm_add_product_to_catalog')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_change_product() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Изменить цену', callback_data='сhange_price_product')
    keyboard.button(text='Изменить штрихкод', callback_data='сhange_code_product')
    keyboard.button(text='Изменить описание товара', callback_data='сhange_text_product')
    keyboard.button(text='Изменить название товара', callback_data='сhange_title_product')
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_product(products: list[TmcCatalog]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.button(text=product.title, callback_data=cbProduct(id=product.id))
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_orders_list() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Открытые заказы📂', callback_data='current_work_orders')
    keyboard.button(text='История заказов📜', callback_data='history_work_orders')
    keyboard.adjust(1)
    return keyboard.as_markup()

async def kb_open_orders(orders: list[OrderWorks]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for order in orders:
        db = Database()
        client = await db.get_client(order.user_id)
        ticket_date = order.date.strftime('%d.%m.%Y %H:%M')
        keyboard.button(text=f'{ticket_date} {client.first_name}', callback_data=cb_data.CbOpenOrders(order_id=order.order_id))
    keyboard.adjust(1)
    return keyboard.as_markup()

def kb_close_order(order_id: int, status_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Закрыть заказ❌', callback_data=cb_data.CbCloseOrder(order_id=order_id, status_id=status_id))
    keyboard.adjust(1)
    return keyboard.as_markup()

