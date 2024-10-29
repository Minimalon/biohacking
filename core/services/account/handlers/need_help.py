from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from core.artix.CS.cs import CS
from core.database.helpticket_query import HelpTicketQuery
from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.utils.qr import generate_qr
from ..callback_data import CbUpdateTicketStatus, CbHelpTicket, CbCloseHelpTicket
from ..keyboards import inline, reply
from core.loggers.bot_logger import Logger
from core.utils import texts
from ...start.pd_models.profile_bonuses import Profile

router = Router()

help_query = HelpTicketQuery()


@router.callback_query(F.data == 'need_help')
async def need_help(call: CallbackQuery, log: Logger):
    log.button('Мне нужна помощь')
    text = 'Нажмите кнопку "Подтвердить✅", и наш оператор перезвонит вам в ближайшее время.'
    await call.message.edit_text(text, reply_markup=inline.kb_confirm_need_help())


@router.callback_query(F.data == 'cancel_need_help')
async def cancel_need_help(call: CallbackQuery, log: Logger):
    log.button('Отменить помощь')
    fullname = f'{call.from_user.first_name} {call.from_user.last_name}' if call.from_user.last_name is not None else call.from_user.first_name
    await call.message.edit_text(await texts.account(fullname),
                                 reply_markup=inline.kb_account())


@router.callback_query(F.data == 'confirm_need_help')
async def confirm_need_help(call: CallbackQuery, log: Logger, db: Database, state: FSMContext):
    log.button('Подтвердил помощь')
    ticket = await help_query.create_ticket(call.from_user.id)
    admins = await db.get_client_by_role(ClientRolesEnum.ADMIN)
    client = await db.get_client(call.from_user.id)
    visible_statuses = await help_query.get_visible_statuses()

    for admin in admins:
        text = (
            f'<b>Запросили помощь</b>\n'
            f'Номер запроса: <code>{ticket.id}</code>\n'
            f'{await texts.user_info(client)}\n\n'
            f'<blockquote>Чтобы поменять статус запроса, нажмите на кнопку ниже.</blockquote>')
        try:
            await call.message.bot.send_message(
                admin.user_id,
                text,
                reply_markup=await inline.kb_create_ticket(ticket.id, visible_statuses)
            )
        except Exception as e:
            log.error(f"Не удалось отправить сообщение клиенту {client.chat_id} {e}")
    await call.message.edit_text(texts.success_head + "Вам в ближайшее время перезвонят")


@router.callback_query(CbUpdateTicketStatus.filter())
async def update_ticket_status(call: CallbackQuery, log: Logger, callback_data: CbUpdateTicketStatus, db: Database):
    status = await help_query.get_status(callback_data.status_id)
    history_ticket = await help_query.get_history_ticket(callback_data.ticket_id)
    if history_ticket is not None:
        if history_ticket.user_id != call.from_user.id:
            client = await db.get_client(history_ticket.user_id)
            await call.message.answer(f'Данная заявка уже обрабатывается\n'
                                      f'{await texts.user_info(client)}')
            log.error(f'Данная заявка уже обрабатывается пользователей {client.user_id}')
            return
    await help_query.create_history_ticket(
        ticket_id=callback_data.ticket_id,
        user_id=call.from_user.id,
        status_id=status.id,
    )
    await help_query.update_ticket_status(
        ticket_id=callback_data.ticket_id,
        status_id=status.id,
    )
    log.info(f'Статус заявки {callback_data.ticket_id} изменен на {status.name} пользователем {call.from_user.id}')
    await call.message.edit_text(texts.success_head + f'Статус заявки под номером "{callback_data.ticket_id}" изменен на "{status.name}"')


@router.callback_query(F.data == 'history_help_tickets')
async def history_help_tickets(call: CallbackQuery, log: Logger, db: Database):
    log.button('История запросов')
    await call.answer(texts.is_develope)


@router.callback_query(F.data == 'current_help_tickets')
async def current_help_tickets(call: CallbackQuery, log: Logger, db: Database):
    log.button('Открытые заявки')
    work_tickets = await help_query.get_tickets_not_closed_by_user(call.from_user.id)
    client = await db.get_client(call.from_user.id)
    if work_tickets:
        await call.message.edit_text('Выберите заявку',
                                     reply_markup=inline.kb_current_help_tickets(work_tickets, client))
    else:
        await call.message.edit_text(texts.intersum_head + 'Нет открытых заявок')


@router.callback_query(CbHelpTicket.filter())
async def current_help_ticket(call: CallbackQuery, log: Logger, callback_data: CbHelpTicket, db: Database):
    ticket = await help_query.get_ticket(callback_data.ticket_id)
    client = await db.get_client(ticket.user_id)
    close_status = await help_query.get_close_status()
    log.info(f'Открыта заявка под номером {ticket.id} пользователем {call.from_user.id}')
    await call.message.edit_text(await texts.help_ticket_help(ticket, client),
                                 reply_markup=inline.kb_close_help_ticket(
                                     ticket_id=ticket.id,
                                     status_id=close_status.id
                                 ))


@router.callback_query(CbCloseHelpTicket.filter())
async def close_help_ticket(call: CallbackQuery, log: Logger, callback_data: CbCloseHelpTicket, db: Database):
    log.button('Закрыть заявку')
    await help_query.update_ticket_status(
        ticket_id=callback_data.ticket_id,
        status_id=callback_data.status_id,
    )
    await call.message.edit_text(texts.success_head + f"Заявка под номером '{callback_data.ticket_id}' закрыта")
    await log.success(f'Заявка под номером {callback_data.ticket_id} закрыта')
