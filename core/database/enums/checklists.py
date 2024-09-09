import enum


class EnumCheckListContentActions(enum.Enum):
    NONE = 'Ничего не запрашивать'
    GET_PHOTO = 'Запросить фото'
    GET_TEXT = 'Запросить текстовое сообщение'
