from aiogram.filters.callback_data import CallbackData

# cl = checklist
class CLMenu(CallbackData, prefix='cl_menu'):
    id: int

class CLContent(CallbackData, prefix='cl_content'):
    id: int
    page: int
    menu_id: int