import asyncio
from collections import defaultdict
import logging
import pandas as pd
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, joinedload

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import AssetType
from core.database.model import *


class Database:
    def __init__(self):
        self.engine = create_async_engine(config.db_cfg.get_url())
        self.AsyncSession = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def add_client(
        self,
        phone_number: str,
        first_name: str,
        last_name: str,
        username: str,
        user_id: int,
        chat_id: int,
        rolename: ClientRolesEnum = ClientRolesEnum.CLIENT,
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
                )
            )
            session.add(
                ClientRoles(
                    user_id=user_id,
                    rolename=rolename,
                )
            )
            await session.commit()

    async def get_client(self, user_id: int) -> Clients | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients)
                .filter(Clients.user_id == user_id)
                .options(
                    joinedload(Clients.role),
                )
            )
            return result.scalars().first()

    async def get_clients(self, user_id: list[int]) -> list[Clients] | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients)
                .where(Clients.user_id.in_(user_id))
                .options(
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

    async def get_all_clients_without_role(self) -> list[Clients]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Clients))
            return result.unique().scalars().all()

    async def get_client_by_phone(self, phone_number: str) -> Clients | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients).filter(Clients.phone_number == phone_number)
            )
            return result.scalars().first()

    async def get_client_by_role(self, rolename: ClientRolesEnum) -> list[Clients]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Clients)
                .where(ClientRoles.rolename == rolename)
                .join(ClientRoles)
            )
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

    async def update_role_client(
        self, user_id: int, rolename: ClientRolesEnum = ClientRolesEnum.CLIENT
    ) -> None:
        async with self.AsyncSession() as session:
            await session.execute(
                update(ClientRoles)
                .where(ClientRoles.user_id == user_id)
                .values(rolename=rolename)
            )
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
    user_id = 376986939
    cs = CS()
    await db.delete_client(user_id)
    await cs.delete_client(user_id)


async def total_balance_all_users():
    db = Database()
    clients = await db.get_all_clients()
    cs = CS()
    total_amount = 0

    user_balances = defaultdict(int)
    for client in clients:
        client_balance = await cs.get_card_balance(client.user_id)
        total_amount += client_balance.balance / 100
        user_balances[client.user_id] = client_balance.balance / 100
    return total_amount, user_balances


