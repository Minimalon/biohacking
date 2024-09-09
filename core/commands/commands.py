from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChatMember, BotCommandScopeChat

from core.database.model import ClientRolesEnum, admins
from core.database.query import Database

client_commands = [
    BotCommand(
        command='start',
        description='Бонусная карта'
    ),
]

employee_commands = [
    BotCommand(
        command='ref',
        description='Реферальная ссылка'
    ),
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
    BotCommand(
        command='ref',
        description='Реферальная ссылка'
    ),
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
                    ))
            elif client.role.rolename == ClientRolesEnum.EMPLOYEE:
                await bot.set_my_commands(
                    client_commands + employee_commands,
                    BotCommandScopeChat(
                        chat_id=client.chat_id,
                    ))
            elif client.role.rolename in admins():
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
            print(e)
