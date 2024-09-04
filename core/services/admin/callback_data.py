from aiogram.filters.callback_data import CallbackData

class ShopCreateUser(CallbackData, prefix='shop_create_user'):
    shopcode: int