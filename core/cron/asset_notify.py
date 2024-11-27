from datetime import date
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import Asset, AssetType, AwardsType
from core.database.award_query import AwardQuery
from core.loggers.make_loggers import refAwards_log
from core.utils import texts

bot = Bot(token=config.tg_cfg.TOKEN,
          default=DefaultBotProperties(
              parse_mode='HTML'
          ))
aq = AwardQuery()


async def notify_assets():
    reg_awards = await aq.get_asset_notifys()
    for notify in reg_awards:
        try:
            msg = (
                f'{texts.success_head}'
                f'Благодарим за покупку!\n'
                f'Вам начисленно {notify.amount / 100} баллов.\n'
                f'С нетерпением ждём вашего визита!'
            )
            await bot.send_photo(notify.user_id,
                                 photo=FSInputFile(Path(config.dir_path, 'files', '6.jpg')),
                                 caption=msg)
            await aq.set_sended_notify(notify.id)
        except Exception as e:
            refAwards_log.exception(e)


if __name__ == '__main__':
    import asyncio

    asyncio.run(notify_assets())
