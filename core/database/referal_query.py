import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, date

from sqlalchemy import text, and_
from sqlalchemy.future import select

from core.database.model import Referrals
from core.database.query import Database
from typing import NamedTuple, List


@dataclass
class ReferralsByLevel:
    user_id: int
    ref_id: int
    level: int
    commission_rate: float


class ReferralQuery(Database):

    def __init__(self):
        super().__init__()

    async def get_all_referrals_by_level(self, root_user_id: int) -> List[ReferralsByLevel] | None:
        """
        Получение всех рефералов для заданного пользователя и всех уровней ниже, включая расчет комиссий.
        """
        async with self.AsyncSession() as session:
            # SQL-запрос с использованием CTE для получения всех рефералов и расчета комиссий
            stmt = text("""
                WITH RECURSIVE referral_tree(user_id, ref_id, level, commission_rate) AS (
                    SELECT 
                        user_id, 
                        ref_id, 
                        1 AS level,
                        0.05 AS commission_rate  -- Комиссия для 1-го уровня: 5%
                    FROM referrals
                    WHERE ref_id = :root_user_id
                    UNION ALL
                    SELECT 
                        r.user_id, 
                        r.ref_id, 
                        rt.level + 1,
                        CASE 
                            WHEN rt.level + 1 = 2 THEN 0.03  -- Комиссия для 2-го уровня: 3%
                            WHEN rt.level + 1 = 3 THEN 0.02  -- Комиссия для 3-го уровня: 2%
                            WHEN rt.level + 1 = 4 THEN 0.01  -- Комиссия для 4-го уровня: 1%
                            WHEN rt.level + 1 BETWEEN 5 AND 10 THEN 0.005  -- Комиссия для уровней 5-10: 0.5%
                            ELSE 0  -- Комиссия для уровней выше 10: 0%
                        END AS commission_rate
                    FROM referrals r
                    JOIN referral_tree rt ON r.ref_id = rt.user_id
                )
                SELECT user_id, ref_id, level, commission_rate
                FROM referral_tree
            """)

            result = await session.execute(stmt, {'root_user_id': root_user_id})
            return [ReferralsByLevel(*row) for row in result.fetchall()]

    async def get_all_referrals_by_user(self, user_id: int) -> List[Referrals] | None:
        """
        Получение всех рефералов для заданного пользователя.
        """
        async with self.AsyncSession() as session:
            result = await session.execute(select(Referrals).where(Referrals.ref_id == user_id))
            return result.scalars().all()

    async def get_user_refs_by_date(self, start_date: date, end_date: date, user_id: int) -> List[Referrals]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Referrals)
                .where(and_(Referrals.date <= start_date, Referrals.date >= end_date),
                    Referrals.ref_id == user_id)
            )
            return result.scalars().all()


async def main():
    ref_db = ReferralQuery()
    date_now = date.today()
    refs_today = await ref_db.get_user_refs_by_date(date_now, date_now - timedelta(days=1), 5263751490)
    for ref in refs_today:
        print(ref.date)


if __name__ == '__main__':
    asyncio.run(main())
