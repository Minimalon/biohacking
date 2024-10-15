import asyncio
import json
import aiohttp
from aiohttp import ClientResponse, BasicAuth
import config

from core.loggers.make_loggers import foreman_log
from core.artix.foreman.pd_model import ForemanCash


async def log_request(method: str, url: str, headers: dict = None, data: str = None) -> None:
    log = foreman_log.bind(url=url, headers=headers, data=data)
    log.info(f"{method} {url}")


async def log_response(response: ClientResponse) -> None:
    log = foreman_log.bind(status_code=response.status, url=response.url)
    if response.ok:
        log.success(response.text)
    else:
        log.error(response.text)


class Foreman:
    def __init__(self, version_ubuntu=18):
        self.version_ubuntu = version_ubuntu
        if version_ubuntu == 18:
            self.base_url = config.foreman_cfg.URL_18
            self.username = config.foreman_cfg.USERNAME_18
            self.password = config.foreman_cfg.PASSWORD_18
        else:
            self.base_url = config.foreman_cfg.URL_14
            self.username = config.foreman_cfg.USERNAME_14
            self.password = config.foreman_cfg.PASSWORD_14
        self.auth = BasicAuth(self.username, self.password)
        # Отключение предупреждений о проверке SSL, использовать с осторожностью

    async def _get(self, url: str, params: dict = None, headers: dict = None, data: str = None) -> dict:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False)) as session:
            async with session.get(url, params=params, headers=headers, auth=self.auth) as resp:
                if resp.status != 200:
                    raise Exception(f"Ошибка запроса: {resp.status}\n {await resp.text()}")
                await log_request('GET', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return await resp.json()

    async def get_architectures(self):
        """Получить список архитектур."""
        url = f"{self.base_url}/api/architectures"
        return await self._get(url)

    async def get_hosts(self, search: str = 'cash-', order: str = 'last_report DESC') -> dict:
        """Получить список хостов"""
        url = f"{self.base_url}/api/hosts"
        per_page = 5000 if self.version_ubuntu == 14 else 'all'
        params = {'per_page': per_page, 'search': search, 'order': order}
        return await self._get(url, params)

    async def get_host_facts(self, host_id: int):
        """Получить факты хоста"""
        url = f"{self.base_url}/api/hosts/{host_id}/facts"
        return await self._get(url, params={'per_page': '10000'})


async def get_cash(cash_number: str) -> ForemanCash:
    foreman = Foreman(18)
    hosts = await foreman.get_hosts(search=cash_number)
    if hosts['subtotal'] == 0:
        foreman = Foreman(14)
        hosts = await foreman.get_hosts(search=cash_number)
        if hosts['subtotal'] == 0:
            raise ValueError(f"Не удалось найти кассу с номером \"{cash_number}\"")

    facts = (await foreman.get_host_facts(hosts['results'][0]['id']))['results']
    for name, value in facts.items():
        return ForemanCash.model_validate_json(json.dumps(value))


async def get_cashes(search: str) -> list[ForemanCash]:
    foreman = Foreman(18)
    hosts = await foreman.get_hosts(search=search)
    if hosts['subtotal'] == 0:
        foreman = Foreman(14)
        hosts = await foreman.get_hosts(search=search)
        if hosts['subtotal'] == 0:
            raise ValueError(f"Не удалось найти кассу \"{search}\"")

    facts = (await foreman.get_host_facts(hosts['results'][0]['id']))['results']
    return [ForemanCash.model_validate_json(json.dumps(value))
            for name, value in facts.items()]


async def get_info_from_all_cashes(only_saman: bool = False,
                                   only_premier: bool = False,
                                   only_rossich: bool = False,
                                   ) -> list[dict]:
    cashes = []
    for f_ver in [18, 14]:
        foreman = Foreman(f_ver)
        hosts = await foreman.get_hosts()
        for host in hosts['results']:
            facts = (await foreman.get_host_facts(host['id']))['results']
            for name, value in facts.items():
                cash = ForemanCash.model_validate_json(json.dumps(value))

                if only_saman and not cash.inn in ['1660349657', '1644096180', '1660347201', '1660346991',
                                                   '1660340005', '1657253779', '1660343863', '1660349488',
                                                   '1660344472', ]:
                    break
                if only_premier and not cash.inn in ['1659208718', '1659208820', '1644096744', '1659208740',
                                                     '1659208757', '1659208845', '1659208838', ]:
                    break
                if only_rossich and not cash.inn in ['1656092053', '1651095981', '1658227108', '1658228253',
                                                     '1650388488', '1656113000', ]:
                    break

                if cash.ip() in [f.ip() for f in cashes]:
                    break

                cash.os_name = 'Обновлен' if cash.os_name == 'bionic' else "Не обновлен"
                cashes.append(cash)
    return [c.__dict__ for c in cashes]
