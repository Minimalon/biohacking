import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Union
from collections import defaultdict

import aiohttp
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile

from aiohttp import ClientResponse, BasicAuth

from core.artix.CS.pd_model import Client, CardBalance, CardInfo, Asset, AssetExtended, AssetType, AwardsType
import config
from core.loggers.make_loggers import cs_log
from core.utils import texts


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
                   auth: BasicAuth = None) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, auth=auth) as resp:
                await log_request('GET', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def _post(self,
                    url: str,
                    params: dict = None,
                    headers: dict = None,
                    data: str = None,
                    auth: BasicAuth = None
                    ) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=headers, data=data, auth=auth) as resp:
                await log_request('POST', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def _delete(self,
                      url: str,
                      params: dict = None,
                      headers: dict = None,
                      data: str = None,
                      auth: BasicAuth = None
                      ) -> ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, params=params, headers=headers, data=data, auth=auth) as resp:
                await log_request('DELETE', str(resp.url), headers=headers, data=data)
                await log_response(resp)
                return resp

    async def get_clients(self) -> list[Client]:
        url = f'{self.cs_url}/dictionaries/clients'
        return [Client(**client) for client in json.loads(await self._get(url))]

    async def get_client_by_id(self, client_id: str | int) -> Client | None:
        url = f'{self.cs_url}/dictionaries/clients/id/{client_id}'
        resp = await self._get(url)
        if await resp.text():
            return Client.model_validate_json(await resp.text())

    async def get_client_by_params(self, params: dict) -> list[Client]:
        url = f'{self.cs_url}/dictionaries/clients/bypage'
        resp = await self._get(url, params=params)
        return [Client(**client) for client in json.loads(await resp.text())['content']]

    async def create_client(self, client: Client) -> ClientResponse:
        url = f'{self.cs_url}/dictionaries/clients'
        resp = await self._post(
            url,
            headers={'Content-Type': 'application/json'},
            data=client.model_dump_json(exclude_none=True)
        )
        return resp

    async def delete_client(self, user_id: int) -> ClientResponse:
        url = f'{self.cs_url}/dictionaries/clients/id/{user_id}'
        resp = await self._delete(url)
        return resp

    async def get_card_balance(self, card_number: Union[int, str]) -> CardBalance | None:
        url = f'{self.acc_url}/cards/{card_number}'
        resp = await self._get(url, auth=BasicAuth(login='_cash_1_0b7357b7'))
        if await resp.text():
            return CardBalance.model_validate_json(await resp.text())

    async def create_card(self, card: CardInfo) -> ClientResponse:
        url = f'{self.cs_url}/dictionaries/cards'
        resp = await self._post(
            url,
            headers={'Content-Type': 'application/json'},
            data=card.model_dump_json(exclude_none=True)
        )
        return resp

    async def get_card_by_id(self, card_id: int) -> CardInfo | None:
        url = f'{self.cs_url}/dictionaries/cards/id/{card_id}'
        resp = await self._get(url)
        if await resp.text():
            return CardInfo.model_validate_json(await resp.text())

    async def post_asset(self, asset: Asset) -> ClientResponse:
        url = f'{self.acc_url}/assets'
        resp = await self._post(
            url,
            data=asset.model_dump_json(exclude_none=True),
            auth=BasicAuth(login='_cash_1_fbf2b1ba'),
            headers={'Content-Type': 'application/json'}
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
    ) -> list[
        AssetExtended]:
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
        p['cardNumber'] = cardNumber
        if accountNumber is not None:
            p['accountNumber'] = accountNumber
        elif type is not None:
            p['type'] = type.value
        if withTransactions is not None:
            p['withTransactions'] = 1 if withTransactions else 0
        if pageNumber is not None:
            p['pageNumber'] = pageNumber
        if pageSize is not None:
            p['pageSize'] = pageSize
        if sortByTimeDescending is not None:
            p['sortByTimeDescending'] = 1 if sortByTimeDescending else 0
        if sortByTimeAscending is not None:
            p['sortByTimeAscending'] = 1 if sortByTimeAscending else 0
        url = f'{self.acc_url}/assets'
        resp = await self._get(
            url,
            params=dict(p),
            auth=BasicAuth(login='_cash_1_fbf2b1ba'),
        )
        return [AssetExtended.model_validate_json(json.dumps(asset)) for asset in await resp.json()]


