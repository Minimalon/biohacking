from sqlalchemy import text, delete, update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.database.model import Catalog, TmcCatalog, Orders, OrdersItems, OrderStatus, OrderWorks
from core.database.query import Database
from typing import List

from core.services.account.pd_models.catalog import Cart



class CatalogQuery(Database):

    def __init__(self):
        super().__init__()

    async def get_catalogs(self) -> List[Catalog]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Catalog))
            return result.scalars().all()

    async def get_catalog(self, catalog_id: int) -> Catalog | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Catalog).where(Catalog.id == catalog_id))
            return result.scalars().first()

    async def get_catalog_by_parent_id(self, parent_id: int) -> list[Catalog]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(Catalog).where(Catalog.parent_id == parent_id))
            return result.scalars().all()

    async def add_catalog(self, title: str) -> Catalog | None:
        async with self.AsyncSession() as session:
            catalog = Catalog(title=title)
            session.add(catalog)
            await session.commit()
            await session.refresh(catalog)
            return catalog

    async def add_tmccatalog(self, code: int, name: str, file_id: str, text: str, price: float,
                             catalogid: int) -> TmcCatalog:
        async with self.AsyncSession() as session:
            tmc = TmcCatalog(code=code, title=name, file_id=file_id, text=text, price=price, catalogid=catalogid)
            session.add(tmc)
            await session.commit()
            await session.refresh(tmc)
            return tmc

    async def delete_catalog(self, catalog_id: int):
        async with self.AsyncSession() as session:
            await session.execute(delete(Catalog).where(Catalog.id == catalog_id))
            await session.commit()

    async def get_tmccatalogs(self) -> List[TmcCatalog]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(TmcCatalog))
            return result.scalars().all()

    async def get_tmccatalogs_by_catalogid(self, catalogid: int) -> List[TmcCatalog]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(TmcCatalog).where(TmcCatalog.catalogid == catalogid))
            return result.scalars().all()

    async def get_tmccatalog(self, id: int) -> TmcCatalog | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(TmcCatalog).where(TmcCatalog.id == id))
            return result.scalars().first()

    async def delete_tmccatalog(self, product_id: int):
        async with self.AsyncSession() as session:
            await session.execute(delete(TmcCatalog).where(TmcCatalog.id == product_id))
            await session.commit()

    async def update_tmccatalog_price(self, product_id: int, price: float):
        async with self.AsyncSession() as session:
            await session.execute(update(TmcCatalog).where(TmcCatalog.id == product_id).values(price=price))
            await session.commit()

    async def update_tmccatalog_code(self, product_id: int, code: int):
        async with self.AsyncSession() as session:
            await session.execute(update(TmcCatalog).where(TmcCatalog.id == product_id).values(code=code))
            await session.commit()

    async def update_tmccatalog_text_and_fileid(self, product_id: int, text: str, file_id: str):
        async with self.AsyncSession() as session:
            await session.execute(
                update(TmcCatalog).where(TmcCatalog.id == product_id).values(text=text, file_id=file_id))
            await session.commit()

    async def update_tmccatalog_title(self, product_id: int, title: str):
        async with self.AsyncSession() as session:
            await session.execute(update(TmcCatalog).where(TmcCatalog.id == product_id).values(title=title))
            await session.commit()

    async def create_order(self, user_id: int, cart: Cart) -> Orders:
        async with self.AsyncSession() as session:
            default_status = await self.get_order_default_status()
            order = Orders(
                user_id=user_id,
                status_id=default_status.id,
            )
            session.add(order)
            await session.commit()
            for item in cart.items:
                session.add(
                    OrdersItems(
                        orderid=order.id,
                        productid=item.id,
                        catalogid=item.catalogid,
                        quantity=item.quantity,
                    )
                )
            await session.commit()
            return order

    async def get_order(self, order_id: int) -> Orders | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(Orders)
                .options(
                    joinedload(Orders.status),
                )
                .where(Orders.id == order_id))
            return result.scalars().first()

    async def get_order_status(self, status_id: int) -> OrderStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(OrderStatus).where(OrderStatus.id == status_id))
            return result.scalars().first()

    async def get_order_items(self, order_id: int) -> List[OrdersItems]:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(OrdersItems)
                .where(OrdersItems.orderid == order_id)
                .join(TmcCatalog, TmcCatalog.id == OrdersItems.productid)
            )
            return result.scalars().all()

    async def get_order_default_status(self) -> OrderStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(OrderStatus).where(OrderStatus.is_default == True))
            return result.scalars().first()

    async def get_order_closed_status(self) -> OrderStatus | None:
        async with self.AsyncSession() as session:
            result = await session.execute(select(OrderStatus).where(OrderStatus.is_closed == True))
            return result.scalars().first()

    async def get_visible_orders_status(self) -> List[OrderStatus]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(OrderStatus).where(OrderStatus.visible == True))
            return result.scalars().all()

    async def get_history_order(self, order_id: int) -> OrderWorks | None:
        async with self.AsyncSession() as session:
            result = await session.execute(
                select(OrderWorks)
                .where(OrderWorks.order_id == order_id))
            return result.scalars().first()

    async def get_open_orders_by_user(self, user_id: int) -> List[OrderWorks]:
        async with self.AsyncSession() as session:
            closed_status = await self.get_order_closed_status()
            result = await session.execute(
                select(OrderWorks)
                .where(OrderWorks.user_id == user_id)
                .where(OrderWorks.status_id != closed_status.id)
            )
            return result.scalars().all()

    async def get_current_orders_by_user(self, user_id: int) -> List[Orders]:
        async with self.AsyncSession() as session:
            closed_status = await self.get_order_closed_status()
            result = await session.execute(
                select(Orders)
                .where(Orders.user_id == user_id)
                .where(Orders.status_id != closed_status.id)
            )
            return result.scalars().all()

    async def create_history_order(self, order_id: int, status_id: int, user_id: int) -> OrderWorks:
        async with self.AsyncSession() as session:
            history_order = OrderWorks(
                order_id=order_id,
                status_id=status_id,
                user_id=user_id,
            )
            session.add(history_order)
            await session.commit()
            return history_order

    async def update_order_status(self, order_id: int, status_id: int) -> None:
        async with self.AsyncSession() as session:
            await session.execute(update(OrderWorks).where(OrderWorks.order_id == order_id).values(status_id=status_id))
            await session.execute(update(Orders).where(Orders.id == order_id).values(status_id=status_id))
            await session.commit()
