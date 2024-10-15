import asyncio
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import distinct, func, delete

from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ChecklistContentAction, ChecklistContent, ChecklistMenu, CheckListComplete
from core.database.query import Database

from core.services.checklist.pd_models.pd_admin import CLCreateMenu
from core.services.checklist.pd_models.pd_start import PDCheckList


class CheckListQuery(Database):

    def __init__(self):
        super().__init__()

    async def get_all_checklist_menus(self) -> list[ChecklistMenu]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(ChecklistMenu))
            return result.scalars().all()

    async def get_checklist_menu(self, menu_id: int) -> ChecklistMenu | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(ChecklistMenu).where(ChecklistMenu.id == menu_id))
            return result.scalars().first()

    async def get_checklist_menus(self, menu_ids: list[int]) -> list[ChecklistMenu] | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(ChecklistMenu).where(ChecklistMenu.id.in_(menu_ids)))
            return result.scalars().all()

    async def delete_checklist_menu(self, menu_id: int) -> None:
        async with self.AsyncSession() as session:
            await session.execute(delete(ChecklistMenu).where(ChecklistMenu.id == menu_id))
            await session.commit()

    async def add_checklist_menu(self, name: str, description: str = '') -> None:
        async with self.AsyncSession() as session:
            session.add(ChecklistMenu(name=name, description=description))
            await session.commit()

    async def get_checklist_action(self, action_id: int) -> ChecklistContentAction | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(ChecklistContentAction).where(ChecklistContentAction.id == action_id))
            return result.scalars().first()

    async def add_checklist_action(
            self,
            action: EnumCheckListContentActions,
            checklistcontentid: int,
    ) -> None:
        async with self.AsyncSession() as session:
            session.add(ChecklistContentAction(action=action, checklistcontentid=checklistcontentid))
            await session.commit()

    async def checlist_content_by_page(self, menu_id: int, page: int = 1) -> ChecklistContent | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(ChecklistContent)
                .options(
                    joinedload(ChecklistContent.menu),
                    joinedload(ChecklistContent.action),
                )
                .where(ChecklistContent.checklistmenuid == menu_id, ChecklistContent.page == page)
            )
            return result.scalars().first()

    async def get_checklist_content(self, content_id: int) -> ChecklistContent | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(ChecklistContent)
                .options(
                    joinedload(ChecklistContent.menu),
                    joinedload(ChecklistContent.action),
                ).where(ChecklistContent.id == content_id))
            return result.scalars().first()

    async def add_checklist_content(
            self,
            content: str,
            page: int,
            checklistmenuid: int,
            photo_path: str = '',
    ) -> None:
        async with self.AsyncSession() as session:
            session.add(ChecklistContent(
                content=content,
                page=page,
                photo_path=photo_path,
                checklistmenuid=checklistmenuid,
            ))
            await session.commit()

    async def create_checklist(self, cl_menu: CLCreateMenu) -> None:
        async with self.AsyncSession() as session:
            checklist_menu = ChecklistMenu(name=cl_menu.name)
            session.add(checklist_menu)
            await session.commit()
            await session.refresh(checklist_menu)  # Обновляем объект, чтобы получить id

            for content in cl_menu.contents:
                checklist_content = ChecklistContent(
                    content=content.content,
                    page=content.page,
                    file_id=content.file_id,
                    checklistmenuid=checklist_menu.id
                )
                session.add(checklist_content)
                await session.commit()

                session.add(ChecklistContentAction(action=content.action, checklistcontentid=checklist_content.id))
                await session.commit()

    async def complete_checklist(self, checklist: PDCheckList, user_id: int) -> None:
        async with self.AsyncSession() as session:
            for answer in checklist.answers:
                session.add(
                    CheckListComplete(
                        user_id=user_id,
                        time_answer=answer.time_answer,
                        action=answer.action,
                        file_id=answer.file_id,
                        text=answer.text,
                        checklistmenuid=answer.content.checklistmenuid,
                        checklistcontentid=answer.content.id,
                    ))
            await session.commit()

    async def get_unique_user_checklist_complete(self) -> list[int]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(distinct(CheckListComplete.user_id))
            )
            return result.scalars().all()

    async def get_unique_dates_checklist_complete(self, user_id: int) -> list[datetime]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(distinct(CheckListComplete.date)).where(CheckListComplete.user_id == user_id)
            )
            return result.scalars().all()

    async def get_unique_menus_by_user(self, user_id: int, date_menu: date) -> list[int]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(distinct(CheckListComplete.checklistmenuid))
                .where(
                    CheckListComplete.user_id == user_id,
                    func.DATE(CheckListComplete.date) == date_menu
                )
            )
            return result.scalars().all()

    async def get_completes(self, user_id: int, date_menu: date, menu_id: int) -> list[CheckListComplete]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(CheckListComplete)
                .where(
                    CheckListComplete.user_id == user_id,
                    CheckListComplete.checklistmenuid == menu_id,
                    func.DATE(CheckListComplete.date) == date_menu,
                )
            )
            return result.scalars().all()


async def test() -> None:
    db = CheckListQuery()
    print(await db.get_unique_menus_by_user(5263751490, date(2024, 9, 27)))


if __name__ == '__main__':
    asyncio.run(test())
