from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.catalog_query import CatalogQuery
from core.database.model import TmcCatalog
from core.loggers.bot_logger import Logger
from core.services.admin.callback_data import cbCatalog
from core.services.start.callback_data import cbProduct
from core.utils import texts
from core.services.admin.keyboards import inline
from core.services.admin.states import AddProductToCatalog, DeleteProductState, ChangeProductState

router = Router()
catalog_query = CatalogQuery()


async def product_info_for_change(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(ChangeProductState.product)
    product = await catalog_query.get_tmccatalog(data['change_product_id'])
    if product.file_id is not None:
        await message.answer_photo(product.file_id,
                                   caption=await texts.product_info(product),
                                   reply_markup=inline.kb_change_product())
    else:
        await message.answer(await texts.product_info(product),
                             reply_markup=inline.kb_change_product())


@router.callback_query(F.data == "add_product_to_catalog")
async def select_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Добавить товар в каталог')
    catalogs = await catalog_query.get_catalogs()
    if not catalogs:
        await call.message.answer(texts.error_head + "Список каталогов пуст")
        log.error('Список каталогов пуст')
        return

    await call.message.edit_text("Выберите каталог", reply_markup=inline.kb_select_catalog(catalogs))
    await state.set_state(AddProductToCatalog.catalog)


@router.callback_query(AddProductToCatalog.catalog, cbCatalog.filter())
async def after_select_catalog(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    catalog = await catalog_query.get_catalog(callback_data.id)
    log.info(f'Выбрали каталог "{catalog.title}"')
    if catalog.parent_id is not None:
        catalogs_by_parent = await catalog_query.get_catalog_by_parent_id(catalog.parent_id)
        await call.message.edit_text("Выберите каталог", reply_markup=inline.kb_select_catalog(catalogs_by_parent))
        await state.set_state(AddProductToCatalog.catalog)
        return
    await state.update_data(addproduct_catalog_id=catalog.id)
    await call.message.edit_text("Отправьте ответным сообщением <b>ШТРИХКОД</b> товара\n"
                                 "Например: 4604661017399")
    await state.set_state(AddProductToCatalog.bcode)


@router.message(AddProductToCatalog.bcode)
async def enter_bcode(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    log.info(f'Написали штрихкод товара "{message.text}"')
    if not message.text.isdigit():
        await message.answer(texts.error_head + "Неправильно введен штрихкод")
        log.error(f'Неправильно введен штрихкод "{message.text}"')
        return
    if message.text in [str(tmccatalog.code)
                        for tmccatalog in
                        await catalog_query.get_tmccatalogs_by_catalogid(data['addproduct_catalog_id'])]:
        await message.answer(texts.error_head + "Такой штрихкод уже существует в выбранном каталоге")
        log.error(f'Такой штрихкод уже существует "{message.text}" в выбранном каталоге')
        return
    await state.update_data(addproduct_bcode=message.text)
    await message.answer("Отправьте ответным сообщением <b>НАЗВАНИЕ</b> товара\n"
                         "Например: <code>Омега-3 100 капсул 1000 мг</code>")
    await state.set_state(AddProductToCatalog.name)


@router.message(AddProductToCatalog.name)
async def enter_name(message: Message, state: FSMContext, log: Logger):
    log.info(f'Написали название товара "{message.text}"')

    await state.update_data(addproduct_name=message.text)
    await message.answer("Отправьте ответным сообщением <b>ЦЕНУ</b> товара\n"
                         "Например: 1000")
    await state.set_state(AddProductToCatalog.price)


@router.message(AddProductToCatalog.price)
async def enter_price(message: Message, state: FSMContext, log: Logger):
    log.info(f'Написали цену товара "{message.text}"')
    if not message.text.isdigit():
        await message.answer(texts.error_head + "Неправильно введена цена")
        log.error(f'Неправильно введена цена "{message.text}"')
        return
    await state.update_data(addproduct_price=message.text)
    await message.answer("Отправьте ответным сообщением <b>ОПИСАНИЕ</b> товара, также можно приложить 1 фото")
    await state.set_state(AddProductToCatalog.text)


@router.message(F.content_type.in_([ContentType.PHOTO, ContentType.TEXT]), AddProductToCatalog.text)
async def enter_text(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    if message.photo is not None:
        file_id = message.photo[-1].file_id
        text = message.caption
    elif message.document is not None:
        file_id = message.document.file_id
        text = message.caption
    else:
        file_id = None
        text = message.text

    if text is not None:
        if len(text) > 824:
            await message.answer(texts.error_head + "Слишком длинное описанние товара\n"
                                                    "Отправьте ответным сообщением ОПИСАНИЕ товара, также можно приложить 1 фото")
            log.error(f'Слишком длинное название "{message.text}"')
            return

    log.info(f'Напечатал содержимое продукта "{text}"')
    log.info(f'Прислал фото продукта "{file_id}"')
    await state.update_data(addproduct_text=text, addproduct_file_id=file_id)
    tmc = TmcCatalog(
        title=data['addproduct_name'],
        code=data['addproduct_bcode'],
        price=data['addproduct_price'],
        text=text,
        file_id=file_id,
        catalogid=data['addproduct_catalog_id']
    )
    if tmc.file_id is not None:
        await message.answer_photo(photo=tmc.file_id,
                                   caption=await texts.product_info(tmc),
                                   reply_markup=inline.kb_prepare_add_product())
    else:
        await message.answer(await texts.product_info(tmc),
                             reply_markup=inline.kb_prepare_add_product())

@router.callback_query(F.data == "сhange_text_product")
async def update_text(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить описание товара')
    await call.message.delete()
    await call.message.answer("Отправьте ответным сообщением <b>ОПИСАНИЕ</b> товара, также можно приложить 1 фото")
    await state.set_state(AddProductToCatalog.text)


@router.callback_query(F.data == "confirm_add_product_to_catalog")
async def confirm_add_product_to_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Подтвердить добавление продукта в каталог')
    data = await state.get_data()
    catalog_id = int(data.get('addproduct_catalog_id'))
    bcode = int(data.get('addproduct_bcode'))
    name = data.get('addproduct_name')
    price = float(data.get('addproduct_price'))
    text = data.get('addproduct_text')
    file_id = data.get('addproduct_file_id')
    tmccatalog = await catalog_query.add_tmccatalog(
        code=bcode,
        name=name,
        file_id=file_id,
        text=text,
        price=price,
        catalogid=catalog_id
    )
    catalog = await catalog_query.get_catalog(catalog_id)
    await call.message.delete()
    await call.message.answer(
        texts.success_head + f"Товар '{tmccatalog.code}' успешно добавлен в каталог '{catalog.title}'",
        reply_markup=inline.kb_operations_with_products())
    await state.clear()


@router.callback_query(F.data == "change_product_to_catalog")
async def change_product_to_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить товар')
    catalogs = await catalog_query.get_catalogs()
    if not catalogs:
        await call.message.answer(texts.error_head + "Список каталогов пуст")
        log.error('Список каталогов пуст')
        return

    await call.message.edit_text("Выберите каталог", reply_markup=inline.kb_select_catalog(catalogs))
    await state.set_state(ChangeProductState.catalog)


@router.callback_query(ChangeProductState.catalog, cbCatalog.filter())
async def change_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    catalog = await catalog_query.get_catalog(callback_data.id)
    log.info(f"Выбрали каталог {catalog.title}")
    products = await catalog_query.get_tmccatalogs_by_catalogid(catalog.id)
    await call.message.edit_text(
        "Выберите продукт",
        reply_markup=inline.kb_select_product(products)
    )
    await state.set_state(ChangeProductState.product)


@router.callback_query(ChangeProductState.product, cbProduct.filter())
async def after_select_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbProduct):
    product = await catalog_query.get_tmccatalog(callback_data.id)
    log.info(f"Выбрали продукт {product.code}")
    await call.message.delete()
    if product.file_id is not None:
        await call.message.answer_photo(product.file_id,
                                        caption=await texts.product_info(product),
                                        reply_markup=inline.kb_change_product())
    else:
        await call.message.answer(await texts.product_info(product),
                                  reply_markup=inline.kb_change_product())
    await state.update_data(change_product_id=product.id)


@router.callback_query(F.data == "сhange_price_product")
async def update_price(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить цену')
    await call.message.delete()
    await call.message.answer("Отправьте ответным сообщением <b>ЦЕНУ</b> товара")
    await state.set_state(ChangeProductState.price)


@router.message(ChangeProductState.price)
async def accept_update_price(message: Message, state: FSMContext, log: Logger):
    log.info(f"Изменяем цену на {message.text}")
    if not message.text.isdigit():
        await message.answer(texts.error_head + "Цена должна быть числом")
        log.error('Цена должна быть числом')
        return
    data = await state.get_data()
    product_id = data.get('change_product_id')
    await catalog_query.update_tmccatalog_price(product_id, float(message.text))
    await product_info_for_change(message, state)


@router.callback_query(F.data == "сhange_code_product")
async def update_code(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить штрихкод')
    await call.message.delete()
    await call.message.answer("Отправьте ответным сообщением <b>ШТРИХКОД</b> товара")
    await state.set_state(ChangeProductState.code)


@router.message(ChangeProductState.code)
async def accept_update_code(message: Message, state: FSMContext, log: Logger):
    log.info(f"Изменяем штрихкод на {message.text}")
    if not message.text.isdigit():
        await message.answer(texts.error_head + "Штрихкод должен быть числом")
        log.error('Штрихкод должен быть числом')
        return
    data = await state.get_data()
    product_id = data.get('change_product_id')
    await catalog_query.update_tmccatalog_code(product_id, int(message.text))
    await product_info_for_change(message, state)


@router.callback_query(F.data == "сhange_text_product")
async def change_product_update_text(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить описание товара')
    await call.message.delete()
    await call.message.answer("Отправьте ответным сообщением <b>ОПИСАНИЕ</b> товара")
    await state.set_state(ChangeProductState.description)


@router.message(F.content_type.in_([ContentType.PHOTO, ContentType.TEXT]), ChangeProductState.description)
async def accept_update_text(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    if message.photo is not None:
        file_id = message.photo[-1].file_id
        text = message.caption
    elif message.document is not None:
        file_id = message.document.file_id
        text = message.caption
    else:
        file_id = None
        text = message.text
    log.info(f'Напечатал содержимое продукта "{text}"')
    log.info(f'Прислал фото продукта "{file_id}"')
    product_id = data.get('change_product_id')
    await catalog_query.update_tmccatalog_text_and_fileid(product_id, text, file_id)
    await product_info_for_change(message, state)


@router.callback_query(F.data == "сhange_title_product")
async def update_title(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить название товара')
    await call.message.delete()
    await call.message.answer("Отправьте ответным сообщением <b>НАЗВАНИЕ</b> товара")
    await state.set_state(ChangeProductState.title)


@router.message(ChangeProductState.title)
async def accept_update_title(message: Message, state: FSMContext, log: Logger):
    log.info(f"Изменяем название на {message.text}")
    data = await state.get_data()
    product_id = data.get('change_product_id')
    await catalog_query.update_tmccatalog_title(product_id, message.text)
    await product_info_for_change(message, state)


@router.callback_query(F.data == "delete_product_to_catalog")
async def delete_product_to_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Удалить товар')
    catalogs = await catalog_query.get_catalogs()
    if not catalogs:
        await call.message.answer(texts.error_head + "Список каталогов пуст")
        log.error('Список каталогов пуст')
        return

    await call.message.edit_text("Выберите каталог", reply_markup=inline.kb_select_catalog(catalogs))
    await state.set_state(DeleteProductState.catalog)


@router.callback_query(DeleteProductState.catalog, cbCatalog.filter())
async def delete_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    catalog = await catalog_query.get_catalog(callback_data.id)
    log.info(f"Выбрали каталог {catalog.title}")
    products = await catalog_query.get_tmccatalogs_by_catalogid(catalog.id)
    await call.message.edit_text(
        "Выберите продукт",
        reply_markup=inline.kb_select_product(products)
    )
    await state.set_state(DeleteProductState.product)


@router.callback_query(DeleteProductState.product, cbProduct.filter())
async def accept_delete_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbProduct):
    product = await catalog_query.get_tmccatalog(callback_data.id)
    log.info(f"Выбрали продукт {product.title}")
    await catalog_query.delete_tmccatalog(product.id)
    await call.message.edit_text(
        texts.success_head + f"Товар '{product.code}' успешно удален",
        reply_markup=inline.kb_operations_with_products()
    )
    log.success(f"Товар '{product.code}' id:{product.id} успешно удален")
    await state.clear()
