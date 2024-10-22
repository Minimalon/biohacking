from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    birthday = State()
    wait_name = State()
    name = State()
    sex = State()


class ClientCatalogState(StatesGroup):
    catalog = State()
    product = State()
    product_info = State()
    quantity = State()
    cart = State()

