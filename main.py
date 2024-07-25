import asyncio
from aiogram import Bot, Dispatcher
from core.services.__for_copy.handlers.callback.default import router as default_router
from core.services.__for_copy.handlers.message import router as message_router


# Запуск бота
async def main():
    bot = Bot(token="7324476984:AAHx1f3o-vVE14WfFDa12J0X0bb27eb4JIM")
    dp = Dispatcher()

    dp.include_routers(message_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())