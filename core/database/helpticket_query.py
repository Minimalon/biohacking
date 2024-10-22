from sqlalchemy import text, delete, update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.database.model import HelpTicket, HelpTicketStatus, WorkHelpTicket
from core.database.query import Database
from typing import List


class HelpTicketQuery(Database):

    def __init__(self):
        super().__init__()

    async def get_default_status(self) -> HelpTicketStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(HelpTicketStatus).where(HelpTicketStatus.default == True))
            return result.scalars().first()

    async def get_visible_statuses(self) -> List[HelpTicketStatus]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(HelpTicketStatus).where(HelpTicketStatus.visible == True))
            return result.scalars().all()

    async def get_status(self, status_id: int) -> HelpTicketStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(HelpTicketStatus).where(HelpTicketStatus.id == status_id))
            return result.scalars().first()

    async def get_close_status(self) -> HelpTicketStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(HelpTicketStatus).where(HelpTicketStatus.closed == True))
            return result.scalars().first()

    async def create_ticket(self, user_id: int, msg: str = '') -> HelpTicket:
        async with self.AsyncSession() as session:
            default_status = await self.get_default_status()
            if not default_status:
                raise ValueError('Отсутствует статус по умолчанию')
            ticket = HelpTicket(user_id=user_id, msg=msg, status=default_status.id)
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            return ticket

    async def get_ticket(self, ticket_id: int) -> HelpTicket | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(HelpTicket)
                .options(joinedload(HelpTicket.ticket_status))
                .where(HelpTicket.id == ticket_id))
            return result.scalars().first()

    async def get_tickets_not_closed_by_user(self, user_id: int) -> List[WorkHelpTicket]:
        async with self.AsyncSession() as session:
            closed_status = await self.get_close_status()
            result = await session.execute(
                select(WorkHelpTicket)
                .where(WorkHelpTicket.user_id == user_id)
                .where(WorkHelpTicket.status_id != closed_status.id)
            )
            return result.scalars().all()

    async def update_ticket_status(self, ticket_id: int, status_id: int) -> None:
        async with self.AsyncSession() as session:
            await session.execute(update(HelpTicket).where(HelpTicket.id == ticket_id).values(status=status_id))
            await session.execute(update(WorkHelpTicket).where(WorkHelpTicket.id == ticket_id).values(status_id=status_id))
            await session.commit()

    async def get_history_ticket(self, ticket_id: int) -> WorkHelpTicket | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(WorkHelpTicket)
                .where(WorkHelpTicket.ticket_id == ticket_id))
            return result.scalars().first()

    async def create_history_ticket(self, ticket_id: int, status_id: int,
                                    user_id: int) -> WorkHelpTicket:
        async with self.AsyncSession() as session:
            history = WorkHelpTicket(ticket_id=ticket_id, status_id=status_id, user_id=user_id)
            session.add(history)
            await session.commit()
            await session.refresh(history)
            return history
