from datetime import datetime, timedelta, date
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, CallbackQuery, FSInputFile
from aiogram.utils.deep_linking import create_start_link

import config
from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.database.referal_query import ReferralQuery
from core.loggers.bot_logger import Logger
from core.utils import texts
from core.utils.qr import generate_qr, get_buffer_qr
from ..keyboards import inline

router = Router()


@router.message(Command('ref'))
async def ref_menu(message: Message, log: Logger):
    log.button('/ref')
    ref_db = ReferralQuery()
    date_current = datetime.now()
    date_now = datetime(date_current.year, date_current.month, date_current.day)
    refs_today = await ref_db.get_user_refs_by_date(date_now + timedelta(days=1), date_now - timedelta(days=0), message.from_user.id)
    refs_tomorrow = await ref_db.get_user_refs_by_date(date_now, date_now - timedelta(days=1), message.from_user.id)
    refs_week = await ref_db.get_user_refs_by_date(date_now + timedelta(days=1), date_now - timedelta(days=7), message.from_user.id)
    refs_mounth = await ref_db.get_user_refs_by_date(date_now + timedelta(days=1), date_now - timedelta(days=30), message.from_user.id)
    refs_total = await ref_db.get_all_referrals_by_user(message.from_user.id)
    text = (
        f'{texts.information_head}'
        f'Сегодня: <code>{len(refs_today)}</code>\n'
        f'Вчера: <code>{len(refs_tomorrow)}</code>\n'
        f'За последние 7 дней: <code>{len(refs_week)}</code>\n'
        f'За последние 30 дней: <code>{len(refs_mounth)}</code>\n'
        f'Всего: <code>{len(refs_total)}</code>\n'
    )
    await message.bot.send_photo(chat_id=message.chat.id,
                                      photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                      caption=text,
                                      reply_markup=inline.kb_ref_menu())


@router.callback_query(F.data == 'create_ref_link')
async def create_ref_link(call: CallbackQuery, log: Logger):
    log.button('Создать реферальную ссылку')
    link = await create_start_link(call.message.bot, str(call.from_user.id), encode=True)
    await call.message.bot.send_photo(
        call.message.chat.id,
        photo=BufferedInputFile(
            await get_buffer_qr(link),
            filename=f"{call.from_user.id}.png"),
        caption=f'<code>{link}</code>',
    )
    await call.message.delete()
