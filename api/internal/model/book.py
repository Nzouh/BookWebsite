from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    title: str
    author: str
    publish_date: datetime
    content: str
