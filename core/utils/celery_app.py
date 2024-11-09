from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from celery import Celery

from config import TelegramConfig

app = Celery('biohacking', broker='pyamqp://guest@10.8.16.18//')

app.autodiscover_tasks(['core.utils.tasks'])