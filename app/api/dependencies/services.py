from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.core.factories import build_calculation_service, build_download_service, build_downloaded_file_service
from app.services.calculation_service import CalculationService
from app.services.download_service import DownloadService
from app.services.downloaded_file_service import (
    DownloadedFileService,
)


async def get_download_service(
    session: AsyncSession = Depends(get_session),
) -> DownloadService:
    return build_download_service(
        session=session,
    )

async def get_downloaded_file_service(
    session: AsyncSession = Depends(get_session),
) -> DownloadedFileService:
    return build_downloaded_file_service(
        session=session,
    )

async def get_calculation_service(
    session: AsyncSession = Depends(get_session),
) -> CalculationService:
    return build_calculation_service(
        session=session,
    )

