import asyncio

from aiogram.client.default import DefaultBotProperties

from core.loggers.make_loggers import except_log
from core.utils.celery_app import app
from aiogram import Bot
from config import tg_cfg


@app.task
def send_message():
    try:
        except_log.info('send_message')
        bot = Bot(token=tg_cfg.TOKEN,
                  default=DefaultBotProperties(
                      parse_mode='HTML'
                  ))
        asyncio.run(bot.send_message(5263751490, '123'))
    except Exception as e:
        except_log.exception(e)


