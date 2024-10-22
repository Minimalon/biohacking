from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.catalog_query import CatalogQuery
from core.loggers.bot_logger import Logger
from core.services.admin.callback_data import cbCatalog
from core.utils import texts
from core.services.admin.keyboards import inline
from core.services.admin.states import CreateCatalogState, DeleteCatalogState

router = Router()
catalog_query = CatalogQuery()


@router.callback_query(F.data == "create_catalog")
async def create_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Создать каталог')
    await call.message.edit_text("Отправьте ответным сообщением <b>НАЗВАНИЕ каталога</b>")
    await state.set_state(CreateCatalogState.name)


@router.message(CreateCatalogState.name)
async def create_catalog_name(message: Message, state: FSMContext, log: Logger):
    log.info(f'Ввели название каталога "{message.text}"')
    await catalog_query.add_catalog(message.text)
    await message.answer(f'{texts.success_head}Каталог "{message.text}" успешно создан',
                         reply_markup=inline.kb_after_create_catalog())
    log.success(f'Каталог "{message.text}" создан')
    await state.clear()


@router.callback_query(F.data == "change_catalog")
async def change_catalog(call: CallbackQuery, log: Logger):
    log.button('Изменить каталог')
    await call.answer(texts.is_develope)


@router.callback_query(F.data == "delete_catalog")
async def delete_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Удалить каталог')
    catalogs = await catalog_query.get_catalogs()
    if not catalogs:
        await call.message.answer(texts.error_head + "Список каталогов пуст")
        log.error('Список каталогов пуст')
        return

    await call.message.edit_text("Выберите каталог", reply_markup=inline.kb_select_catalog(catalogs))
    await state.set_state(DeleteCatalogState.catalog)

@router.callback_query(DeleteCatalogState.catalog, cbCatalog.filter())
async def after_select_catalog_to_delete(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    catalog = await catalog_query.get_catalog(callback_data.id)
    log.info(f'Выбрали каталог "{catalog.title}"')
    log.success(f'Каталог "{catalog.title}" id:{catalog.id} удален')
    await catalog_query.delete_catalog(catalog.id)
    await state.clear()
    await call.message.edit_text(texts.success_head + f'Каталог "{catalog.title}" успешно удален',),

