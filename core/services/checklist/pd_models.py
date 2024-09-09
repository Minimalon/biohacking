from pydantic import BaseModel, Field, computed_field

class PDCLContent(BaseModel):
    id: int
    menu_id: int
    page: int = 1
    action: int = 0

