from datetime import datetime, timedelta, timezone

from core.artix.CS.cs import CS
from core.artix.CS.pd_model import AssetType, Asset, AwardsType
from core.database.query import Database
from core.database.referal_query import ReferralQuery
from core.loggers.make_loggers import refAwards_log

ref_query = ReferralQuery()
db = Database()


async def asset_referals_by_levels(start_datetime: datetime, end_datetime: datetime):
    uniq_referals = await ref_query.get_all_uniq_referrals()
    cs = CS()
    for uniq_ref in uniq_referals:
        for ref_level in await ref_query.get_all_referrals_by_level(uniq_ref.ref_id):
            assets = await cs.get_assets(ref_level.user_id, type=AssetType.ADD)
            sum_amount = sum([
                a.amount
                for a in assets
                if start_datetime <= a.time.astimezone(timezone.utc) <= end_datetime
            ])
            if sum_amount > 0:
                awards = round(sum_amount * ref_level.commission_rate, 0)
                await cs.post_asset(
                    Asset(
                        cardNumber=uniq_ref.ref_id,
                        amount=awards,
                        type=AssetType.ADD,
                        additionalInfo={
                            'type': AwardsType.REFERAL_SYSTEM.value,
                            'level': str(ref_level.level),
                            'commission_rate': str(ref_level.commission_rate),
                            'from_user_id': str(uniq_ref.user_id)
                        }
                    )
                )
                refAwards_log.info(
                    f'Вознаграждение пользователя: {uniq_ref.ref_id} - {awards} за уровень {ref_level.level} с комиссией {ref_level.commission_rate}')
            else:
                refAwards_log.info(
                    f'Вознаграждение пользователя: {uniq_ref.ref_id} - 0 за уровень {ref_level.level} с комиссией {ref_level.commission_rate}')


async def referals_main():
    date_now = datetime.now(timezone.utc)


    # Вчерашние вознаграждения
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

    asyncio.run(referals_main())
