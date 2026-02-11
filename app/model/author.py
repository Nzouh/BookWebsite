from pydantic import BaseModel
from typing import Optional

class Author(BaseModel):
    name: str
    biography: Optional[str] = None
    book_list: list[str] = []
    profile_picture: Optional[str] = None   # URL to profile picture
    user_id: Optional[str] = None           # links to the User who owns this profile