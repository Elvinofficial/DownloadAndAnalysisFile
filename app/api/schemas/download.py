from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field

from app.db.models.download_job import DownloadJobStatus


class DownloadJobStartResponse(BaseModel):
    job_id: UUID
    status: DownloadJobStatus


class DownloadJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: DownloadJobStatus
    total_files: int
    downloaded_files: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    @computed_field
    @property
    def progress_percent(self) -> int:
        if self.total_files == 0:
            return 0

        return round(
            self.downloaded_files / self.total_files * 100
        )