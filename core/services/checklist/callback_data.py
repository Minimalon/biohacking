from datetime import datetime, date

from aiogram.filters.callback_data import CallbackData

from core.database.enums.checklists import EnumCheckListContentActions


# cl = checklist
class CLMenu(CallbackData, prefix='cl_menu'):
    id: int


class CLContent(CallbackData, prefix='cl_content'):
    id: int
    page: int
    menu_id: int


class CLContentAction(CallbackData, prefix='select_action'):
    action: EnumCheckListContentActions


class CLClient(CallbackData, prefix='cl_client'):
    user_id: int


class CLHistoryDate(CallbackData, prefix='cl_history_date'):
    date_menu: date


class CLHistoryMenu(CallbackData, prefix='cl_history_menu'):
    menu_id: int


class CLDeleteMenu(CallbackData, prefix='cl_delete_menu'):
    menu_id: int
