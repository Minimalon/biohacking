import os
from datetime import datetime, timezone, timedelta

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import AssetType
from core.database.referal_query import ReferralQuery

cs = CS()
ref_query = ReferralQuery()


async def get_asset_by_levels(user_id: int, start_datetime: datetime, end_datetime: datetime):
    result = []
    for ref_level in await ref_query.get_all_referrals_by_level(user_id):
        assets = await cs.get_assets(ref_level.user_id, type=AssetType.ADD)
        sum_amount = sum([
            a.amount
            for a in assets
            if start_datetime <= a.time.astimezone(timezone.utc) <= end_datetime
        ])
        if sum_amount > 0:
            result.append([ref_level, sum_amount, [
            a
            for a in assets
            if start_datetime <= a.time.astimezone(timezone.utc) <= end_datetime
        ]])
    return result


async def test():
    date_now = datetime.now(timezone.utc)
    start_datetime = datetime(date_now.year, date_now.month, date_now.day) - timedelta(days=1)
    end_datetime = datetime(date_now.year, date_now.month, date_now.day, 23, 59, 59) - timedelta(days=1)
    start_datetime = start_datetime.replace(tzinfo=timezone.utc)
    end_datetime = end_datetime.replace(tzinfo=timezone.utc)
    return await get_asset_by_levels(388039160, start_datetime, end_datetime)