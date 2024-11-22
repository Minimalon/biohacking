from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.utils.formatting import as_marked_section, as_key_value

import config
from config import tg_cfg
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import AssetType, Asset, AwardsType
from core.database.award_query import AwardQuery
from core.database.model import ReferalAward
from core.database.query import Database
from core.database.referal_query import ReferralQuery
from core.loggers.make_loggers import refAwards_log
from core.utils import texts

ref_query = ReferralQuery()
db = Database()
award_query = AwardQuery()


async def asset_referals_by_levels(start_datetime: datetime, end_datetime: datetime):
    uniq_referals = await ref_query.get_all_uniq_referrals()
    cs = CS()
    for uniq_ref in uniq_referals:
        notify = []
        for ref_level in await ref_query.get_all_referrals_by_level(uniq_ref.ref_id):
            assets = await cs.get_assets(ref_level.user_id, type=AssetType.ADD)

            awards_list = []
            for asset in assets:
                if start_datetime <= asset.time.astimezone(
                        timezone.utc) <= end_datetime and asset.type == AssetType.ADD:
                    awards_list.append(asset)

            # sum_amount = sum([
            #     a.amount
            #     for a in assets
            #     if start_datetime <= a.time.astimezone(timezone.utc) <= end_datetime
            # ])
            if len(awards_list) > 0:
                sum_amount = sum([a.amount for a in awards_list])
                sum_assets = round(sum_amount * ref_level.commission_rate, 0)
                if not config.DEVELOPE_MODE:
                    await cs.post_asset(
                        Asset(
                            cardNumber=uniq_ref.ref_id,
                            amount=sum_assets,
                            type=AssetType.ADD,
                            additionalInfo={
                                'type': AwardsType.REFERAL_SYSTEM.value,
                                'level': str(ref_level.level),
                                'commission_rate': str(ref_level.commission_rate),
                                'from_user_id': str(ref_level.user_id)
                            }
                        )
                    )
                    await award_query.add_award(
                        ReferalAward(
                            user_id=uniq_ref.ref_id,
                            from_user_id=ref_level.user_id,
                            amount=sum_assets,
                            type=AwardsType.REFERAL_SYSTEM.value,
                            level=ref_level.level,
                            commission_rate=ref_level.commission_rate
                        )
                    )

                refAwards_log.info(
                    f'Вознаграждение пользователя: {uniq_ref.ref_id} - {sum_assets} за уровень {ref_level.level} с комиссией {ref_level.commission_rate}')
                notify.append([ref_level, sum_assets])
            else:
                refAwards_log.info(
                    f'Вознаграждение пользователя: {uniq_ref.ref_id} - 0 за уровень {ref_level.level} с комиссией {ref_level.commission_rate}')

        if notify:
            levels = defaultdict(dict)
            for user, sum_assets in notify:
                levels[user.level] = sum_assets
            content = as_marked_section(
                texts.awards_head.strip(),
                *[as_key_value(f'Уровень {key}', f'{value / 100} руб') for key, value in levels.items()],
            )
            assets_message = f'➖➖➖📋Операции📋➖➖➖\n'
            for asset in assets:
                client = await db.get_client(int(asset.cardNumber))
                assets_message += f'➖<b>Дата</b>: {asset.time.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")}\n'
                assets_message += f'➖<b>Сумма</b>: {asset.amount / 100} руб\n'
                # assets_message += f'➖<b>Тип</b>: {asset.type}\n'
                assets_message += f'➖<b>Номер карты</b>: {asset.cardNumber}\n'
                assets_message += f'➖<b>Имя</b>: {client.first_name}\n'
                assets_message += f'➖<b>Телефон</b>: {client.phone_number}\n'
                assets_message += '➖➖➖➖➖➖➖➖\n'

            bot = Bot(token=tg_cfg.TOKEN,
                      default=DefaultBotProperties(
                          parse_mode='HTML'
                      ))
            if config.DEVELOPE_MODE:
                try:
                    await bot.send_photo(5263751490,
                                         photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                         **content.as_kwargs(text_key='caption', entities_key='caption_entities'))
                except Exception as e:
                    refAwards_log.exception(e)
                try:
                    await bot.send_photo(5263751490,
                                         photo=FSInputFile(Path(config.dir_path, 'files', '1.jpg')),
                                         caption=assets_message)
                except Exception as e:
                    refAwards_log.exception(e)
            else:
                try:
                    await bot.send_photo(uniq_ref.ref_id,
                                         photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                         **content.as_kwargs(text_key='caption', entities_key='caption_entities'))
                except Exception as e:
                    refAwards_log.exception(e)
                try:
                    await bot.send_photo(uniq_ref.ref_id,
                                         photo=FSInputFile(Path(config.dir_path, 'files', '1.jpg')),
                                         caption=assets_message)
                except Exception as e:
                    refAwards_log.exception(e)


async def referals_main():
    date_now = datetime.now(timezone.utc)

    # Вчерашние вознаграждения
    if config.DEVELOPE_MODE:
        start_datetime = datetime(date_now.year, date_now.month, date_now.day) - timedelta(days=2)
    else:
        start_datetime = datetime(date_now.year, date_now.month, date_now.day) - timedelta(days=1)
    end_datetime = datetime(date_now.year, date_now.month, date_now.day, 23, 59, 59) - timedelta(days=1)
    start_datetime = start_datetime.replace(tzinfo=timezone.utc)
    end_datetime = end_datetime.replace(tzinfo=timezone.utc)
    await asset_referals_by_levels(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )


if __name__ == '__main__':
    import asyncio
    print(config.DEVELOPE_MODE)
    asyncio.run(referals_main())
