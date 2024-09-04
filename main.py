import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from core.commands.admins import get_admin_commands
from core.commands.client import get_commands_clients
from core.commands.employee import get_commands_employee
from core.database.model import init_models
from config import *
from core.loggers.make_loggers import create_loggers
from core.middlewares.add_var import CallBackMiddleware, MessageMiddleware, ErrorEventMiddleware
from core.services.admin.handlers.routers import admin_routers
from core.services.referals.handlers.routers import referals_routers
from core.services.start.handlers.routers import routers as start_routers
from core.services.test.handlers.routers import test_routers


# Запуск бота
async def main():
    await init_models()
    await create_loggers()
    tg_config = TelegramConfig()
    bot = Bot(token=tg_config.TOKEN,
              default=DefaultBotProperties(
                  parse_mode='HTML'
              ))
    storage = RedisStorage.from_url(await RedisConfig().url())
    dp = Dispatcher(storage=storage)

    await get_commands_clients(bot)
    await get_admin_commands(bot)
    await get_commands_employee(bot)

    # Мидлвари
    dp.callback_query.middleware(CallBackMiddleware())
    dp.message.middleware(MessageMiddleware())
    dp.errors.middleware(ErrorEventMiddleware())

    # Команда /start
    dp.include_routers(*start_routers)
    dp.include_routers(*admin_routers)

    # Рефералка
    dp.include_routers(*referals_routers)

    # Тесты команд
    dp.include_routers(*test_routers)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
