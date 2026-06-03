from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import ChatRequiresMatchError, DomainError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        status_code = 400
        if exc.code == "not_found":
            status_code = 404
        elif exc.code == "unauthorized":
            status_code = 401
        elif exc.code == "forbidden":
            status_code = 403
        elif exc.code == "conflict":
            status_code = 409
        elif exc.code == "chat_requires_match":
            status_code = 403

        body: dict = {"error": exc.message, "code": exc.code}
        if isinstance(exc, ChatRequiresMatchError):
            body = {"error": exc.message}

        return JSONResponse(status_code=status_code, content=body)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        from app.config import get_settings
        from app.infrastructure.logging.setup import get_logger

        logger = get_logger("api")
        settings = get_settings()
        logger.error("unhandled_exception", error=str(exc), exc_info=settings.debug)
        detail = str(exc) if settings.debug else "Erro interno do servidor."
        return JSONResponse(status_code=500, content={"error": detail, "code": "internal_error"})
