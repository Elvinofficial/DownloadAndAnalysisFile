from dataclasses import dataclass
from math import ceil
from typing import Literal
from uuid import UUID

from app.db.models.downloaded_file import DownloadedFile
from app.repositories.downloaded_file_repository import (
    DownloadedFileRepository,
)


class DownloadedFileNotFoundError(Exception):
    pass


SortOrder = Literal["asc", "desc"]
SortBy = Literal["file_name", "downloaded_at"]


@dataclass(slots=True, frozen=True)
class DownloadedFilePage:
    items: list[DownloadedFile]
    page: int
    page_size: int
    total: int
    total_pages: int


class DownloadedFileService:
    def __init__(
        self,
        *,
        downloaded_file_repository: DownloadedFileRepository,
    ) -> None:
        self._downloaded_file_repository = downloaded_file_repository

    async def get_list(
        self,
        *,
        page: int,
        page_size: int,
        sort_by: SortBy,
        sort_order: SortOrder,
    ) -> DownloadedFilePage:
        offset = (page - 1) * page_size

        files = await self._downloaded_file_repository.get_list(
            offset=offset,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total = await self._downloaded_file_repository.count()

        total_pages = ceil(total / page_size) if total > 0 else 0

        return DownloadedFilePage(
            items=list(files),
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    async def get_by_id(
        self,
        file_id: UUID,
    ) -> DownloadedFile:
        downloaded_file = (
            await self._downloaded_file_repository.get_by_id(
                file_id,
            )
        )

        if downloaded_file is None:
            raise DownloadedFileNotFoundError(
                f"Downloaded file {file_id} was not found",
            )

        return downloaded_file