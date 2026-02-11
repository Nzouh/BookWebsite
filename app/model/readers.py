from pydantic import BaseModel
from typing import Optional

class Reader(BaseModel):
    name: str
    favorites: list[str] = []
    in_progress: list[str] = []
    finished: list[str] = []
    user_id: Optional[str] = None    # links to the User who owns this profile
