from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from core.database.enums.checklists import EnumCheckListContentActions


class PDCLAction(BaseModel):
    id: int
    action: EnumCheckListContentActions
    checklistcontentid: int

class PDCLContent(BaseModel):
    id: int
    menu_id: int
    page: int = 1
    action: int = 0

class Content(BaseModel):
    id: int
    content: str
    file_id: str | None = None
    page: int
    checklistmenuid: int

class Answer(BaseModel):
    content: Content
    action: EnumCheckListContentActions
    time_answer: datetime = Field(default_factory=datetime.now)
    file_id: str | None = None
    text: str | None = None


class PDCheckList(BaseModel):
    menu_name: str
    answers: list[Answer]