from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.future import select
from sqlalchemy import update

from core.database.model import *
import config
from core.services.checklist.pd_models.pd_admin import CLCreateMenu


class Database:
    def __init__(self):
        self.engine = create_async_engine(config.db_cfg.get_url())
        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def add_client(
            self,
            phone_number: str,
            first_name: str,
            last_name: str,
            username: str,
            user_id: int,
            chat_id: int,
            rolename: ClientRolesEnum = ClientRolesEnum.CLIENT
    ) -> None:
        async with self.AsyncSession() as session:
            session.add(
                Clients(
                    phone_number=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    user_id=user_id,
                    chat_id=chat_id,
                ))
            session.add(
                ClientRoles(
                    user_id=user_id,
                    rolename=rolename,
                ))
            await session.commit()

    async def get_client(self, user_id: int) -> Clients | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients).filter(Clients.user_id == user_id).
                options(
                    joinedload(Clients.role),
                )
            )
            return result.scalars().first()

    async def get_clients(self, user_id: list[int]) -> list[Clients] | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients).where(Clients.user_id.in_(user_id)).
                options(
                    joinedload(Clients.role),
                )
            )
            return result.scalars().all()

    async def get_all_clients(self) -> list[Clients]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients).options(
                    joinedload(Clients.role),
                )
            )
            return result.unique().scalars().all()

    async def get_client_by_phone(self, phone_number: str) -> Clients | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Clients).filter(Clients.phone_number == phone_number))
            return result.scalars().first()

    async def get_client_by_role(self, rolename: ClientRolesEnum) -> list[Clients]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Clients).where(ClientRoles.rolename == rolename).join(ClientRoles))
            return result.scalars().all()

    async def update_client(self, user_id: int, update_data: dict) -> None:
        async with self.AsyncSession() as session:
            client = await session.get(Clients, user_id)
            for key, value in update_data.items():
                setattr(client, key, value)
            await session.commit()

    async def delete_client(self, user_id: int) -> None:
        async with self.AsyncSession() as session:
            client = await session.get(Clients, user_id)
            await session.delete(client)
            await session.commit()

    async def add_referral(self, user_id: int, ref_id: int) -> None:
        async with self.AsyncSession() as session:
            session.add(Referrals(user_id=user_id, ref_id=ref_id))
            await session.commit()

    async def update_role_client(self, user_id: int, rolename: ClientRolesEnum = ClientRolesEnum.CLIENT) -> None:
        async with self.AsyncSession() as session:
            await session.execute(update(ClientRoles).where(ClientRoles.user_id == user_id).values(rolename=rolename))
            await session.commit()


async def test():
    db = Database()
    # clcontent = await db.next_page_checlist_content(1, page=1)
    # print(clcontent.action)
    # clients = await db.get_all_clients()
    # for client in clients:
    #     for role in client.role:
    #         print(role.rolename)

    # await db.add_checklist_menu('Открытие смены')
    # await db.add_checklist_content('Тест <b>123</b>', 1, 1, )
    # await db.add_checklist_action(EnumCheckListContentActions.NONE, 1)

    await db.delete_client(376986939)


if __name__ == '__main__':
    import asyncio

    asyncio.run(test())
