from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.services import get_downloaded_file_service
from app.api.schemas.downloaded_file import (
    DownloadedFileListResponse,
    DownloadedFileResponse,
)
from app.services.downloaded_file_service import (
    DownloadedFileNotFoundError,
    DownloadedFileService,
)


router = APIRouter(
    prefix="/files",
    tags=["Downloaded files"],
)


@router.get(
    "",
    response_model=DownloadedFileListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_downloaded_files(
    downloaded_file_service: DownloadedFileService = Depends(
        get_downloaded_file_service,
    ),
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 10,
    sort_by: Literal[
        "file_name",
        "downloaded_at",
    ] = "downloaded_at",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
) -> DownloadedFileListResponse:
    result = await downloaded_file_service.get_list(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return DownloadedFileListResponse(
        items=[
            DownloadedFileResponse.model_validate(item)
            for item in result.items
        ],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
        total_pages=result.total_pages,
    )


@router.get(
    "/{file_id}",
    response_model=DownloadedFileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_downloaded_file(
    file_id: UUID,
    downloaded_file_service: DownloadedFileService = Depends(
        get_downloaded_file_service,
    ),
) -> DownloadedFileResponse:
    try:
        downloaded_file = await downloaded_file_service.get_by_id(
            file_id,
        )

    except DownloadedFileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return DownloadedFileResponse.model_validate(
        downloaded_file,
    )