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

bot = Bot(token=tg_cfg.TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


async def asset_referals_by_levels(start_datetime: datetime, end_datetime: datetime):
    await ref_query.delete_double_referrals()
    uniq_referals = await ref_query.get_all_uniq_referrals()
    cs = CS()
    for uniq_ref in uniq_referals:
        notify = []
        all_assets = []
        clients_cache = {}

        for ref_level in await ref_query.get_all_referrals_by_level(uniq_ref.ref_id):
            assets = await cs.get_assets(ref_level.user_id, type=AssetType.ADD)

            filtered_awards = [
                asset
                for asset in assets
                if start_datetime <= asset.time.astimezone(timezone.utc) <= end_datetime
            ]

            if filtered_awards:
                sum_amount = sum(a.amount for a in filtered_awards)
                sum_assets = round(sum_amount * ref_level.commission_rate, 0)
                if not config.DEVELOPE_MODE:
                    await cs.post_asset(
                        Asset(
                            cardNumber=uniq_ref.ref_id,
                            amount=sum_assets,
                            type=AssetType.ADD,
                            additionalInfo={
                                "type": AwardsType.REFERAL_SYSTEM.value,
                                "level": str(ref_level.level),
                                "commission_rate": str(ref_level.commission_rate),
                                "from_user_id": str(ref_level.user_id),
                            },
                        )
                    )
                    await award_query.add_award(
                        ReferalAward(
                            user_id=uniq_ref.ref_id,
                            from_user_id=ref_level.user_id,
                            amount=sum_assets,
                            type=AwardsType.REFERAL_SYSTEM.value,
                            level=ref_level.level,
                            commission_rate=ref_level.commission_rate,
                        )
                    )

                refAwards_log.info(
                    f"Вознаграждение пользователя: {uniq_ref.ref_id} - {sum_assets} за уровень {ref_level.level} с комиссией {ref_level.commission_rate}"
                )
                notify.append((ref_level, sum_assets))
                all_assets.extend(filtered_awards)
            else:
                refAwards_log.info(
                    f"Вознаграждение пользователя: {uniq_ref.ref_id} - 0 за уровень {ref_level.level} с комиссией {ref_level.commission_rate}"
                )

        if notify:
            levels = {level.level: sum_assets for level, sum_assets in notify}
            content = as_marked_section(
                texts.awards_head.strip(),
                *[
                    as_key_value(f"Уровень {key}", f"{value / 100} руб")
                    for key, value in levels.items()
                ],
            )
            assets_message = f"➖➖➖📋Операции📋➖➖➖\n"
            for asset in filtered_awards:
                card_number = int(asset.cardNumber)
                client = clients_cache.get(card_number)
                if not client:
                    client = await db.get_client(card_number)
                    clients_cache[card_number] = client
                assets_message += (
                    f'➖<b>Дата</b>: {asset.time.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")}\n'
                    f"➖<b>Сумма</b>: {asset.amount / 100} руб\n"
                    f"➖<b>Номер карты</b>: {asset.cardNumber}\n"
                    f"➖<b>Имя</b>: {client.first_name}\n"
                    f"➖<b>Телефон</b>: {client.phone_number}\n"
                    # f'➖<b>Уровень</b>: {[l.level for l, a in notify if l.user_id == asset.cardNumber][0]}\n'
                    "➖➖➖➖➖➖➖➖\n"
                )

            user_id = uniq_ref.ref_id if not config.DEVELOPE_MODE else 5263751490
            try:
                await bot.send_photo(
                    user_id,
                    photo=FSInputFile(Path(config.dir_path, "files", "8.jpg")),
                    **content.as_kwargs(
                        text_key="caption", entities_key="caption_entities"
                    ),
                )
            except Exception as e:
                refAwards_log.exception(e)
            try:
                await bot.send_photo(
                    user_id,
                    photo=FSInputFile(Path(config.dir_path, "files", "1.jpg")),
                    caption=assets_message,
                )
            except Exception as e:
                refAwards_log.exception(e)


async def referals_main():
    date_now = datetime.now(timezone.utc)

    # Вчерашние вознаграждения
    if config.DEVELOPE_MODE:
        start_datetime = datetime(
            date_now.year, date_now.month, date_now.day
        ) - timedelta(days=2)
    else:
        start_datetime = datetime(
            date_now.year, date_now.month, date_now.day
        ) - timedelta(days=1)
    end_datetime = datetime(
        date_now.year, date_now.month, date_now.day, 23, 59, 59
    ) - timedelta(days=1)
    start_datetime = start_datetime.replace(tzinfo=timezone.utc)
    end_datetime = end_datetime.replace(tzinfo=timezone.utc)
    await asset_referals_by_levels(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )


if __name__ == "__main__":
    import asyncio

    date_now = datetime.now(timezone.utc)
    start_datetime = datetime(date_now.year, date_now.month, date_now.day) - timedelta(
        days=1
    )
    end_datetime = datetime(
        date_now.year, date_now.month, date_now.day, 23, 59, 59
    ) - timedelta(days=1)
