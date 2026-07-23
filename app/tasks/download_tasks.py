import asyncio
from uuid import UUID

from app.clients.source_api_client import SourceApiClient
from app.core.config import settings
from app.core.factories import build_download_service
from app.db.session import AsyncSessionLocal, engine
from app.repositories.download_job_repository import (
    DownloadJobRepository,
)
from app.repositories.downloaded_file_repository import (
    DownloadedFileRepository,
)
from app.services.download_service import DownloadService
from app.services.file_storage_service import FileStorageService
from app.tasks.celery_app import celery_app


@celery_app.task(
    name="downloads.process",
)
def process_download_task(job_id: str) -> None:
    asyncio.run(
        _process_download(
            UUID(job_id),
        )
    )


async def _process_download(
    job_id: UUID,
) -> None:
    try:
        async with AsyncSessionLocal() as session:
            download_service = build_download_service(
                session=session,
            )

            await download_service.process_job(job_id)

    finally:
        await engine.dispose()