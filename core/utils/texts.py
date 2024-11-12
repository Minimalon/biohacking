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
awards_head = '➖➖➖💰Начисления💰➖➖➖\n'

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
    return (f'➖➖ℹ️ QR КОД ℹ️➖➖\n\n'
            f'<b>Номер карты</b>: <code>{profile.cs_card.idcard}</code>\n'
            f'<b>Баланс</b>: <code>{profile.cs_card_balance.balance / 100} руб</code>\n\n\n'
            f'➖➖ℹ️ УСЛОВИЯ ℹ️➖➖\n'
            f'С каждой покупки копятся Баллы, которые экономят бюджет и при этом являются максимально выгодными и честными.\n\n'
            f'Условия получения Баллов:\n'
            f'<b><u>До</u></b> 5.000 руб. - накопление 3%\n'
            f'От 5.000 руб. - накопление 5%\n'
            f'От 12.000 рублей - накопление 7%\n'
            f'От 20.000 рублей - накоплен. 10%\n'
            f'От 50.000 рублей - накоплен. 12% \n'
            f'От 100.000 рублей - накоплен. 15%\n\n'
            f'Баллы приходят на следующий день после регистрации в Боте.\n\n'
            f'Баллы реализуются на 30% на всю продукцию и на 100% на все коктейли в «НейроБаре».\n\n'
            f'Так же за Баллы в будущем, готовьтесь получать подарки, либо покупать курсы экспертов или консультации специалистов Биохакинга! 👍'
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
        f'Обязательно подпишись на наш Telegram: https://t.me/bogonaft\n\n'
        f'Ну что начнем?\n'
        f'Выберите категорию ⬇️'
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


async def energy_awards() -> str:
    return (
        f'ПОЗДРАВЛЯЕМ! 🥳\n\n'
        f'Твой первый подарок - это 100 бонусов, которые ты можешь использовать завтра на 100% в нашем Нейробаре! Забери свой подарочный кислородный коктейль! 👍\n\n'
        f'Твой второй подарок - это авторский Гайд «ЭНЕРГОУТРО» от идеолога компаний Миннебаева Равиля Расиховича. 🤩\n\n'
        f'Благодаря данному Гайду - ты подымешь эффективность в несколько раз и «Хакнешь» свою жизнь на Новый Уровень! \n\n'
        f'Приятной практики.\n'
        f'Жди ещё новых подарков! 🎁\n\n'
        f'<i>«Раскрой свой потенциал!»</i>'
    )

async def referals_program() -> str:
    return (
        f'Рекомендуй нас друзьям и получай дополнительные Бонусы до 13% накоплений с их покупок!\n\n'
        f'<b><u>Условие получения Бонусов: </u></b>\n\n'
        f'1 линия - 5% накоплений\n'
        f'2 линия - 3% накоплений\n'
        f'3 линия - 2% накоплений\n'
        f'4 линия - 1% накоплений\n'
        f'5 линия - 0,5% накоплений\n'
        f'6 линия - 0,5% накоплени\n'
        f'7 линия - 0,5% накоплений\n'
        f'8 линия - 0,5% накоплений\n'
        f'9 линия - 0,5% накоплений\n'
        f'10 линия - 0,5% накоплений\n\n'
        f'Бонусы приходят на следующий день, после совершения покупки другом.\n'
        f'Бонусы реализуются на 30% на всю продукцию и на 100% на все коктейли в «НейроБаре».\n\n'
        f'❗️На специальных условиях для Агентов и Блогеров можно вывести Бонусы в реальные деньги💰'
    )