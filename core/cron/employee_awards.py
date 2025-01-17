from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

import config
from core.artix.CS.cs import CS
from core.artix.CS.pd_model import Asset, AssetType, AwardsType
from core.database.award_query import AwardQuery
from core.database.model import ClientRolesEnum
from core.database.query import Database

db = Database()
bot = Bot(token=config.tg_cfg.TOKEN,
          default=DefaultBotProperties(
              parse_mode='HTML'
          ))
aq = AwardQuery()
cs = CS()

# async def employee_awards() -> None:
#
#     employes = await db.get_client_by_role(ClientRolesEnum.EMPLOYEE)
#
#     for employee in employes:
#         response = await cs.post_asset(Asset(
#             cardNumber=employee.user_id,
#             amount=3000 * 100,
#             type=AssetType.ADD,
#             additionalInfo={
#                 'type': AwardsType.REGISTRATION
#             }
#         ))
#         if response.ok:
#             await aq.set_reg_sended(award.id)
#             msg = (
#                 f'{texts.success_head}'
#                 f'Благодарим за вчерашнюю покупку!\n'
#                 f'Сегодня вам пришли подарочные {award.amount / 100} баллов. Используйте их на кислородные коктейли в НейроБаре со 100% скидкой.\n'
#                 f'С нетерпением ждём вашего визита!'
#             )
#             await bot.send_photo(award.user_id,
#                                  photo=FSInputFile(Path(config.dir_path, 'files', '9.jpg')),
#                                  caption=msg)