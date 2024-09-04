from core.services.start.pd_models import Profile

error_head = f"➖➖➖➖🚨ОШИБКА🚨➖➖➖➖\n"
intersum_head = f"➖➖➖➖❗️ВАЖНО❗️➖➖➖➖\n"
information_head = f"➖➖➖ℹ️Информацияℹ️➖➖➖\n"
auth_head = f"➖➖➖🔑Авторизация🔑➖➖➖\n"
success_head = '➖➖➖✅Успешно✅➖➖➖\n'

fake_phone = f'{error_head}Вы отправили чужой сотовой.'
is_develope = 'Данная кнопка находится в разработке'
error_cashNotOnline = error_head + f'Компьютер не в сети. Возможно он выключен, или нет интернета.'
no_access = 'Данная команда вам не доступна'

async def create_user(fio: str, user_code: int, cash_code: int) -> str:
    return (f'{success_head}'
            f'<b>ФИО</b>: <code>{fio}</code>\n'
            f'<b>Пароль</b>: <code>{user_code}</code>\n'
            f'<b>Номер магазина</b>: <code>{cash_code}</code>\n'
            )

async def profile(profile: Profile) -> str:
    return (f'{information_head}'
            f'<b>Номер карты</b>: <code>{profile.cs_card.idcard}</code>\n'
            f'<b>Баланс</b>: <code>{profile.cs_card_balance.balance / 100} руб</code>\n'
            )
