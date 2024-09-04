from core.loggers.make_loggers import bot_log
from aiogram.types import Message


class Logger:
    def __init__(self, message: Message, st_info: dict = None, title: str = ''):
        self.log = bot_log.bind(
            first_name=message.chat.first_name,
            chat_id=message.chat.id,
        )
        self.t = title

    def button(self, button_name: str):
        self.log.info(f'Нажали кнопку "{button_name}"')

    def info(self, message: str):
        self.log.info(f'{message}')

    def debug(self, message: str):
        self.log.debug(f'{message}')

    def error(self, message: str):
        self.log.error(f'{message}')

    def success(self, message: str):
        self.log.success(f'{message}')

    def exception(self, message):
        self.log.exception(f'{message}')
