from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    content: str
    biography: Optional[str] = None    # book description/summary
    image: Optional[str] = None        # URL to the book cover image
