from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChatMember, BotCommandScopeChat

from core.database.model import ClientRolesEnum
from core.database.query import Database
from core.loggers.make_loggers import setCommands_log

client_commands = [
    BotCommand(
        command='start',
        description='Бонусная карта'
    ),
    BotCommand(
        command='ref',
        description='Реферальная ссылка'
    ),
]

employee_commands = [
    BotCommand(
        command='checklist',
        description='Чек лист'
    ),
]

admin_commands = [
    BotCommand(
        command='admin',
        description='Админ панель'
    ),
]

bloger_commands = [
]


async def set_commands(bot: Bot):
    db = Database()
    for client in await db.get_all_clients():
        try:
            if client.role.rolename == ClientRolesEnum.CLIENT:
                await bot.set_my_commands(
                    client_commands,
                    BotCommandScopeChat(
                        chat_id=client.chat_id,
                    )
                )
            elif client.role.rolename == ClientRolesEnum.EMPLOYEE:
                await bot.set_my_commands(
                    client_commands + employee_commands,
                    BotCommandScopeChat(
                        chat_id=client.chat_id,
                    ))
            elif client.role.rolename in [ClientRolesEnum.ADMIN, ClientRolesEnum.SUPERADMIN]:
                await bot.set_my_commands(
                    client_commands + admin_commands + employee_commands,
                    BotCommandScopeChat(
                        chat_id=client.chat_id,
                    ))
            elif client.role.rolename in ClientRolesEnum.BLOGER:
                await bot.set_my_commands(
                    client_commands + bloger_commands,
                    BotCommandScopeChat(
                        chat_id=client.chat_id,
                    ))
        except Exception as e:
            log = setCommands_log.bind(
                filter='commands',
                client_id=client.user_id,
                chat_id=client.chat_id,
                roles=client.role
            )
            log.error(e)
