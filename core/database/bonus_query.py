import enum

from sqlalchemy import text, delete, update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.artix.CS.pd_model import AwardsType
from core.database.model import BonusAward
from core.database.query import Database
from typing import List


class BonusQuery(Database):

    def __init__(self):
        super().__init__()

    async def get_bonuses(self) -> List[BonusAward]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(BonusAward))
            return result.scalars().all()

    async def get_bonuses_by_user_id(self, user_id: int) -> List[BonusAward]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(BonusAward).where(BonusAward.user_id == user_id))
            return result.scalars().all()

    async def add_award(self, user_id: int, amount: int, type: AwardsType) -> BonusAward:
        async with self.AsyncSession() as session:
            award = BonusAward(user_id=user_id, amount=amount, type=type)
            session.add(award)
            await session.commit()
            await session.refresh(award)
            return award
