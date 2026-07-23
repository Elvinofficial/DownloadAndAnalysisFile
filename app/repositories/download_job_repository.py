from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.download_job import DownloadJob, DownloadJobStatus


class DownloadJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self) -> DownloadJob:
        job = DownloadJob()

        self.session.add(job)
        await self.session.flush()

        return job

    async def get_by_id(
        self,
        job_id: UUID,
    ) -> DownloadJob | None:
        statement = select(DownloadJob).where(
            DownloadJob.id == job_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def mark_running(
        self,
        job: DownloadJob,
        *,
        started_at: datetime,
    ) -> DownloadJob:
        job.status = DownloadJobStatus.RUNNING
        job.started_at = started_at
        job.completed_at = None
        job.error_message = None

        await self.session.flush()

        return job

    async def set_total_files(
        self,
        job: DownloadJob,
        *,
        total_files: int,
    ) -> DownloadJob:
        job.total_files = total_files

        await self.session.flush()

        return job

    async def increment_downloaded_files(
        self,
        job: DownloadJob,
        *,
        count: int,
    ) -> DownloadJob:
        job.downloaded_files += count

        await self.session.flush()

        return job

    async def mark_completed(
        self,
        job: DownloadJob,
        *,
        completed_at: datetime,
    ) -> DownloadJob:
        job.status = DownloadJobStatus.COMPLETED
        job.completed_at = completed_at
        job.error_message = None

        await self.session.flush()

        return job

    async def mark_failed(
        self,
        job: DownloadJob,
        *,
        error_message: str,
        completed_at: datetime,
    ) -> DownloadJob:
        job.status = DownloadJobStatus.FAILED
        job.error_message = error_message
        job.completed_at = completed_at

        await self.session.flush()

        return job

    async def increment_total_files(
        self,
        job: DownloadJob,
        *,
        count: int,
    ) -> DownloadJob:
        if count < 0:
            raise ValueError("count must not be negative")

        job.total_files += count

        await self.session.flush()

        return job