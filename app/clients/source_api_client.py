import asyncio
from collections.abc import Mapping
from time import monotonic
from typing import Any

import httpx

from app.clients.exceptions import (
    SourceApiRateLimitError,
    SourceApiResponseError,
    SourceApiUnavailableError,
)
from app.clients.schemas import (
    FileNamesResponse,
    MarkDownloadedResponse,
)
from app.core.config import Settings


class SourceApiClient:
    REQUEST_INTERVAL_SECONDS = 1.0

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self._base_url = settings.source_api_url.rstrip("/")
        self._timeout = settings.source_api_timeout_seconds

        self._headers = {
            "X-Candidate-Id": settings.source_api_candidate_id,
        }

        self._request_lock = asyncio.Lock()
        self._last_request_at: float | None = None

    async def _wait_before_request(self) -> None:
        if self._last_request_at is None:
            return

        elapsed = monotonic() - self._last_request_at

        delay = self.REQUEST_INTERVAL_SECONDS - elapsed

        if delay > 0:
            await asyncio.sleep(delay)

    async def get_file_names(self) -> list[str]:
        response = await self._request(
            method="GET",
            path="/api/files/names",
        )

        data = FileNamesResponse.model_validate(response.json())

        print("Received file names:", data.file_names)  # Debugging line

        return data.file_names

    async def download_files(
        self,
        file_names: list[str],
    ) -> bytes:
        if not 1 <= len(file_names) <= 3:
            raise ValueError(
                "download_files accepts from 1 to 3 file names"
            )

        response = await self._request(
            method="POST",
            path="/api/files/download",
            json={
                "file_names": file_names,
            },
            headers={
                "Accept": "application/zip",
            },
        )

        content_type = response.headers.get("content-type", "")

        if "application/zip" not in content_type:
            raise SourceApiResponseError(
                status_code=response.status_code,
                response_body=(
                    f"Expected application/zip, got {content_type}"
                ),
            )

        return response.content

    async def mark_downloaded(
        self,
        file_names: list[str],
    ) -> MarkDownloadedResponse:
        if not file_names:
            raise ValueError("file_names must not be empty")

        response = await self._request(
            method="POST",
            path="/api/files/downloaded",
            json={
                "file_names": file_names,
            },
        )

        return MarkDownloadedResponse.model_validate(
            response.json()
        )

    async def _request(
        self,
        *,
        method: str,
        path: str,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        request_headers = {
            **self._headers,
            **(headers or {}),
        }

        async with self._request_lock:
            await self._wait_before_request()

            try:
                async with httpx.AsyncClient(
                    base_url=self._base_url,
                    timeout=self._timeout,
                    headers=request_headers,
                ) as client:
                    response = await client.request(
                        method=method,
                        url=path,
                        json=json,
                    )

            except httpx.TimeoutException as error:
                raise SourceApiUnavailableError(
                    "Source API request timed out",
                ) from error

            except httpx.RequestError as error:
                raise SourceApiUnavailableError(
                    f"Source API connection error: {error}",
                ) from error

            finally:
                print(
                    "Candidate ID:",
                    self._headers.get("X-Candidate-Id"),
                    flush=True,
                )
                self._last_request_at = monotonic()

        if response.status_code in {403, 429}:
            retry_after = self._parse_retry_after(
                response.headers.get("Retry-After"),
            )

            raise SourceApiRateLimitError(
                retry_after_seconds=retry_after,
            )

        if not response.is_success:
            raise SourceApiResponseError(
                status_code=response.status_code,
                response_body=response.text,
            )

        return response

    @staticmethod
    def _parse_retry_after(value: str | None) -> int:
        if value is None:
            return 60

        try:
            return max(int(value), 1)
        except ValueError:
            return 60