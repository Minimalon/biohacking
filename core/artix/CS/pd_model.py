import enum
from datetime import datetime
from typing import Union, Dict, List
from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator


class AwardsType(enum.Enum):
    REGISTRATION = "Регистрация в боте"
    REFERAL_SYSTEM = "Реферальная система"


class AssetType(enum.Enum):
    PAY = "PAY"  # оплата
    BACK = "BACK"  # Возврат клиенту (возврат денежных средств)
    ADD = "ADD"  # зачисление
    SUB = "SUB"  # списание
    FIRED = "FIRED"  # сгорание


class AssetState(enum.Enum):
    NON_CONFIRMED = 'NON_CONFIRMED'  # транзакция начата
    COMMITED = 'COMMITED'  # транзакция подтверждена
    CANCELLED = 'CANCELLED'  # транзакция отменена


class Client(BaseModel):
    idclient: Union[str, int] = Field('', title='Идентификатор клиента')
    name: str = Field('', title='ФИО')
    text: str | None = Field(None, title='Текст')
    sex: int | None = Field(None, title='0 - мужской, 1 - женский')
    birthday: datetime | None = Field(None, title='Дата рождения')
    specialdate1name: str | None = Field(None, title='Название даты 1')
    specialdate2name: str | None = Field(None, title='Название даты 2')
    specialdate3name: str | None = Field(None, title='Название даты 3')
    zipcode: str | None = Field(None, title='Почтовый индекс')
    address: str | None = Field(None, title='Адрес')
    email: str | None = Field(None, title='Электронная почта')
    webpage: str | None = Field(None, title='Сайт')
    phonenumber: str = Field(None, title='Номер телефона')
    inn: str | None = Field(None, title='ИНН')
    document: str | None = Field(None, title='Документ')
    okpo: str | None = Field(None, title='ОКПО')
    okpd: str | None = Field(None, title='ОКПД')
    occupation: str | None = Field(None, title='Профессия')
    extendedoptions: str | None = Field(None, title='Расширенные параметры')
    codeword: str | None = Field(None, title='Кодовое слово')
    organizationcode: str | None = Field(None, title='Код организации')
    subscriptionadj: int | None = Field(None, title='Поиск по согласию на рассылку	0 - нет, 1 - да')


class CardBalance(BaseModel):
    number: str | int = Field('', title='Номер карты')
    accountNumber: str | int = Field('', title='Номер счета')
    status: str = Field('', title='Статус карты')
    balance: int = Field(0, title='Баланс')
    balanceInactive: int = Field(0)


class CardInfo(BaseModel):
    idcard: int | str = Field('', title='Идентификатор карты')
    idcardgroup: int = Field(2, title='Идентификатор группы карт')
    idclient: int | str = Field('', title='Идентификатор клиента')
    number: int | str = Field('', title='Номер карты')
    blocked: int = Field(0, title='Заблокирована')


class Asset(BaseModel):
    """
    Данные об операции
    """

    amount: int = Field(..., description="Сумма в копейках")
    cardNumber: str = Field(..., description="Номер карты")
    sessionId: Union[str] = Field(description="Уникальный идентификатор операции", default_factory=uuid4)
    acceptId: Union[str, None] = Field(
        None,
        description="Идентификатор, по которому устанавливались временные ограничения действия бонусов",
    )
    acceptWeight: Union[int, None] = Field(
        None,
        description="Число, указывающее порядок применения начислений данной транзакции - операции с большим числом будут иметь приоритет при операциях списывания",
    )
    additionalInfo: Dict[str, str] = Field(
        {'comment': ''},
        description="Дополнительная информация об операции, полезна для анализа",
    )
    timeBeginAccept: Union[datetime, None] = Field(
        None,
        description="Время начала действия операции",
        example="2019-04-23T22:22:44.134+0700",
    )
    timeEndAccept: Union[datetime, None] = Field(
        None,
        description="Время окончания действия операции",
        example="2019-04-23T22:22:44.134+0700",
    )
    timeFromCash: Union[datetime, None] = Field(
        None,
        description="Время поступления средств в кассу",
        example="2019-04-23T22:22:44.134+0700",
    )
    type: AssetType = Field(..., description="Тип операции")

    @field_validator("cardNumber", mode='before')
    def transform_int_to_str(cls, value) -> str:
        return str(value)

    @field_validator("amount", mode='before')
    def transform_to_intr(cls, value) -> int:
        return int(value)


class AssetTransaction(BaseModel):
    state: AssetState = Field(..., description="Статус операции")
    terminalId: Union[str, None] = Field(None, description="Идентификатор терминала")
    time: datetime = Field(..., description="Время операции")
    transactionReason: Union[str, None] = Field(None, description="Причина операции")
    transactionSource: Union[str, None] = Field(None, description="Источник операции")


class AssetExtended(BaseModel):
    """Данные об операции"""
    acceptId: Union[str, None] = Field(
        None,
        description="Идентификатор, по которому устанавливались временные ограничения действия бонусов",
    )
    acceptWeight: Union[int, None] = Field(
        None,
        description="Число, указывающее порядок применения начислений данной транзакции - операции с большим числом будут иметь приоритет при операциях списывания",
    )
    additionalInfo: Dict[str, str] = Field(
        {'comment': ''},
        description="Дополнительная информация об операции, полезна для анализа",
    )
    accountNumber: str = Field(
        ...,
        description="Номер счета"
    )
    amount: int = Field(
        ...,
        description="Сумма в копейках",
    )
    assetTransactions: Union[List[AssetTransaction], List] = Field(
        [],
        description="Список операций",
    )
    cardNumber: str = Field(
        ...,
        description="Номер карты",
    )
    lastReason: Union[str, None] = Field(
        None,
        description="Последняя причина операции",
    )
    lastSource: Union[str, None] = Field(
        None,
        description="Последний источник операции",
    )
    sessionId: Union[str] = Field(
        description="Уникальный идентификатор операции",
    )
    state: AssetState = Field(
        ...,
        description="Статус операции",
    )
    terminalId: Union[str, None] = Field(
        None,
        description="Идентификатор терминала",
    )
    time: datetime = Field(
        ...,
        description="Время операции",
    )
    timeBeginAccept: Union[datetime, None] = Field(
        None,
        description="Время начала действия операции",
        example="2019-04-23T22:22:44.134+0700",
    )
    timeEndAccept: Union[datetime, None] = Field(
        None,
        description="Время окончания действия операции",
        example="2019-04-23T22:22:44.134+0700",
    )
    timeFromCash: Union[datetime, None] = Field(
        None,
        description="Время поступления средств в кассу",
        example="2019-04-23T22:22:44.134+0700",
    )
    type: AssetType = Field(
        ...,
        description="Тип операции",
    )


if __name__ == '__main__':
    print(Asset(
        type=AssetType.ADD,
        amount=100,
        cardNumber='123'
    ).model_dump_json(exclude_none=True))