async def generate_assets_report():
    db = Database()
    cs = CS()
    clients = await db.get_all_clients_without_role()

    detailed_data = []
    summary_data = []

    # Сбор данных по каждому клиенту
    for client in clients:
        try:
            # Получаем все ассеты с пагинацией
            all_assets = []
            page_number = 0
            while True:
                assets = await cs.get_assets(
                    cardNumber=str(client.user_id),
                    pageNumber=page_number,
                    pageSize=500,
                    sortByTimeDescending=True,
                )
                if not assets:
                    break
                all_assets.extend(assets)
                if len(assets) < 500:
                    break
                page_number += 1

            # Рассчитываем баланс
            balance_kop = 0
            for asset in all_assets:
                # Определяем влияние операции на баланс
                if asset.type == AssetType.ADD:
                    balance_kop += asset.amount
                elif asset.type == AssetType.SUB:
                    balance_kop -= asset.amount

                # Добавляем детали
                detailed_data.append(
                    {
                        "user_id": client.user_id,
                        "Имя": client.first_name,
                        "Фамилия": client.last_name,
                        "Номер карты": asset.cardNumber,
                        "Счёт": asset.accountNumber,
                        "Время операции": asset.time,
                        "Сумма (коп)": asset.amount,
                        "Тип операции": asset.type.value,
                        "Статус": asset.state.value,
                        "Комментарий": asset.additionalInfo.get("comment", ""),
                        "ID операции": asset.sessionId,
                        "Источник": asset.lastSource,
                        "Терминал": asset.terminalId,
                    }
                )

            # Добавляем в сводку
            summary_data.append(
                {
                    "user_id": client.user_id,
                    "Имя": client.first_name,
                    "Фамилия": client.last_name,
                    "Баланс (руб)": balance_kop / 100,
                    "Кол-во операций": len(all_assets),
                }
            )

        except Exception as e:
            print(f"Ошибка для клиента {client.user_id}: {str(e)}")

    # Создаём DataFrame
    df_summary = pd.DataFrame(summary_data)
    df_detail = pd.DataFrame(detailed_data)

    # Упорядочиваем колонки
    detail_columns = [
        "user_id",
        "Имя",
        "Фамилия",
        "Номер карты",
        "Счёт",
        "Время операции",
        "Сумма (коп)",
        "Тип операции",
        "Статус",
        "Комментарий",
        "ID операции",
        "Источник",
        "Терминал",
    ]

    # Сохраняем в Excel
    with pd.ExcelWriter("../../full_report.xlsx", engine="xlsxwriter") as writer:
        df_summary.to_excel(
            writer,
            sheet_name="Сводка",
            index=False,
            columns=["user_id", "Имя", "Фамилия", "Баланс (руб)", "Кол-во операций"],
        )

        df_detail[detail_columns].to_excel(
            writer, sheet_name="Детализация", index=False
        )

        # Автонастройка ширины колонок
        for sheet in writer.sheets:
            worksheet = writer.sheets[sheet]
            for idx, col in enumerate(df_detail.columns):
                max_len = max(df_detail[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(idx, idx, max_len + 2)

    return "full_report.xlsx"


# Ограничиваем количество одновременных запросов
SEMAPHORE_LIMIT = 10  # Можно регулировать в зависимости от возможностей сервера
RETRY_ATTEMPTS = 3  # Количество попыток повторного запроса


MAX_CONCURRENT_REQUESTS = 5
PAGE_SIZE = 100


async def generate_assets_report():
    db = Database()
    cs = CS()
    clients = await db.get_all_clients_without_role()
    detailed_data = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def process_client(client):
        async with semaphore:
            try:
                page_number = 0
                while True:
                    # Получаем сырой ответ для дебага
                    raw_assets = await cs.get_assets(
                        cardNumber=str(client.user_id),
                        pageNumber=page_number,
                        pageSize=PAGE_SIZE,
                        sortByTimeDescending=True,
                    )

                    # Дебаг-проверка структуры данных
                    if raw_assets and hasattr(raw_assets[0], "amount"):
                        print(f"Пример ассета: {vars(raw_assets[0])}")

                    for asset in raw_assets:
                        detailed_data.append(
                            {
                                "user_id": client.user_id,
                                "Телефон": client.phone_number,
                                "Имя": client.first_name,
                                "Фамилия": client.last_name,
                                "Никнейм": client.username,
                                "Номер карты": asset.cardNumber,
                                "Счёт": asset.accountNumber,
                                "Время операции": asset.time.isoformat(),
                                "Сумма (коп)": asset.amount,
                                "Тип операции": asset.type.value,
                                "Статус": asset.state.value,
                                "Комментарий": asset.additionalInfo.get("comment", ""),
                                "ID операции": asset.sessionId,
                                "Источник": asset.lastSource,
                                "Терминал": asset.terminalId,
                            }
                        )

                    if len(raw_assets) < PAGE_SIZE:
                        break
                    page_number += 1

            except Exception as e:
                print(f"Критическая ошибка: {str(e)}")
                raise

    await asyncio.gather(*[process_client(client) for client in clients])

    # Создание отчёта с валидацией
    df = pd.DataFrame(detailed_data)

    # Проверка заполненности данных
    if df.empty:
        raise ValueError("Отчёт не содержит данных! Проверьте параметры запросов")

    print(f"Статистика:\n{df.describe(include='all')}")

    file_path = "operations_report.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


async def main():
    report_path = await generate_assets_report()
    print(f"Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
