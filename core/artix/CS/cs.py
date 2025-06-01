import json
from collections import defaultdict
from typing import Union

import aiohttp
from aiohttp import ClientResponse, BasicAuth

import config
from core.artix.CS.pd_model import (
    Client,
    CardBalance,
    CardInfo,
    Asset,
    AssetExtended,
    AssetType,
)
from core.loggers.make_loggers import cs_log


async def log_request(
    method: str, url: str, headers: dict = None, data: str = None
) -> None:
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

    async def _get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        data: str = None,
        auth: BasicAuth = None,
    ) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, headers=headers, auth=auth
            ) as resp:
                await log_request("GET", str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def _post(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        data: str = None,
        auth: BasicAuth = None,
    ) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, params=params, headers=headers, data=data, auth=auth
            ) as resp:
                await log_request("POST", str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def _delete(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        data: str = None,
        auth: BasicAuth = None,
    ) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url, params=params, headers=headers, data=data, auth=auth
            ) as resp:
                await log_request("DELETE", str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def get_clients(self) -> list[Client]:
        url = f"{self.cs_url}/dictionaries/clients"
        return [Client(**client) for client in json.loads(await self._get(url))]

    async def get_client_by_id(self, client_id: str | int) -> Client | None:
        url = f"{self.cs_url}/dictionaries/clients/id/{client_id}"
        resp = await self._get(url)
        if await resp.text():
            return Client.model_validate_json(await resp.text())

    async def get_client_by_params(self, params: dict) -> list[Client]:
        url = f"{self.cs_url}/dictionaries/clients/bypage"
        resp = await self._get(url, params=params)
        return [Client(**client) for client in json.loads(await resp.text())["content"]]

    async def create_client(self, client: Client) -> ClientResponse:
        url = f"{self.cs_url}/dictionaries/clients"
        resp = await self._post(
            url,
            headers={"Content-Type": "application/json"},
            data=client.model_dump_json(exclude_none=True),
        )
        return resp

    async def delete_client(self, user_id: int) -> ClientResponse:
        url = f"{self.cs_url}/dictionaries/clients/id/{user_id}"
        resp = await self._delete(url)
        return resp

    async def get_card_balance(
        self, card_number: Union[int, str]
    ) -> CardBalance | None:
        url = f"{self.acc_url}/cards/{card_number}"
        resp = await self._get(url, auth=BasicAuth(login="_cash_1_0b7357b7"))
        if await resp.text():
            return CardBalance.model_validate_json(await resp.text())

    async def create_card(self, card: CardInfo) -> ClientResponse:
        url = f"{self.cs_url}/dictionaries/cards"
        resp = await self._post(
            url,
            headers={"Content-Type": "application/json"},
            data=card.model_dump_json(exclude_none=True),
        )
        return resp

    async def get_card_by_id(self, card_id: int) -> CardInfo | None:
        url = f"{self.cs_url}/dictionaries/cards/id/{card_id}"
        resp = await self._get(url)
        if await resp.text():
            return CardInfo.model_validate_json(await resp.text())

    async def post_asset(self, asset: Asset) -> ClientResponse:
        url = f"{self.acc_url}/assets"
        resp = await self._post(
            url,
            data=asset.model_dump_json(exclude_none=True),
            auth=BasicAuth(login="_cash_1_fbf2b1ba"),
            headers={"Content-Type": "application/json"},
        )
        return resp

    async def get_assets(
        self,
        cardNumber: str,
        accountNumber: str = None,
        type: AssetType = None,
        withTransactions: bool = None,
        pageNumber: int = None,
        pageSize: int = None,
        sortByTimeDescending: bool = True,
        sortByTimeAscending: bool = None,
    ) -> list[AssetExtended]:
        """
        Получить список операций по карте, максимально 500 записей
        :param sortByTimeAscending: Сортировать по времени в порядке возрастания времени
        :param pageSize: Количество записей в каждой странице
        :param pageNumber: Номер страницы данных, которые нужно отобразить
        :param withTransactions: указывать транзакции
        :param type: Фильтр по типу операций
        :param cardNumber: Номер карты
        :param accountNumber: Номер счёта
        :param sortByTimeDescending: Сортировать по времени в порядке убывания времени
        :return: list[AssetExtended]
        """
        p = defaultdict(dict)
        p["cardNumber"] = cardNumber
        if accountNumber is not None:
            p["accountNumber"] = accountNumber
        elif type is not None:
            p["type"] = type.value
        if withTransactions is not None:
            p["withTransactions"] = 1 if withTransactions else 0
        if pageNumber is not None:
            p["pageNumber"] = pageNumber
        if pageSize is not None:
            p["pageSize"] = pageSize
        if sortByTimeDescending is not None:
            p["sortByTimeDescending"] = 1 if sortByTimeDescending else 0
        if sortByTimeAscending is not None:
            p["sortByTimeAscending"] = 1 if sortByTimeAscending else 0
        url = f"{self.acc_url}/assets"
        resp = await self._get(
            url,
            params=dict(p),
            auth=BasicAuth(login="_cash_1_fbf2b1ba"),
        )
        return [
            AssetExtended.model_validate_json(json.dumps(asset))
            for asset in await resp.json()
        ]
