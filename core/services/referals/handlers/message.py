from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.deep_linking import create_start_link

from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.loggers.bot_logger import Logger
from core.utils import texts
from core.utils.qr import generate_qr, get_buffer_qr

router = Router()


@router.message(Command('ref'))
async def referal(message: Message, log: Logger, db: Database):
    client = await db.get_client(message.from_user.id)
    log.button('/ref')
    if not client.role.rolename in [ClientRolesEnum.ADMIN, ClientRolesEnum.SUPERADMIN, ClientRolesEnum.EMPLOYEE]:
        await message.answer(texts.no_access)
        log.error('Пользователь не является админом')
        return

    link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
    await message.bot.send_photo(
        message.chat.id,
        photo=BufferedInputFile(
            await get_buffer_qr(link),
            filename=f"{message.from_user.id}.png"),
        caption=link
    )
