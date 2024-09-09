import asyncio
import enum

from sqlalchemy import String, Column, DateTime, Boolean, Integer, BigInteger, ForeignKey, Enum
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

import config
from core.database.enums.checklists import EnumCheckListContentActions

engine = create_async_engine(config.db_cfg.get_url())
Base = declarative_base()


def admins():
    return [ClientRolesEnum.SUPERADMIN, ClientRolesEnum.ADMIN]


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
        cascade="delete, delete-orphan",
    )
    referrals = relationship(
        "Referrals",
        foreign_keys="[Referrals.user_id]",
        back_populates="client",
        cascade="delete, delete-orphan",
    )
    referred_by = relationship(
        "Referrals",
        foreign_keys="[Referrals.ref_id]",
        back_populates="referrer",
        uselist=False,
    )
    role = relationship(
        "ClientRoles",
        back_populates="client",
        cascade="delete, delete-orphan",
        uselist=False,
    )


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
    user_id = Column(BigInteger, ForeignKey('clients.user_id'), nullable=False)
    ref_id = Column(BigInteger, ForeignKey('clients.user_id'), nullable=False)
    client = relationship("Clients", foreign_keys=[user_id], back_populates="referrals")
    referrer = relationship("Clients", foreign_keys=[ref_id], back_populates="referred_by")


class ClientRoles(Base):
    __tablename__ = 'clientroles'
    user_id = Column(BigInteger, ForeignKey('clients.user_id'), nullable=False, primary_key=True)
    rolename = Column(Enum(ClientRolesEnum), default=ClientRolesEnum.CLIENT, nullable=False)
    client = relationship("Clients", back_populates="role")


class ChecklistMenu(Base):
    __tablename__ = 'checklistmenu'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(50))

    contents = relationship('ChecklistContent', back_populates='menu',
                            uselist=True,
                            cascade="delete, delete-orphan")


class ChecklistContent(Base):
    __tablename__ = 'checklistcontent'
    id = Column(BigInteger, primary_key=True)
    content = Column(String(50), nullable=False)
    photo_path = Column(String(50), nullable=True)
    page = Column(BigInteger, nullable=False)
    checklistmenuid = Column(BigInteger, ForeignKey('checklistmenu.id'), nullable=False)

    action = relationship('ChecklistContentAction', back_populates='content',
                          cascade="delete, delete-orphan",
                          uselist=False)
    menu = relationship("ChecklistMenu", back_populates="contents", uselist=False)


class ChecklistContentAction(Base):
    __tablename__ = 'checklistcontentaction'
    id = Column(BigInteger, primary_key=True)
    action = Column(Enum(EnumCheckListContentActions), default=EnumCheckListContentActions.NONE, nullable=False)
    checklistcontentid = Column(BigInteger, ForeignKey('checklistcontent.id'), nullable=False)

    content = relationship("ChecklistContent", back_populates="action", uselist=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
