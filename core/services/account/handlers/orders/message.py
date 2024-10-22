from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.services.account.keyboards import inline
from core.loggers.bot_logger import Logger

router = Router()


@router.callback_query(F.data == 'orders')
async def orders(call: CallbackQuery, log: Logger):
    log.button('Заказы')
    text = (
        f'<b>Оформить заказ</b> - Посмотреть наш ассортимент продуктов, и также вы можете оформить свой заказ.\n'
        f'<b>История заказов</b> - Посмотреть историю своих заказов.\n'
        f'<b>Назад⬅️</b> - Вернуться в личный кабинет.'
    )
    await call.message.edit_text(text, reply_markup=inline.kb_orders())
