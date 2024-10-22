from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from core.database.catalog_query import CatalogQuery
from core.loggers.bot_logger import Logger
from core.services.account.callback_data import CbCurrentOrder
from core.utils import texts
from core.services.account.keyboards import inline

router = Router()
catalog_query = CatalogQuery()

@router.callback_query(F.data == 'current_orders')
async def current_orders(call: CallbackQuery, log: Logger):
    log.button('Текущие заказы')
    cur_orders = await catalog_query.get_current_orders_by_user(call.from_user.id)
    if not cur_orders:
        await call.message.answer(texts.error_head + "Текущих заказов нет")
        log.error('Текущих заказов нет')
        return
    await call.message.edit_text("Список открытых заказов",
                                 reply_markup=inline.kb_current_orders(cur_orders))


@router.callback_query(CbCurrentOrder.filter())
async def select_current_order(call: CallbackQuery, log: Logger, callback_data: CbCurrentOrder):
    order = await catalog_query.get_order(callback_data.order_id)
    log.button(f'Выбрали текущий заказ "{order.id}" "{order.status.name}"')
    order_items = await catalog_query.get_order_items(order.id)
    await call.message.edit_text(await texts.current_user_order(order, order_items),
                                 reply_markup=inline.kb_after_select_current_order())