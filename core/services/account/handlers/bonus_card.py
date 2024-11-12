from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from core.artix.CS.cs import CS
from core.utils.qr import generate_qr
from ..keyboards import inline, reply
from core.loggers.bot_logger import Logger
from core.utils import texts
from ...start.pd_models.profile_bonuses import Profile
from ...start.states import RegistrationStates

router = Router()


@router.callback_query(F.data == 'bonus_card')
async def bonus_card(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Бонусная карта')
    cs = CS()

    cs_client = await cs.get_client_by_id(call.from_user.id)
    cs_client_card = await cs.get_card_by_id(call.from_user.id)
    cs_card_balance = await cs.get_card_balance(call.from_user.id)

    if not cs_client or not cs_client_card or not cs_card_balance:
        await state.set_state(RegistrationStates.birthday)
        await call.message.edit_text('Введите день рождения\nПример: 01.01.1990')
        return

    profile = Profile(
        cs_client=cs_client,
        cs_card=cs_client_card,
        cs_card_balance=cs_card_balance
    )
    await call.message.bot.send_photo(
        call.message.chat.id,
        photo=FSInputFile(await generate_qr(call.from_user.id)),
        caption=await texts.profile(profile),
        reply_markup=inline.kb_bonus_card()
    )
    await call.answer()
