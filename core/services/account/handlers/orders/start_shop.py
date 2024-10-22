from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.catalog_query import CatalogQuery
from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.services.account.callback_data import CbCreateOrder
from core.utils import texts
from core.services.start.callback_data import cbProduct, cbAddProductToCart
from core.services.account.keyboards import inline
from core.services.account.pd_models.catalog import CartItem, Cart
from core.services.start.states import ClientCatalogState
from core.services.admin.callback_data import cbCatalog
from core.services.admin.keyboards.inline import kb_select_catalog

router = Router()
catalog_query = CatalogQuery()


@router.callback_query(F.data == "start_shop")
async def select_catalog(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Каталог')
    catalogs = await catalog_query.get_catalogs()
    if not catalogs:
        await call.message.answer(texts.error_head + "Список каталогов пуст")
        log.error('Список каталогов пуст')
        return
    await call.message.edit_text("Выберите каталог", reply_markup=kb_select_catalog(catalogs))
    await state.set_state(ClientCatalogState.catalog)


@router.callback_query(ClientCatalogState.catalog, cbCatalog.filter())
async def select_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    catalog = await catalog_query.get_catalog(callback_data.id)
    log.info(f"Выбрали каталог {catalog.title}")
    products = await catalog_query.get_tmccatalogs_by_catalogid(catalog.id)
    if not products:
        await call.message.answer(texts.error_head + "Список продуктов пуст")
        await call.answer()
        log.error('Список продуктов пуст')
        return

    await call.message.edit_text(
        "Выберите продукт",
        reply_markup=inline.kb_select_product(products)
    )
    await state.set_state(ClientCatalogState.product)


@router.callback_query(ClientCatalogState.product, cbProduct.filter())
async def after_select_product(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbProduct):
    product = await catalog_query.get_tmccatalog(callback_data.id)
    log.info(f"Выбрали продукт {product.title}")
    if product.file_id:
        await call.message.answer_photo(photo=product.file_id,
                                        caption=await texts.product_info(product),
                                        reply_markup=inline.kb_product_info(product))
    else:
        await call.message.answer(await texts.product_info(product),
                                  reply_markup=inline.kb_product_info(product))
    await call.message.delete()
    await state.set_state(ClientCatalogState.product_info)


@router.callback_query(ClientCatalogState.product_info, cbAddProductToCart.filter())
async def add_product_to_cart(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbAddProductToCart):
    log.button('Добавить в корзину')
    await state.update_data(product_id=callback_data.id)
    await call.message.delete()
    await call.message.answer('Отравьте ответным сообщением <b>КОЛИЧЕСТВО</b> товара')
    await state.set_state(ClientCatalogState.quantity)


@router.callback_query(ClientCatalogState.product_info, cbCatalog.filter())
async def back_to_products(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    log.button('Назад к выбору товаров')
    tmccatalogs = await catalog_query.get_tmccatalogs_by_catalogid(callback_data.id)
    await call.message.answer("Выберите товар",
                              reply_markup=inline.kb_select_product(tmccatalogs)
                              )
    await call.message.delete()
    await state.set_state(ClientCatalogState.product)


@router.callback_query(ClientCatalogState.product, cbCatalog.filter())
async def back_to_catalog(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: cbCatalog):
    log.button('Назад к выбору каталогов')
    catalogs = await catalog_query.get_catalogs()
    await call.message.edit_text("Выберите каталог",
                                 reply_markup=kb_select_catalog(catalogs)
                                 )
    await state.set_state(ClientCatalogState.catalog)


@router.message(ClientCatalogState.quantity)
async def quantity(message: Message, state: FSMContext, log: Logger, db: Database):
    quantity = message.text
    data = await state.get_data()
    if not quantity.isdigit():
        await message.answer(texts.error_head + "Вы ввели не число")
        log.error(f"Количество {quantity} не число")
        return
    log.info(f"Количество {quantity}")
    product_id = data['product_id']
    product = await catalog_query.get_tmccatalog(product_id)
    cartitem = CartItem(
        id=product.id,
        title=product.title,
        code=product.code,
        price=product.price,
        quantity=int(quantity),
        file_id=product.file_id,
        text=product.text,
        catalogid=product.catalogid
    )
    if data.get('cart'):
        cart = Cart.model_validate_json(data['cart'])
        cart.items.append(cartitem)
    else:
        cart = Cart(items=[cartitem])
    await message.answer(await cart.prepare_text(), reply_markup=inline.kb_product_to_cart())
    await state.update_data(cart=cart.model_dump_json())
    await state.set_state(ClientCatalogState.cart)


@router.callback_query(F.data == 'create_order')
async def create_order(call: CallbackQuery, state: FSMContext, log: Logger, db: Database):
    log.button('Создать заказ')
    data = await state.get_data()
    cart = Cart.model_validate_json(data['cart'])
    order = await catalog_query.create_order(user_id=call.from_user.id, cart=cart)
    admins = await db.get_client_by_role(ClientRolesEnum.ADMIN)
    visible_statuses = await catalog_query.get_visible_orders_status()
    for client in admins:
        try:
            await call.message.bot.send_message(
                client.chat_id,
                await cart.compleate_order_text(order.id, client),
                reply_markup=await inline.kb_create_order(
                    order_id=order.id,
                    visible_statuses=visible_statuses,
                )
            )
        except Exception as e:
            log.error(f"Не удалось отправить сообщение клиенту {client.chat_id} {e}")
    await call.message.edit_text(
        texts.success_head + f"<b><u>Заказ успешно создан</u></b>\n{await cart.prepare_text()}")
    log.success(f"Заказ {order.id} создан")
    await state.clear()


@router.callback_query(CbCreateOrder.filter())
async def admin_accept_create_order(call: CallbackQuery, state: FSMContext, log: Logger, db: Database,
                                    callback_data: CbCreateOrder):
    order = await catalog_query.get_order(callback_data.order_id)
    status = await catalog_query.get_order_status(callback_data.status_id)
    history_order = await catalog_query.get_history_order(order.id)

    if history_order is not None:
        if history_order.user_id != call.from_user.id:
            client = await db.get_client(history_order.user_id)
            await call.message.answer(f'Данный заказ уже обрабатывается\n'
                                      f'{await texts.user_info(client)}')
            log.error(f'Данный заказ уже обрабатывается пользователей {client.user_id}')
            return

    await catalog_query.create_history_order(
        order_id=order.id,
        user_id=call.from_user.id,
        status_id=callback_data.status_id,
    )
    await catalog_query.update_order_status(
        order_id=order.id,
        status_id=callback_data.status_id,
    )
    log.info(f'Статус заказа {callback_data.order_id} изменен на {status.name} пользователем {call.from_user.id}')
    await call.message.bot.send_message(
        order.user_id,
        texts.success_head + f'Статус вашего заказа изменён\nСтатус заказа под номером "{callback_data.order_id}" изменен на "{status.name}"'
    )
    await call.message.edit_text(
        texts.success_head + f'Статус заказа под номером "{callback_data.order_id}" изменен на "{status.name}"')
