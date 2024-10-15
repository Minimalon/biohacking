from aiogram.filters.callback_data import CallbackData

from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ClientRolesEnum


class ShopCreateUser(CallbackData, prefix='shop_create_user'):
    shopcode: int


class SelectRole(CallbackData, prefix='select_role'):
    role: ClientRolesEnum


if __name__ == '__main__':
    for c in ClientRolesEnum:
        print(c.value)

