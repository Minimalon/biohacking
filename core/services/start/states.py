from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    birthday = State()
    name = State()
    sex = State()

