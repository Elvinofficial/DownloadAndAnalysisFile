from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DownloadedFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    downloaded_at: datetime


class DownloadedFileListResponse(BaseModel):
    items: list[DownloadedFileResponse]

    page: int
    page_size: int
    total: int
    total_pages: int