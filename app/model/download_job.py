from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DownloadStatus:
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

class BookStatus:
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class DownloadJob(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    book_hash: str
    user_id: Optional[str] = None
    status: str = DownloadStatus.PENDING
    progress: int = 0
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())
