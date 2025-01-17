from aiogram.fsm.state import State, StatesGroup


class CreateUserState(StatesGroup):
    select_shop = State()
    fio = State()


class SetAdminState(StatesGroup):
    enter_phone = State()
    accept_phone = State()


class CreatePostState(StatesGroup):
    text = State()
    prepared = State()


class CreateCatalogState(StatesGroup):
    name = State()

class AddProductToCatalog(StatesGroup):
    catalog = State()
    bcode = State()
    name = State()
    price = State()
    text = State()
    prepare_commit = State()

class DeleteCatalogState(StatesGroup):
    catalog = State()

class DeleteProductState(StatesGroup):
    catalog = State()
    product = State()

class ChangeProductState(StatesGroup):
    catalog = State()
    product = State()
    price = State()
    code = State()
    description = State()
    title = State()


class SendBonusState(StatesGroup):
    idcard = State()
    award = State()
