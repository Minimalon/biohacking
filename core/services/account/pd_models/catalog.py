from pydantic import BaseModel

from core.database.model import Clients
from core.utils import texts


class CartItem(BaseModel):
    id: int
    title: str
    code: int
    price: float
    quantity: int
    file_id: str
    text: str
    catalogid: int


class Cart(BaseModel):
    items: list[CartItem]

    async def prepare_text(self) -> str:
        text = texts.information_head
        for i, item in enumerate(self.items, start=1):
            text += f"<b>Товар#️⃣{i}</b>\n"
            text += f"➖<b>Название:</b> {item.title}\n"
            text += f"➖<b>Цена:</b> {item.price}\n"
            text += f"➖<b>Количество:</b> {item.quantity}\n"
        text += f"➖<b>Итоговая сумма:</b> <code>{sum(item.price * item.quantity for item in self.items)}</code>\n\n"
        text += '<blockquote>Ожидайте, в случае необходимости с вами свяжется оператор.</blockquote>'
        return text

    async def compleate_order_text(self, order_id: int, client: Clients) -> str:
        text = f"<b><u>Заказ №</u></b>: <code>{order_id}</code>\n"
        text += texts.information_head
        text += f"➖<b>Имя клиента:</b> <code>{client.first_name}\n</code>"
        text += f"➖<b>Сотовый:</b> +{client.phone_number}\n"
        for i, item in enumerate(self.items, start=1):
            text += f"<b>Товар#️⃣{i}</b>\n"
            text += f"➖<b>Название:</b> <code>{item.title}\n</code>"
            text += f"➖<b>Штрихкод:</b> <code>{item.code}\n</code>"
            text += f"➖<b>Цена:</b> <code>{item.price}\n</code>"
            text += f"➖<b>Количество:</b> <code>{item.quantity}\n</code>"
            text += f"➖<b>Сумма:</b> <code>{item.price * item.quantity}\n</code>"
        text += f"➖<b>Итоговая сумма:</b> <code>{sum(item.price * item.quantity for item in self.items)}</code>\n\n"
        text += '<blockquote>Чтобы поменять статус запроса, нажмите на кнопку ниже.</blockquote>'
        return text
