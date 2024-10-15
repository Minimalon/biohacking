import asyncio
from datetime import datetime
from typing import Union, Type
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine, update, insert, inspect, func
from sqlalchemy.orm import sessionmaker, aliased

import config
from core.artix.cash.model import *
from core.utils import texts


class Artix:
    def __init__(self, ip: str, database: str = 'dictionaries'):
        self.engine = create_engine(config.artixcash_db_cfg.get_url(database, ip))
        self.Session = sessionmaker(bind=self.engine)

    def get_actionpanelitems(self, actionpanelcode: int = 5, context: int = 6, page: int = 2) -> list[
        Actionpanel, Actionpanelitem, Actionparameter]:
        with self.Session() as session:
            actionpanel_alias = aliased(Actionpanel)
            actionpanelitem_alias = aliased(Actionpanelitem)
            actionparameter_alias = aliased(Actionparameter)
            query = (
                session.query(actionpanel_alias, actionpanelitem_alias, actionparameter_alias)
                .join(actionpanelitem_alias, actionpanel_alias.actionpanelcode == actionpanelitem_alias.actionpanelcode)
                .join(actionparameter_alias, actionpanelitem_alias.actioncode == actionparameter_alias.cmactioncode)
                .where(actionpanelitem_alias.actionpanelcode == actionpanelcode,
                       actionpanel_alias.context == context,
                       actionpanel_alias.page == page, )
            )
            return query.all()

    def get_actionpanel_by_context_and_page(self, context: int, page: int) -> Union[Actionpanel, None]:
        with self.Session() as session:
            drbr_panel = (session.query(Actionpanel)
                          .where(Actionpanel.context == context,
                                 Actionpanel.page == page)
                          .first())
            return drbr_panel

    def get_actionPanelItems_draftbeer(self) -> list[Actionpanel, Actionpanelitem, Actionparameter]:
        """
        Все кнопки внутри категории "Пиво", которые имеют actionparameter
        :return:
        """
        current_context, nextpage = None, None
        for actionpanel, actionpanelitem, actionparametr in self.get_actionpanelitems():
            if 'пиво' in actionpanelitem.name.lower() and actionparametr.parametername == 'page':
                nextpage = actionparametr.parametervalue
                current_context = actionpanel.context
                break
        if current_context is None:
            raise ValueError("Не найдена категория <b><u>Пиво</u></b>")

        apanel = self.get_actionpanel_by_context_and_page(current_context, nextpage)
        return self.get_actionpanelitems(
            actionpanelcode=apanel.actionpanelcode,
            context=apanel.context,
            page=apanel.page,
        )

    def get_actionpanelitem(self, actionpanelitemcode: int) -> Union[Actionpanelitem, None]:
        with self.Session() as session:
            q = (session.query(Actionpanelitem)
                 .where(Actionpanelitem.actionpanelitemcode == actionpanelitemcode)
                 .first())
            return q

    def get_actionpanelparameter(self, actioncode: int) -> Union[Actionparameter, None]:
        with self.Session() as session:
            q = (session.query(Actionparameter)
                 .where(Actionparameter.cmactioncode == actioncode)
                 .first())
            return q

    def get_hotkey(self, hotkeycode: int) -> Union[Hotkey, None]:
        with self.Session() as session:
            q = (session.query(Hotkey)
                 .where(Hotkey.hotkeycode == hotkeycode)
                 .first())
            return q

    def get_hotkeyinvents(self, hotkeycode: int) -> Union[list[HotkeyInvent], None]:
        with self.Session() as session:
            q = (session.query(HotkeyInvent)
                 .where(HotkeyInvent.hotkeycode == hotkeycode)
                 .all())
            return q if len(q) > 0 else None

    async def update_name_actionpanelitem(self, name: str, actionpanelitemcode: int):
        with self.Session() as s:
            s.execute(update(Actionpanelitem).where(
                Actionpanelitem.actionpanelitemcode == actionpanelitemcode
            ).values(name=name))
            s.commit()

    async def update_or_add_bcode_hotkeyinvent(self, bcode: str, hotkeycode: int):
        with self.Session() as s:
            invent = (s.query(HotkeyInvent)
                      .where(HotkeyInvent.hotkeycode == hotkeycode)
                      .first())
            if invent is not None:
                s.execute(update(HotkeyInvent).where(
                    HotkeyInvent.hotkeycode == hotkeycode
                ).values(inventcode=bcode))
            else:
                s.execute(insert(HotkeyInvent).values(
                    inventcode=bcode,
                    hotkeycode=hotkeycode,
                ))
            s.commit()

    async def insert_draftbeer_ostatki(self, cis: str, bcode: str, name: str, expirationdate: datetime, volume: float,
                                       connectdate: datetime = None):
        try:
            if connectdate is None:
                connectdate = datetime.now()
            with self.Session() as s:
                already_cis = (s.query(Remaindraftbeer)
                               .where(Remaindraftbeer.markingcode == cis)
                               .first())
                if already_cis is None:
                    s.execute(insert(Remaindraftbeer).values(
                        markingcode=cis,
                        barcode=bcode,
                        name=name,
                        connectdate=connectdate,
                        expirationdate=expirationdate,
                        volume=volume,
                    ))
                # elif already_cis.volume == 0:
                else:
                    s.execute(update(Remaindraftbeer).
                    where(Remaindraftbeer.markingcode == cis)
                    .values(
                        markingcode=cis,
                        barcode=bcode,
                        name=name,
                        connectdate=connectdate,
                        expirationdate=expirationdate,
                        volume=volume,
                    ))
                s.commit()
        except OperationalError:
            raise ConnectionError(texts.error_cashNotOnline)

    async def check_table(self, table_name) -> bool:
        inspector = inspect(self.engine)
        table_exists = table_name in inspector.get_table_names()
        return True if table_exists else False

    async def get_tmc(self, bcode: str) -> Union[TMC, None]:
        with self.Session() as session:
            return session.query(TMC).where(TMC.bcode == bcode).first()

    async def update_tmc(self, **kwargs) -> None:
        with self.Session() as session:
            session.execute(update(TMC).where(TMC.bcode == str(kwargs['bcode']))
                            .values(**kwargs))
            session.commit()

    async def get_barcode(self, bcode: str) -> Union[BARCODES, None]:
        with self.Session() as session:
            return session.query(BARCODES).where(BARCODES.barcode == bcode).first()

    async def update_barcode(self, **kwargs) -> None:
        with self.Session() as session:
            session.execute(update(BARCODES).where(BARCODES.barcode == str(kwargs['barcode']))
                            .values(**kwargs))
            session.commit()

    async def get_units(self) -> list[Type[Units]]:
        with self.Session() as session:
            return session.query(Units).all()

    async def get_unit_by_frunit(self, frunit: int) -> Type[Units] | None:
        with self.Session() as session:
            return session.query(Units).where(Units.frunit == frunit).first()

    async def insert_unit(self, name: str, flag: int, frunit: int) -> None:
        with self.Session() as session:
            session.execute(insert(Units).values(
                name=name,
                flag=flag,
                frunit=frunit,
            ))
            session.commit()

    async def create_mol(self, fio: str) -> int:
        """Возвращает код созданного пользователя"""
        with self.Session() as session:
            max_code = session.query(func.max(MOL.code)).scalar()
            session.execute(insert(MOL).values(
                code=str(int(max_code) + 1),
                login=str(int(max_code) + 1),
                password=str(int(max_code) + 1),
                name=fio,
            ))
            session.execute(insert(RoleUser).values(
                usercode=str(int(max_code) + 1),
            ))
            session.commit()
            return int(max_code) + 1


