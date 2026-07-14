from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class TsuboError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "tsubo_error",
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(TsuboError):
    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(message, code="not_found", status_code=404, **kwargs)


class ValidationError(TsuboError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code="validation_error", status_code=422, **kwargs)


class ExternalServiceError(TsuboError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code="external_service_error", status_code=502, **kwargs)


class FXRateUnavailableError(TsuboError):
    def __init__(self, message: str = "FX rate unavailable", **kwargs: Any) -> None:
        super().__init__(message, code="fx_rate_unavailable", status_code=503, **kwargs)


async def tsubo_error_handler(request: Request, exc: TsuboError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    detail = exc.detail
    if isinstance(detail, dict):
        content = detail
    else:
        content = {"message": str(detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "request_id": request_id,
                **content,
            }
        },
    )