async def append(bot: Bot):
    users = ['603385647', '388039160', '924922438', '811319960', '428163781', '394596727', '5815624104', '447062998',
             '986863686', '443968576', '5321706310', '1770784850', '1244631522', '726476418', '856469774', '248836879',
             '2070480739', '539369477', '450416964', '1843885562', '1472092643', '762612462', '5196065459', '243957203',
             '5731366934', '388682762', '919470794', '7300522463', '1075878229', '1035355202', '209326571', '242714843',
             '1334675578', '804529505', '593274035', '836502136', '845717047', '6396392644', '743064960', '1843355953',
             '823004386', '6105053287', '768367828', '532327323', '1071211800', '5551692359', '370475345', '1329929220',
             '1199805378', '154421863', '473272589', '1873174575', '540112118', '5267256328', '7662207590', '913281234',
             '1376871141', '829801990', '545342917', '525940449', '711139597', '1047693972', '941347997', '5263751490',
             '854522526', '1233707578', '456186956', '468505807', '386798741', '6132851728', '739627027', '836979817',
             '374674688', '934042263', '1735401006', '869522946', '6517473497', '663144377', '176400022', '1233383368',
             '959220585', '7349176834', '59495467', '5086015856', '347064', '1194135957', '5694925340', '221536412',
             '839016486', '1042392857', '783099943', '547806778', '905998327', '976178771', '1202600019', '901385019',
             '1025061890', '867679204', '643910845', '951987616', '376986939', '314088607', '304152026', '1041379443',
             '5189516540', '506605468', '897941471', '2028615862', '722174255', '889905981', '1082539305', '88948103',
             '5320029087', '1153719765', '933088613', '888700916', '1371688598', '1068414861', '1098975110',
             '396854039', '701466626', '685561134', '6836203261', '1425286299', '6079288733', '343997783', '906670626',
             '259291378', '775307220', '1460350522', '227646654', '118596905', '445661446', '1664941884', '1915210340',
             '1804720336', '250146117', '1558613771', '5013978760', '147990467', '243106074', '863151724', '491602033',
             '774070746', '702817377', '666315625', '744031816', '377883568', '844383343', '718418809', '394108602',
             '1411636573', '758293445', '538041749', '719760785', '892564623', '365105417', '422192164', '721298987',
             '331934216', '6245525622', '254529427', '84009184', '553718569', '781111803', '567460171', '1284714872',
             '890968039', '759979594', '1523726581', '649712285', '1370870887', '816759331', '52675602', '656848510',
             '1075760068', '410607320', '969198876', '616343888', '177385643', '269843754', '923109939', '67315946',
             '532530546', '293040858', '708880276', '326514691', '1348958796', '1746014272', '298438497', '1503797199',
             '349839763', '156987730', '1431221402', '1215569323', '880779748', '656150299', '633824078', '297770994',
             '225307612', '5689013799', '163757102', '1247017384', '1388088931', '1448536499', '1046820914',
             '199988303', '1906962310', '84544698', '6398871389', '5190650025', '6890766957', '1921382130',
             '1279765004', '230050949', '1642246482', '1114234569', '860075389', '1338446952', '339964677',
             '6514392352', '266131407', '5237761025', '5235050718', '305469639', '267864051', '2041507926', '819005477',
             '277951244', '821021159', '1122259853', '7244722107', '551473086', '6683724193', '1942384192',
             '1310626380', '1169121038', '741817182', '5345637333', ]
    cs = CS()
    not_reg = []
    for user in users:
        # balance = await cs.get_card_balance(user)
        assets = await cs.get_assets(user, type=AssetType.ADD)
        amounts = [asset.amount for asset in assets if asset.time.day == datetime.now().day]
        if 10000 in amounts:
            try:
                await bot.send_photo(user,
                                     photo=FSInputFile(Path(config.dir_path, 'files', '8.jpg')),
                                     caption=texts.success_head + f"Вам начислены приветственные 100 рублей за регистрацию.")
                print(f"Вам начислены приветственные 100 рублей за регистрацию.", user)
            except Exception as e:
                print(e)
            # await cs.post_asset(Asset(
            #     cardNumber=user,
            #     amount=100 * 100,
            #     type=AssetType.ADD,
            #     additionalInfo={
            #         'type': AwardsType.REGISTRATION
            #     }
            # ))
            not_reg.append(user)
    print(not_reg)
    print(len(not_reg))


if __name__ == '__main__':
    import asyncio
    bot = Bot(token=config.tg_cfg.TOKEN,
              default=DefaultBotProperties(
                  parse_mode='HTML'
              ))

    asyncio.run(append(bot))
