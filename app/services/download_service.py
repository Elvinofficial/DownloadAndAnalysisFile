from datetime import UTC, datetime
from typing import Iterator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.source_api_client import SourceApiClient
from app.repositories.download_job_repository import DownloadJobRepository
from app.repositories.downloaded_file_repository import DownloadedFileCreate, DownloadedFileRepository
from app.services.file_storage_service import FileStorageService
from app.db.models.download_job import DownloadJob
import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.clients.exceptions import SourceApiRateLimitError

T = TypeVar("T")


class DownloadJobNotFoundError(Exception):
    pass


class DownloadService:
    BATCH_SIZE = 3
    MAX_RATE_LIMIT_RETRIES = 5

    def __init__(
        self,
        *,
        session: AsyncSession,
        source_api_client: SourceApiClient,
        file_storage_service: FileStorageService,
        download_job_repository: DownloadJobRepository,
        downloaded_file_repository: DownloadedFileRepository,
    ) -> None:
        self._session = session
        self._source_api_client = source_api_client
        self._file_storage_service = file_storage_service
        self._download_job_repository = download_job_repository
        self._downloaded_file_repository = downloaded_file_repository

    async def _execute_with_rate_limit_retry(
        self,
        operation: Callable[[], Awaitable[T]],
    ) -> T:
        for attempt in range(self.MAX_RATE_LIMIT_RETRIES + 1):
            try:
                return await operation()

            except SourceApiRateLimitError as error:
                if attempt >= self.MAX_RATE_LIMIT_RETRIES:
                    raise

                await asyncio.sleep(
                    error.retry_after_seconds,
                )

        raise RuntimeError("Unreachable code")

    async def start_download(self) -> UUID:
        job = await self._download_job_repository.create()

        await self._session.commit()

        return job.id

    async def process_job(
        self,
        job_id: UUID,
    ) -> None:
        job = await self._download_job_repository.get_by_id(job_id)

        if job is None:
            raise DownloadJobNotFoundError(
                f"Download job {job_id} was not found",
            )

        try:
            await self._download_job_repository.mark_running(
                job,
                started_at=datetime.now(UTC),
            )
            await self._session.commit()

            file_names = await self._execute_with_rate_limit_retry(
                self._source_api_client.get_file_names,
            )

            print("FILE NAMES RESPONSE:", repr(file_names))
            print("FILE NAMES TYPE:", type(file_names))
            print("FILE NAMES COUNT:", len(file_names))

            await self._download_job_repository.increment_total_files(
                job,
                count=len(file_names),
            )
            await self._session.commit()

            for batch in self._split_into_batches(
                file_names,
                self.BATCH_SIZE,
            ):
                archive = await self._execute_with_rate_limit_retry(
                    lambda batch=batch: (
                        self._source_api_client.download_files(batch)
                    ),
                )

                stored_files = self._file_storage_service.save_archive(
                    archive_bytes=archive,
                    expected_file_names=batch,
                )

                files_to_create = [
                    DownloadedFileCreate(
                        file_name=stored_file.file_name,
                        storage_path=stored_file.storage_path,
                    )
                    for stored_file in stored_files
                ]

                await self._downloaded_file_repository.create_many(
                    job_id=job.id,
                    files=files_to_create,
                )

                await self._session.commit()

                await self._execute_with_rate_limit_retry(
                    lambda batch=batch: (
                        self._source_api_client.mark_downloaded(batch)
                    ),
                )

                await self._download_job_repository.increment_downloaded_files(
                    job,
                    count=len(stored_files),
                )

                await self._session.commit()

            await self._download_job_repository.mark_completed(
                job,
                completed_at=datetime.now(UTC),
            )
            await self._session.commit()

        except Exception as exc:
            await self._session.rollback()

            failed_job = await self._download_job_repository.get_by_id(job_id)

            if failed_job is not None:
                await self._download_job_repository.mark_failed(
                    failed_job,
                    error_message=str(exc),
                    completed_at=datetime.now(UTC),
                )
                await self._session.commit()

            raise

    async def get_job(
        self,
        job_id: UUID,
    ) -> DownloadJob:
        job = await self._download_job_repository.get_by_id(job_id)

        if job is None:
            raise DownloadJobNotFoundError(
                f"Download job {job_id} was not found",
            )

        return job

    @staticmethod
    def _split_into_batches(
        file_names: list[str],
        batch_size: int,
    ) -> Iterator[list[str]]:
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero"
            )

        for index in range(0, len(file_names), batch_size):
            yield file_names[index:index + batch_size]