from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def get_commands_employee(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Главное меню'
        ),
        BotCommand(
            command='ref',
            description='Реферальная ссылка'
        ),
        BotCommand(
            command='checklist',
            description='Чек лист'
        ),

    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
