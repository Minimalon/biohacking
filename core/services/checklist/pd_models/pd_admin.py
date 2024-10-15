from pathlib import Path

from pydantic import BaseModel, Field, computed_field, model_validator

from core.database.enums.checklists import EnumCheckListContentActions


class CLCreateContent(BaseModel):
    content: str = ''
    page: int = 1
    action: EnumCheckListContentActions = EnumCheckListContentActions.NONE
    file_id: str | None = None


class CLCreateMenu(BaseModel):
    name: str
    contents: list[CLCreateContent] = []
    page: int = 1

    @model_validator(mode='after')
    def update_pages(self):
        for i, content in enumerate(self.contents, start=1):
            content.page = i
        return self


