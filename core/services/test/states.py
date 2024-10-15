from aiogram.fsm.state import State, StatesGroup


class TestAcceptPhoto(StatesGroup):
    photo = State()