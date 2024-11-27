import enum
from datetime import date

from sqlalchemy import text, delete, update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.artix.CS.pd_model import AwardsType
from core.database.model import ReferalAward, RegistrationAssets, AssetNotify
from core.database.query import Database
from typing import List


class AwardQuery(Database):

    def __init__(self):
        super().__init__()

    async def add_award(self, ref_award: ReferalAward) -> None:
        async with self.AsyncSession() as session:
            session.add(ref_award)
            await session.commit()

    async def add_registration_award(self, regAward: RegistrationAssets) -> None:
        async with self.AsyncSession() as session:
            session.add(regAward)
            await session.commit()

    async def get_reg_awards(self) -> List[RegistrationAssets] | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(RegistrationAssets).where(RegistrationAssets.created_at < date.today(),
                                                 RegistrationAssets.sended == False)
            )
            return result.scalars().all()

    async def set_reg_sended(self, id: int) -> None:
        async with self.AsyncSession() as session:
            await session.execute(update(RegistrationAssets).where(RegistrationAssets.id == id).values(sended = True))
            await session.commit()

    async def get_asset_notifys(self) -> List[AssetNotify] | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(AssetNotify).where(AssetNotify.sended == False)
            )
            return result.scalars().all()

    async def set_sended_notify(self, id: int) -> None:
        async with self.AsyncSession() as session:
            await session.execute(update(AssetNotify).where(AssetNotify.id == id).values(sended = True))
            await session.commit()