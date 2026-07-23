class SourceApiError(Exception):
    """Базовая ошибка интеграции с внешним API."""


class SourceApiUnavailableError(SourceApiError):
    """Внешний API временно недоступен."""


class SourceApiRateLimitError(SourceApiError):
    def __init__(
        self,
        retry_after_seconds: int,
        message: str = "Source API rate limit exceeded",
    ) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class SourceApiResponseError(SourceApiError):
    def __init__(
        self,
        *,
        status_code: int,
        response_body: str,
    ) -> None:
        super().__init__(
            f"Unexpected source API response: "
            f"status={status_code}, body={response_body}"
        )
        self.status_code = status_code
        self.response_body = response_body