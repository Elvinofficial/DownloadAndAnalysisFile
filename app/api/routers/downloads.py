from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.services import get_download_service
from app.api.schemas.download import (
    DownloadJobResponse,
    DownloadJobStartResponse,
)
from app.db.models.download_job import DownloadJobStatus
from app.services.download_service import (
    DownloadJobNotFoundError,
    DownloadService,
)
from app.tasks.download_tasks import process_download_task


router = APIRouter(
    prefix="/downloads",
    tags=["Downloads"],
)


@router.post(
    "",
    response_model=DownloadJobStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_download(
    download_service: DownloadService = Depends(
        get_download_service,
    ),
) -> DownloadJobStartResponse:
    print("Starting download job...")
    job_id = await download_service.start_download()
    print(f"Download job started with ID: {job_id}")
    process_download_task.delay(
        str(job_id),
    )

    return DownloadJobStartResponse(
        job_id=job_id,
        status=DownloadJobStatus.PENDING,
    )


@router.get(
    "/{job_id}",
    response_model=DownloadJobResponse,
    status_code=status.HTTP_200_OK,
)
async def get_download_job(
    job_id: UUID,
    download_service: DownloadService = Depends(
        get_download_service,
    ),
) -> DownloadJobResponse:
    try:
        job = await download_service.get_job(
            job_id,
        )

    except DownloadJobNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return DownloadJobResponse.model_validate(job)