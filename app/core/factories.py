from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.source_api_client import SourceApiClient
from app.core.config import settings
from app.repositories.download_job_repository import DownloadJobRepository
from app.repositories.downloaded_file_repository import DownloadedFileRepository
from app.services.download_service import DownloadService
from app.services.file_storage_service import FileStorageService
from app.services.downloaded_file_service import (
    DownloadedFileService,
)
from pathlib import Path
from app.services.calculation_service import (
    CalculationService,
)

def build_calculation_service(
    session: AsyncSession,
) -> CalculationService:
    downloaded_file_repository = DownloadedFileRepository(
        session=session,
    )

    file_storage_service = FileStorageService(
        storage_root=settings.storage_root,
    )

    return CalculationService(
        downloaded_file_repository=downloaded_file_repository,
        file_storage_service=file_storage_service,
    )

def build_downloaded_file_service(
    session: AsyncSession,
) -> DownloadedFileService:
    downloaded_file_repository = DownloadedFileRepository(
        session=session,
    )

    return DownloadedFileService(
        downloaded_file_repository=downloaded_file_repository,
    )




def build_download_service(
    session: AsyncSession,
) -> DownloadService:
    source_api_client = SourceApiClient(
        settings=settings,
    )

    file_storage_service = FileStorageService(
        storage_root=settings.absolute_storage_root,
    )

    download_job_repository = DownloadJobRepository(
        session=session,
    )

    downloaded_file_repository = DownloadedFileRepository(
        session=session,
    )
    

    return DownloadService(
        session=session,
        source_api_client=source_api_client,
        file_storage_service=file_storage_service,
        download_job_repository=download_job_repository,
        downloaded_file_repository=downloaded_file_repository,
    )