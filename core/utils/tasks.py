import asyncio

from celery import shared_task
from core.utils.celery_app import app
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from config import TelegramConfig


@app.task
def add(x, y):
    print('add')
    return x + y


@app.task
def sub(x, y):
    return x - y


@app.task
async def send_message():
    tg_config = TelegramConfig()
    bot = Bot(token=tg_config.TOKEN)
    await bot.send_message(5263751490, '123')
