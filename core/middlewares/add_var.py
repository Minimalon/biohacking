import json
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, ErrorEvent

from core.database.query import Database
from core.loggers.bot_logger import Logger as log


class CallBackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any],
    ) -> Any:
        data['log'] = log(event.message)
        data['db'] = Database()

        return await handler(event, data)


class MessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        data['log'] = log(event)
        data['db'] = Database()

        return await handler(event, data)


class ErrorEventMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[ErrorEvent, Dict[str, Any]], Awaitable[Any]],
            event: ErrorEvent,
            data: dict[str, Any],
    ) -> Any:
        message = event.update.message if event.update.message else event.update.callback_query.message
        data['log'] = log(message)
        data['db'] = Database()

        return await handler(event, data)
