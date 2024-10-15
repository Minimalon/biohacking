import asyncio
import json
from typing import Union

import aiohttp

from aiohttp import ClientResponse, BasicAuth

from core.artix.CS.pd_model import Client, CardBalance, CardInfo
import config
from core.loggers.make_loggers import cs_log


async def log_request(method: str, url: str, headers: dict = None, data: str = None) -> None:
    log = cs_log.bind(url=url, headers=headers, data=data)
    log.info(f"{method} {url}")


async def log_response(response: ClientResponse) -> None:
    log = cs_log.bind(status_code=response.status, url=response.url)
    log.info(str(response.url))
    if response.ok:
        log.success(await response.text())
    else:
        log.error(await response.text())


class CS:
    def __init__(self):
        self.cfg = config.CashServerConfig()
        self.cs_url = self.cfg.cs_url()
        self.acc_url = self.cfg.acc_url()

    async def _get(self,
                   url: str,
                   params: dict = None,
                   headers: dict = None,
                   data: str = None,
                   auth: BasicAuth = None) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, auth=auth) as resp:
                await log_request('GET', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return await resp.text()

    async def _post(self, url: str, params: dict = None, headers: dict = None, data: str = None) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=headers, data=data) as resp:
                await log_request('POST', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return await resp.text()

    async def get_clients(self) -> list[Client]:
        url = f'{self.cs_url}/dictionaries/clients'
        return [Client(**client) for client in json.loads(await self._get(url))]

    async def get_client_by_id(self, client_id: str | int) -> Client | None:
        url = f'{self.cs_url}/dictionaries/clients/id/{client_id}'
        resp = await self._get(url)
        if resp:
            return Client.model_validate_json(resp)

    async def get_client_by_params(self, params: dict) -> list[Client]:
        url = f'{self.cs_url}/dictionaries/clients/bypage'
        return [Client(**client) for client in json.loads(await self._get(url, params=params))['content']]

    async def create_client(self, client: Client):
        url = f'{self.cs_url}/dictionaries/clients'
        return await self._post(
            url,
            headers={'Content-Type': 'application/json'},
            data=client.model_dump_json(exclude_none=True)
        )

    async def get_card_balance(self, card_number: Union[int, str]) -> CardBalance | None:
        url = f'{self.acc_url}/cards/{card_number}'
        resp = await self._get(url, auth=BasicAuth(login='_cash_1_0b7357b7'))
        if resp:
            return CardBalance.model_validate_json(resp)

    async def create_card(self, card: CardInfo) -> str:
        url = f'{self.cs_url}/dictionaries/cards'
        return await self._post(
            url,
            headers={'Content-Type': 'application/json'},
            data=card.model_dump_json(exclude_none=True)
        )

    async def get_card_by_id(self, card_id: int) -> CardInfo | None:
        url = f'{self.cs_url}/dictionaries/cards/id/{card_id}'
        resp = await self._get(url)
        if resp:
            return CardInfo.model_validate_json(resp)

