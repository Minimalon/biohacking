import enum

from sqlalchemy import String, Column, DateTime, Boolean, Integer, BigInteger, ForeignKey, Enum, Numeric, TypeDecorator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import config
from .base import Base
from .enums.checklists import EnumCheckListContentActions

engine = create_async_engine(config.db_cfg.get_url())

class ClientRolesEnum(enum.Enum):
    CLIENT = 'Клиент'
    EMPLOYEE = 'Сотрудник'
    ADMIN = 'Админ'
    BLOGER = 'Блогер'
    SUPERADMIN = 'СуперАдмин'


class Clients(Base):
    __tablename__ = 'clients'
    date = Column(DateTime(timezone=True), server_default=func.now())
    phone_number = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50))
    user_id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    autologins = relationship(
        "ArtixAutologin",
        back_populates="client",
        cascade="all, delete",
    )
    referrals_sent = relationship(
        "Referrals",
        foreign_keys="[Referrals.user_id]",
        back_populates="client",
        cascade="all, delete",
    )

    referrals_received = relationship(
        "Referrals",
        foreign_keys="[Referrals.ref_id]",
        back_populates="referred_client",
        cascade="all, delete",
    )
    role = relationship(
        "ClientRoles",
        back_populates="client",
        cascade="all, delete",
        uselist=False,
    )
    complete_checklists = relationship(
        "CheckListComplete",
        back_populates="client",
        cascade="all, delete",
    )
    orders = relationship(
        "Orders",
        back_populates="client",
        cascade="all, delete",
        uselist=True,
    )
    help_tickets = relationship(
        "HelpTicket",
        back_populates="client",
        cascade="all, delete",
        uselist=True,
    )
    bonus_awards = relationship(
        "BonusAward",
        back_populates="client",
        cascade="all, delete",
        uselist=True,
    )

class ClientRoles(Base):
    __tablename__ = 'clientroles'
    user_id = Column(BigInteger, ForeignKey('clients.user_id'), nullable=False, primary_key=True)
    rolename = Column(Enum(ClientRolesEnum), default=ClientRolesEnum.CLIENT, nullable=False)
    client = relationship("Clients", back_populates="role")


class ArtixAutologin(Base):
    __tablename__ = 'artix_autologin'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    shopcode = Column(Integer, nullable=False)
    cashcode = Column(Integer, nullable=False)
    user_id = Column(BigInteger, ForeignKey('clients.user_id'), nullable=False)
    inn = Column(String(50), nullable=False)
    client = relationship("Clients", back_populates="autologins")



class Referrals(Base):
    __tablename__ = 'referrals'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete='CASCADE'), nullable=False)
    ref_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete='CASCADE'), nullable=False)

    client = relationship(
        "Clients",
        foreign_keys=[user_id],
        back_populates="referrals_sent",
        passive_deletes=True,
        uselist=False
    )

    referred_client = relationship(
        "Clients",
        foreign_keys=[ref_id],
        back_populates="referrals_received",
        passive_deletes=True,
        uselist=False
    )


class ChecklistMenu(Base):
    __tablename__ = 'checklistmenu'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(50))

    contents = relationship('ChecklistContent', back_populates='menu',
                            uselist=True,
                            cascade="all, delete")


class ChecklistContent(Base):
    __tablename__ = 'checklistcontent'
    id = Column(BigInteger, primary_key=True)
    content = Column(String(50), nullable=False)
    file_id = Column(String(250), nullable=True)
    page = Column(BigInteger, nullable=False)
    checklistmenuid = Column(BigInteger, ForeignKey('checklistmenu.id', ondelete="CASCADE"), nullable=False)

    action = relationship('ChecklistContentAction', back_populates='content',
                          cascade="all, delete-orphan",
                          uselist=False)
    menu = relationship("ChecklistMenu", back_populates="contents", uselist=False)


class ChecklistContentAction(Base):
    __tablename__ = 'checklistcontentaction'
    id = Column(BigInteger, primary_key=True)
    action = Column(Enum(EnumCheckListContentActions), default=EnumCheckListContentActions.NONE, nullable=False)
    checklistcontentid = Column(BigInteger, ForeignKey('checklistcontent.id', ondelete="CASCADE"), nullable=False)

    content = relationship("ChecklistContent", back_populates="action", uselist=False)


