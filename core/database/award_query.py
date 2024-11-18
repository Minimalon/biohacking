import enum

from sqlalchemy import text, delete, update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.artix.CS.pd_model import AwardsType
from core.database.model import ReferalAward
from core.database.query import Database
from typing import List


class AwardQuery(Database):

    def __init__(self):
        super().__init__()

    async def add_award(self, ref_award: ReferalAward) -> None:
        async with self.AsyncSession() as session:
            session.add(ref_award)
            await session.commit()
