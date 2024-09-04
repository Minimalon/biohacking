from aiogram.fsm.state import State, StatesGroup


class CreateUserState(StatesGroup):
    select_shop = State()
    fio = State()


class SetAdminState(StatesGroup):
    phone = State()


class CreatePostState(StatesGroup):
    text = State()
    prepared = State()
