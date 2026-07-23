from collections import Counter
from dataclasses import dataclass
from uuid import UUID

from app.repositories.downloaded_file_repository import (
    DownloadedFileRepository,
)
from app.services.file_storage_service import (
    FileStorageService,
)


DIGITS = tuple(str(value) for value in range(10))


class CalculationFilesNotFoundError(Exception):
    def __init__(
        self,
        missing_file_ids: list[UUID],
    ) -> None:
        self.missing_file_ids = missing_file_ids

        super().__init__(
            f"Downloaded files were not found: "
            f"{', '.join(map(str, missing_file_ids))}"
        )


class InvalidFileContentError(Exception):
    pass


@dataclass(slots=True, frozen=True)
class DigitStatisticsResult:
    digits: dict[str, int]
    total_digits: int


@dataclass(slots=True, frozen=True)
class FileCalculationResult:
    file_id: UUID
    file_name: str
    statistics: DigitStatisticsResult


@dataclass(slots=True, frozen=True)
class CalculationResult:
    total: DigitStatisticsResult
    files: list[FileCalculationResult]


class CalculationService:
    def __init__(
        self,
        *,
        downloaded_file_repository: DownloadedFileRepository,
        file_storage_service: FileStorageService,
    ) -> None:
        self._downloaded_file_repository = (
            downloaded_file_repository
        )
        self._file_storage_service = (
            file_storage_service
        )

    async def calculate(
        self,
        *,
        file_ids: list[UUID],
    ) -> CalculationResult:
        downloaded_files = (
            await self._downloaded_file_repository.get_by_ids(
                file_ids,
            )
        )

        files_by_id = {
            downloaded_file.id: downloaded_file
            for downloaded_file in downloaded_files
        }

        missing_file_ids = [
            file_id
            for file_id in file_ids
            if file_id not in files_by_id
        ]

        if missing_file_ids:
            raise CalculationFilesNotFoundError(
                missing_file_ids,
            )

        total_counter: Counter[str] = Counter()
        file_results: list[FileCalculationResult] = []

        for file_id in file_ids:
            downloaded_file = files_by_id[file_id]

            content = (
                self._file_storage_service.read_text_file(
                    downloaded_file.storage_path,
                )
            )

            normalized_content = self._normalize_content(
                content=content,
                file_name=downloaded_file.file_name,
            )

            file_counter = Counter(normalized_content)
            total_counter.update(file_counter)

            file_results.append(
                FileCalculationResult(
                    file_id=downloaded_file.id,
                    file_name=downloaded_file.file_name,
                    statistics=self._build_statistics(
                        file_counter,
                    ),
                )
            )

        return CalculationResult(
            total=self._build_statistics(
                total_counter,
            ),
            files=file_results,
        )

    @staticmethod
    def _normalize_content(
        *,
        content: str,
        file_name: str,
    ) -> str:
        normalized_content = content.strip()

        if len(normalized_content) != 500:
            raise InvalidFileContentError(
                f"File {file_name} must contain "
                f"exactly 500 digits"
            )

        if not normalized_content.isascii():
            raise InvalidFileContentError(
                f"File {file_name} contains "
                f"non-ASCII characters"
            )

        if not normalized_content.isdigit():
            raise InvalidFileContentError(
                f"File {file_name} must contain "
                f"digits only"
            )

        return normalized_content

    @staticmethod
    def _build_statistics(
        counter: Counter[str],
    ) -> DigitStatisticsResult:
        digits = {
            digit: counter.get(digit, 0)
            for digit in DIGITS
        }

        return DigitStatisticsResult(
            digits=digits,
            total_digits=sum(digits.values()),
        )