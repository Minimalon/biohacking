from sqlalchemy import String, Column, Boolean, BigInteger, Integer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from core.settings import config


engine = create_async_engine(f"postgresql+asyncpg://{config.db_user}:{config.db_password}@{config.ip}:{config.port}/{config.database}")
Base = declarative_base()


class CashInfo(Base):
    __tablename__ = 'cash_info'

    id = Column(BigInteger, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(255), nullable=False)
    kpp = Column(String(255), nullable=False)
    fsrar = Column(String(255))
    fsrar2 = Column(String(255))
    address = Column(String(255), nullable=False)
    ooo_name = Column(String(255))
    ip_name = Column(String(255))
    ip_inn = Column(String(255))
    ip = Column(String(255))
    touch_panel = Column(Boolean(), default=False)


class Shippers(Base):
    __tablename__ = 'shippers'
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False, )
    inn = Column(String(255), nullable=False)
    fsrar = Column(String(255), nullable=False)


Base.metadata.create_all(engine)
