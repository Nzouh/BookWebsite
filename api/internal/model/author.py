from pydantic import BaseModel
from typing import Optional

class Author(BaseModel):
    name : str
    biography: Optional[str]
    book_list: list[str]