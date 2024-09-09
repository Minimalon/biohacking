from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import config
from core.database.query import Database
from core.loggers.bot_logger import Logger
from ..callback_data import CLMenu, CLContent
from ..keyboards import inline
from core.utils import texts
from ..pd_models import PDCLContent

router = Router()


@router.message(Command("checklist"))
async def start(message: Message, state: FSMContext, log: Logger, db: Database):
    log.button('/checklist')
    await state.clear()
    if config.bot_cfg.develope_mode:
        await message.answer(texts.is_develope)
        return
    menus = await db.get_checklist_menus()
    if not menus:
        await message.answer(f"{texts.error_head}"
                             f"Нет созданных меню\n"
                             f"Обратитесь к Администратору для создания меню" )
        log.error(f"Нет созданных меню")
        return
    await message.answer("Выберите нужную операцию",
                         reply_markup=inline.kb_checklist(menus))


@router.callback_query(CLMenu.filter())
async def checklist_menu(call: CallbackQuery, state: FSMContext, log: Logger, db: Database, callback_data: CLMenu):
    menu = await db.get_checklist_menu(callback_data.id)
    log.info(f'Выбрали чек-лист меню "{menu.name}"')
    clcontent = await db.next_page_checlist_content(menu.id)
    if not clcontent:
        await call.message.answer(f"{texts.error_head}"
                                  f"Нет созданных чек-листов\n"
                                  f"Обратитесь к Администратору для создания чек-листа" )
        log.error(f"Нет созданных чек-листов")
        return
    pdclcontent = PDCLContent(
        id=clcontent.id,
        menu_id=menu.id,
        page=clcontent.page,
    )
    await state.update_data(pdclcontent=pdclcontent.model_dump_json())
    nextclcontent = await db.next_page_checlist_content(pdclcontent.menu_id, pdclcontent.page + 1)
    if nextclcontent is None:
        await call.message.edit_text(clcontent.content, reply_markup=inline.kb_end_content())
    else:
        await call.message.edit_text(clcontent.content, reply_markup=inline.kb_content(pdclcontent))

@router.callback_query(CLContent.filter())
async def checklist_content(call: CallbackQuery, state: FSMContext, log: Logger, db: Database, callback_data: CLContent):
    data = await state.get_data()
    pdclcontent = PDCLContent.model_validate_json(data['pdclcontent'])
    log.info(f'Выбрали чек-лист "{callback_data.id}" страница {callback_data.page} из меню {callback_data.menu_id}')
    pdclcontent.page += 1
    clcontent = await db.next_page_checlist_content(pdclcontent.menu_id, pdclcontent.page)
    await state.update_data(pdclcontent=pdclcontent.model_dump_json())
    nextclcontent = await db.next_page_checlist_content(pdclcontent.menu_id, pdclcontent.page + 1)
    if nextclcontent is None:
        await call.message.edit_text(clcontent.content, reply_markup=inline.kb_end_content())
    else:
        await call.message.edit_text(clcontent.content, reply_markup=inline.kb_content(pdclcontent))

@router.callback_query(F.data == 'checklist_content_end')
async def checklist_content_end(call: CallbackQuery, state: FSMContext, log: Logger, db: Database):
    data = await state.get_data()
    pdclcontent = PDCLContent.model_validate_json(data['pdclcontent'])
    log.success(f'Завершили чек-лист "{pdclcontent.id}" страница {pdclcontent.page} из меню {pdclcontent.menu_id}')
    await state.clear()

