from aiogram.fsm.state import State, StatesGroup


class CreateChecklist(StatesGroup):
    name = State()
    action = State()
    content = State()


class StatesCheckList(StatesGroup):
    NONE = State()
    GET_PHOTO = State()
    GET_TEXT = State()


class StatesCLHistory(StatesGroup):
    CLIENT = State()
    DATE = State()
    MENU = State()