class CheckListComplete(Base):
    __tablename__ = 'checklistcomplete'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete="CASCADE"), nullable=False)
    time_answer = Column(DateTime(timezone=True))
    action = Column(Enum(EnumCheckListContentActions), nullable=False)
    file_id = Column(String(250), nullable=True)
    text = Column(String(250), nullable=True)
    checklistmenuid = Column(BigInteger, nullable=False)
    checklistcontentid = Column(BigInteger, nullable=False)

    client = relationship("Clients", back_populates="complete_checklists")


class Catalog(Base):
    __tablename__ = 'catalog'
    id = Column(BigInteger, primary_key=True)
    title = Column(String(50), nullable=False)
    parent_id = Column(BigInteger, ForeignKey('catalog.id'), nullable=True)
    row = Column(Integer, nullable=True)

    tmccatalogs = relationship("TmcCatalog",
                               back_populates="catalog",
                               uselist=True,
                               cascade="all, delete",
                               )


class TmcCatalog(Base):
    __tablename__ = 'tmccatalog'
    id = Column(BigInteger, primary_key=True)
    code = Column(BigInteger, nullable=False)
    title = Column(String(250), nullable=False)
    file_id = Column(String(250), nullable=True)
    text = Column(String(1500), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    catalogid = Column(BigInteger, ForeignKey('catalog.id'), nullable=False)

    catalog = relationship("Catalog",
                           back_populates="tmccatalogs",
                           uselist=False,
                           )


class OrderStatus(Base):
    __tablename__ = 'orderstatus'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    visible = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)

    orders = relationship("Orders", back_populates="status")
class OrderWorks(Base):
    __tablename__ = 'orderworks'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete="CASCADE"), nullable=False)
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete="CASCADE"), nullable=False)
    status_id = Column(BigInteger, ForeignKey('orderstatus.id', ondelete="CASCADE"), nullable=False)

    order = relationship("Orders", back_populates="history")



class Orders(Base):
    __tablename__ = 'orders'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete="CASCADE"), nullable=False)
    status_id = Column(BigInteger, ForeignKey('orderstatus.id', ondelete="CASCADE"), nullable=False)

    status = relationship("OrderStatus", back_populates="orders")
    client = relationship("Clients", back_populates="orders")
    items = relationship("OrdersItems", back_populates="order", cascade="all, delete")
    history = relationship("OrderWorks", back_populates="order", uselist=True)


class OrdersItems(Base):
    __tablename__ = 'ordersitems'
    id = Column(BigInteger, primary_key=True)
    orderid = Column(BigInteger, ForeignKey('orders.id'), nullable=False)
    productid = Column(BigInteger, ForeignKey('tmccatalog.id'), nullable=False)
    catalogid = Column(BigInteger, ForeignKey('catalog.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Orders", back_populates="items")

class HelpTicketStatus(Base):
    __tablename__ = 'helpticketstatus'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    visible = Column(Boolean, default=True, nullable=False)
    default = Column(Boolean, default=False, nullable=False)
    closed = Column(Boolean, default=False, nullable=False)

    tickets = relationship("HelpTicket", back_populates="ticket_status", uselist=True)
    work_tickets = relationship("WorkHelpTicket", back_populates="status", uselist=True)


class WorkHelpTicket(Base):
    __tablename__ = 'workhelpticket'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete="CASCADE"), nullable=False)
    ticket_id = Column(BigInteger, ForeignKey('helptickets.id', ondelete="CASCADE"), nullable=False)
    status_id = Column(BigInteger, ForeignKey('helpticketstatus.id', ondelete="CASCADE"), nullable=False)

    status = relationship("HelpTicketStatus", back_populates="work_tickets", uselist=False)



class HelpTicket(Base):
    __tablename__ = 'helptickets'
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete='CASCADE'), nullable=False)
    msg = Column(String(1024), nullable=True)
    status = Column(BigInteger, ForeignKey('helpticketstatus.id'), nullable=False)

    client = relationship("Clients", back_populates="help_tickets")
    ticket_status = relationship("HelpTicketStatus", back_populates="tickets", uselist=False)

class BonusAward(Base):
    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('clients.user_id', ondelete="CASCADE"), nullable=False)
    award = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)

    client = relationship("Clients", back_populates="bonus_awards")


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
