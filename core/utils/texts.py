from core.database.catalog_query import CatalogQuery
from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ChecklistContent, CheckListComplete, TmcCatalog, Clients, HelpTicket, OrdersItems, \
    Orders
from core.database.query import Database
from core.services.start.pd_models.profile_bonuses import Profile

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


async def history_complete_question(content: ChecklistContent) -> str:
    return (
        f'Страница: #️⃣<code>{content.page}</code>\n'
        f'➖➖➖❓<b><u>ВОПРОС</u></b>❓➖➖➖\n\n'
        f'{content.content}\n'
    )


async def user_info(client: Clients) -> str:
    full_name = f'{client.first_name} {client.last_name}' if client.last_name else client.first_name
    return (f'{information_head}'
            f'Имя: <code>{full_name}</code>\n'
            f'Номер телефона: +{client.phone_number}\n'
            )


async def history_complete_answer(cl: CheckListComplete, content: ChecklistContent) -> str:
    if cl.action == EnumCheckListContentActions.NONE:
        return (
            f'Страница: #️⃣<code>{content.page}</code>\n'
            f'➖➖➖❗️<b><u>ОТВЕТ</u></b>❗️➖➖➖\n'
            f'✅\n'
        )
    else:
        return (
            f'Страница: #️⃣<code>{content.page}</code>\n'
            f'➖➖➖❗️<b><u>ОТВЕТ</u></b>❗️➖➖➖\n\n'
            f'{cl.text}\n'
        )


async def account(first_name: str) -> str:
    return (
        f'Здравствуйте, {first_name}!\n\n'
        f'Я могу узнать баланс бонусных баллов, покажу статус выполнения заказа и решу проблемы с заказом.\n\n'
        f'Если потребудется, можно задать вопрос нашим специалистам.\n\n'
        f'С чего начнем?'
    )


async def product_info(product: TmcCatalog) -> str:
    text = (
        f'{information_head}'
        f'<b>Название:</b> <code>{product.title}</code>\n'
        f'<b>Штрихкод:</b> <code>{product.code}</code>\n'
        f'<b>Цена:</b> <code>{product.price}</code>\n'
        f'➖➖➖➖➖➖➖➖➖\n'
        f'{product.text}'
    )
    return text


async def help_ticket_help(ticket: HelpTicket, client: Clients) -> str:
    full_name = f'{client.first_name} {client.last_name}' if client.last_name else client.first_name
    return (
        f'➖➖➖ℹ️Клиентℹ️➖➖➖\n'
        f'<b>Имя:</b> <code>{full_name}</code>\n'
        f'<b>Номер телефона:</b> +{client.phone_number}\n'
        f'➖➖➖ℹ️Заякаℹ️➖➖➖\n'
        f'<b>Номер заявки:</b> <code>{ticket.id}</code>\n'
        f'<b>Статус:</b> <code>{ticket.ticket_status.name}</code>\n'
        f'<b>Дата создания:</b> <code>{ticket.date.strftime("%d.%m.%Y %H:%M:%S")}</code>\n'
    )


async def order_work(order: Orders, client: Clients, order_items: list[OrdersItems]) -> str:
    full_name = f'{client.first_name} {client.last_name}' if client.last_name else client.first_name
    text = (
        f'➖➖➖ℹ️Клиентℹ️➖➖➖\n'
        f'<b>Имя:</b> <code>{full_name}</code>\n'
        f'<b>Номер телефона:</b> +{client.phone_number}\n'
        f'➖➖➖ℹ️Заказℹ️➖➖➖\n'
        f'<b>Номер Заказ:</b> <code>{order.id}</code>\n'
        f'<b>Статус:</b> <code>{order.status.name}</code>\n'
        f'<b>Дата создания:</b> <code>{order.date.strftime("%d.%m.%Y %H:%M:%S")}</code>\n'
        f'➖➖➖ℹ️Составℹ️➖➖➖\n'
    )
    db = CatalogQuery()
    for item in order_items:
        product = await db.get_tmccatalog(item.productid)
        catalog = await db.get_catalog(product.catalogid)
        text += (
            f'<b>Название:</b> <code>{product.title}</code>\n'
            f'<b>Цена:</b> <code>{product.price}</code>\n'
            f'<b>Количество:</b> <code>{item.quantity}</code>\n'
            f'<b>Каталог:</b> <code>{catalog.title}</code>\n'
            f'➖➖➖➖➖➖➖➖➖\n'
        )
    return text
async def current_user_order(order: Orders, order_items: list[OrdersItems]) -> str:
    text = (
        f'➖➖➖ℹ️Заказℹ️➖➖➖\n'
        f'<b>Номер Заказ:</b> <code>{order.id}</code>\n'
        f'<b>Статус:</b> <code>{order.status.name}</code>\n'
        f'<b>Дата создания:</b> <code>{order.date.strftime("%d.%m.%Y %H:%M:%S")}</code>\n'
        f'➖➖➖ℹ️Составℹ️➖➖➖\n'
    )
    db = CatalogQuery()
    for item in order_items:
        product = await db.get_tmccatalog(item.productid)
        catalog = await db.get_catalog(product.catalogid)
        text += (
            f'<b>Название:</b> <code>{product.title}</code>\n'
            f'<b>Цена:</b> <code>{product.price}</code>\n'
            f'<b>Количество:</b> <code>{item.quantity}</code>\n'
            f'<b>Каталог:</b> <code>{catalog.title}</code>\n'
            f'➖➖➖➖➖➖➖➖➖\n'
        )
    return text


if __name__ == '__main__':
    print(801 // 800 + 1)
