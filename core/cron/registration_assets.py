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
cs = CS()


async def registration_assets():
    reg_awards = await aq.get_reg_awards()
    for award in reg_awards:
        try:
            if not config.DEVELOPE_MODE:
                await cs.post_asset(Asset(
                    cardNumber=award.user_id,
                    amount=award.amount,
                    type=AssetType.ADD,
                    additionalInfo={
                        'type': AwardsType.REGISTRATION
                    }
                ))
            msg = (
                f'{texts.success_head}'
                f'Благодарим за вчерашнюю покупку!\n'
                f'Сегодня вам пришли подарочные {award.amount / 100} баллов. Используйте их на кислородные коктейли в НейроБаре со 100% скидкой.\n'
                f'С нетерпением ждём вашего визита!'
            )
            await bot.send_photo(award.user_id,
                                 photo=FSInputFile(Path(config.dir_path, 'files', '9.jpg')),
                                 caption=msg)
            await aq.set_reg_sended(award.id)
        except Exception as e:
            refAwards_log.exception(e)


if __name__ == '__main__':
    import asyncio

    asyncio.run(registration_assets())
