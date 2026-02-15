from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Chapter(BaseModel):
    title: str
    content: str
    order: int             # chapter number (1, 2, 3...)

class Book(BaseModel):
    title: str
    author: str
    biography: Optional[str] = None    # book description/summary
    image: Optional[str] = None        # URL to the book cover image (compatibility with old code)
    chapters: list[Chapter] = []       # list of chapters

    # Anna's Archive Metadata + Download Status
    md5: Optional[str] = None
    download_url: Optional[str] = None # Original source URL
    format: Optional[str] = None
    size: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    cover_url: Optional[str] = None    # New field for consistency
    cover_data: Optional[str] = None   # For fallback covers
    status: Optional[str] = "ready"    # processing, ready, error
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    requested_by: Optional[str] = None
    
    created_at: float = datetime.now().timestamp()
    updated_at: float = datetime.now().timestamp()
