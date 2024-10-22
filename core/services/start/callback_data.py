from aiogram.filters.callback_data import CallbackData

class Sex(CallbackData, prefix='sex'):
    sex: int


class cbProduct(CallbackData, prefix='product'):
    id: int


class cbAddProductToCart(CallbackData, prefix='product_to_cart'):
    id: int
