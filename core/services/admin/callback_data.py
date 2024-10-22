from aiogram.filters.callback_data import CallbackData

from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ClientRolesEnum


class ShopCreateUser(CallbackData, prefix='shop_create_user'):
    shopcode: int


class SelectRole(CallbackData, prefix='select_role'):
    role: ClientRolesEnum


class cbCatalog(CallbackData, prefix='select_catalog'):
    id: int


class CbOpenOrders(CallbackData, prefix='open_orders'):
    order_id: int


class CbCloseOrder(CallbackData, prefix='close_order'):
    order_id: int
    status_id: int
