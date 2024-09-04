from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from core.database.query import Database


async def get_admin_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Главное меню'
        ),
        BotCommand(
            command='admin',
            description='Админ панель'
        ),
        BotCommand(
            command='ref',
            description='Создать реферальную ссылку'
        ),
    ]
    db = Database()
    for admin in await db.get_admins():
        try:
            await bot.set_my_commands(commands, BotCommandScopeChat(chat_id=admin.user_id))
        except Exception:
            pass
