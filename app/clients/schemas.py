from pydantic import BaseModel, Field


class FileNamesResponse(BaseModel):
    file_names: list[str]


class DownloadFilesRequest(BaseModel):
    file_names: list[str] = Field(
        min_length=1,
        max_length=3,
    )


class MarkDownloadedRequest(BaseModel):
    file_names: list[str] = Field(min_length=1)


class MarkDownloadedResponse(BaseModel):
    marked_now: int
    already_marked: int