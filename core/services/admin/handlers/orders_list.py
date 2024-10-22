from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.catalog_query import CatalogQuery
from ..callback_data import CbOpenOrders, CbCloseOrder
from ..keyboards import inline, reply
from core.loggers.bot_logger import Logger
from core.utils import texts

router = Router()
catalog_query = CatalogQuery()


@router.message(Command('orders_list'))
async def orders_list(message: Message, log: Logger):
    log.button('/orders_list')
    await message.answer("'Открытые заказы - заказы в работе\n"
                         "История заказы - посмотреть историю закрытых заказов\n",
                         reply_markup=inline.kb_orders_list())


@router.callback_query(F.data == 'current_work_orders')
async def current_work_orders(call: CallbackQuery, log: Logger):
    log.button('Открытые заказы')
    open_orders = await catalog_query.get_open_orders_by_user(call.from_user.id)
    if not open_orders:
        await call.message.answer(texts.error_head + "Открытых заказов нет")
        log.error('Открытых заказов нет')
        return
    await call.message.edit_text("Выберите заказ",
                                 reply_markup=await inline.kb_open_orders(open_orders))


@router.callback_query(CbOpenOrders.filter())
async def select_work_order(call: CallbackQuery, log: Logger, callback_data: CbOpenOrders):
    order = await catalog_query.get_order(callback_data.order_id)
    log.info(f"Выбрали заказ {order.id}")
    client = await catalog_query.get_client(order.user_id)
    close_status = await catalog_query.get_order_closed_status()
    order_items = await catalog_query.get_order_items(order.id)

    await call.message.edit_text(await texts.order_work(order, client, order_items),
                                 reply_markup=inline.kb_close_order(order.id, close_status.id))


@router.callback_query(F.data == 'history_work_orders')
async def history_orders(call: CallbackQuery, log: Logger):
    log.button('История заказов')
    await call.answer(texts.is_develope)


@router.callback_query(CbCloseOrder.filter())
async def close_order(call: CallbackQuery, log: Logger, callback_data: CbCloseOrder):
    log.button('Закрыть заказ')
    await catalog_query.update_order_status(callback_data.order_id, callback_data.status_id)
    await call.message.edit_text(texts.success_head + f"Заказ под номером '{callback_data.order_id}' успешно закрыт")
    log.success(f"Заказ под номером '{callback_data.order_id}' успешно закрыт")
