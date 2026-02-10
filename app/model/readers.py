from pydantic import BaseModel
from typing import Optional

class Reader(BaseModel):
    name: str
    favorites: list[str]
    in_progress: list[str]
    finished: list[str]
