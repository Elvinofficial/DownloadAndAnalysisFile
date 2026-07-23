from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CalculationRequest(BaseModel):
    file_ids: list[UUID] = Field(
        min_length=1,
    )

    @field_validator("file_ids")
    @classmethod
    def validate_unique_file_ids(
        cls,
        value: list[UUID],
    ) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError(
                "file_ids must not contain duplicates"
            )

        return value


class DigitStatistics(BaseModel):
    digits: dict[str, int]
    total_digits: int


class FileCalculationResponse(BaseModel):
    file_id: UUID
    file_name: str
    statistics: DigitStatistics


class CalculationResponse(BaseModel):
    total: DigitStatistics
    files: list[FileCalculationResponse]