from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.downloaded_file import DownloadedFile


@dataclass(slots=True, frozen=True)
class DownloadedFileCreate:
    file_name: str
    storage_path: str


class DownloadedFileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        job_id: UUID,
        file_name: str,
        storage_path: str,
    ) -> DownloadedFile:
        downloaded_file = DownloadedFile(
            job_id=job_id,
            file_name=file_name,
            storage_path=storage_path,
        )

        self.session.add(downloaded_file)
        await self.session.flush()

        return downloaded_file

    async def get_by_id(
        self,
        file_id: UUID,
    ) -> DownloadedFile | None:
        statement = select(DownloadedFile).where(
            DownloadedFile.id == file_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_job_id(
        self,
        job_id: UUID,
    ) -> Sequence[DownloadedFile]:
        statement = (
            select(DownloadedFile)
            .where(DownloadedFile.job_id == job_id)
            .order_by(DownloadedFile.downloaded_at.desc())
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def get_list(
        self,
        *,
        offset: int,
        limit: int,
        sort_by: str = "downloaded_at",
        sort_order: str = "desc",
    ) -> Sequence[DownloadedFile]:
        sort_columns = {
            "file_name": DownloadedFile.file_name,
            "downloaded_at": DownloadedFile.downloaded_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            DownloadedFile.downloaded_at,
        )

        order_expression = (
            sort_column.asc()
            if sort_order == "asc"
            else sort_column.desc()
        )

        statement = (
            select(DownloadedFile)
            .order_by(order_expression)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def count(self) -> int:
        statement = select(func.count(DownloadedFile.id))

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def create_many(
        self,
        *,
        job_id: UUID,
        files: list[DownloadedFileCreate],
    ) -> list[DownloadedFile]:
        downloaded_files = [
            DownloadedFile(
                job_id=job_id,
                file_name=file.file_name,
                storage_path=file.storage_path,
            )
            for file in files
        ]

        self.session.add_all(downloaded_files)
        await self.session.flush()

        return downloaded_files

    async def get_by_ids(
        self,
        file_ids: list[UUID],
    ) -> list[DownloadedFile]:
        if not file_ids:
            return []

        statement = (
            select(DownloadedFile)
            .where(
                DownloadedFile.id.in_(file_ids),
            )
        )

        result = await self.session.execute(statement)

        return list(
            result.scalars().all()
        )