from aiogram.fsm.state import State, StatesGroup


class GPTDialogState(StatesGroup):
    wait_answer = State()