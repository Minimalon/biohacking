from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import  CallbackQuery

from core.database.checklist_query import CheckListQuery
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils.texts import history_complete_question, history_complete_answer
from ..callback_data import CLClient, CLHistoryDate, CLHistoryMenu
from ..keyboards import inline
from ..states import StatesCLHistory

router = Router()
cl_query = CheckListQuery()


@router.callback_query(F.data == 'history_checklist')
async def history_checklist(call: CallbackQuery, state: FSMContext, db: Database, log: Logger):
    log.button('История выполнений')
    unique_users = await cl_query.get_unique_user_checklist_complete()

    if len(unique_users) == 0:
        await call.message.answer('Ни один пользователь не прошел чек-лист')
        log.error('Ни один пользователь не прошел чек-лист')
        return

    clients = await db.get_clients(unique_users)
    await call.message.edit_text('Выберите пользователя', reply_markup=inline.kb_history_clients(clients))
    await state.set_state(StatesCLHistory.CLIENT)


@router.callback_query(CLClient.filter(), StatesCLHistory.CLIENT)
async def select_client(call: CallbackQuery, state: FSMContext, db: Database, log: Logger, callback_data: CLClient):
    client = await db.get_client(callback_data.user_id)
    log.info(f'Выбрали пользователя {client.first_name} {client.user_id}')
    await state.update_data(history_client_id=client.user_id)
    await state.set_state(StatesCLHistory.DATE)
    dates = await cl_query.get_unique_dates_checklist_complete(client.user_id)
    await call.message.edit_text(f'Выберите дату', reply_markup=inline.kb_history_dates(dates))


@router.callback_query(CLHistoryDate.filter(), StatesCLHistory.DATE)
async def select_date(call: CallbackQuery, state: FSMContext, db: Database, log: Logger, callback_data: CLHistoryDate):
    log.info(f'Выбрали дату {callback_data.date_menu}')
    data = await state.get_data()
    client = await db.get_client(data.get('history_client_id'))
    unique_menu_ids = await cl_query.get_unique_menus_by_user(client.user_id, callback_data.date_menu)
    menus = await cl_query.get_checklist_menus(unique_menu_ids)
    await state.update_data(history_date=str(callback_data.date_menu))
    await call.message.edit_text(f'Выберите Чек-лист', reply_markup=inline.kb_history_menus(menus))
    await state.set_state(StatesCLHistory.MENU)


@router.callback_query(CLHistoryMenu.filter(), StatesCLHistory.MENU)
async def select_menu(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: CLHistoryMenu):
    log.info(f'Выбрали меню {callback_data.menu_id}')
    data = await state.get_data()
    history_date, user_id = date.fromisoformat(data.get('history_date')), data.get('history_client_id')
    checklists= await cl_query.get_completes(
        user_id=user_id,
        date_menu=history_date,
        menu_id=callback_data.menu_id
    )
    for cl in checklists:
        question_content = await cl_query.get_checklist_content(cl.checklistcontentid)
        if question_content.file_id is not None:
            await call.message.bot.send_photo(
                call.message.chat.id,
                question_content.file_id,
                caption=await history_complete_question(question_content)
            )
        else:
            await call.message.answer(await history_complete_question(question_content))

        if cl.file_id is not None:
            await call.message.bot.send_photo(
                call.message.chat.id,
                cl.file_id,
                caption=await history_complete_answer(cl, question_content)
            )
        else:
            await call.message.answer(await history_complete_answer(cl, question_content))
