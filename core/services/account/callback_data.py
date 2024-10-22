from aiogram.filters.callback_data import CallbackData


class CbUpdateTicketStatus(CallbackData, prefix='update_ticket_status'):
    ticket_id: int
    status_id: int


class CbHelpTicket(CallbackData, prefix='help_ticket'):
    ticket_id: int


class CbCloseHelpTicket(CallbackData, prefix='close_help_ticket'):
    ticket_id: int
    status_id: int

class CbCreateOrder(CallbackData, prefix='create_order'):
    order_id: int
    status_id: int

class CbCurrentOrder(CallbackData, prefix='current_user_order'):
    order_id: int
