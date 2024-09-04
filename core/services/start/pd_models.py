from pydantic import BaseModel, Field

from core.artix.CS.pd_model import Client, CardInfo, CardBalance


class Profile(BaseModel):
    cs_client: Client | None
    cs_card: CardInfo | None
    cs_card_balance: CardBalance | None