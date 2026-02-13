from pydantic import BaseModel
from typing import Optional

class Chapter(BaseModel):
    title: str
    content: str
    order: int             # chapter number (1, 2, 3...)

class Book(BaseModel):
    title: str
    author: str
    biography: Optional[str] = None    # book description/summary
    image: Optional[str] = None        # URL to the book cover image
    chapters: list[Chapter] = []       # list of chapters (content lives here)
