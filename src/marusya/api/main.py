"""Создание веб-приложения FastAPI."""

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from marusya.api.routes import router
from marusya.errors import AppError
from marusya.errors import TableUnavailableError


def create_app() -> FastAPI:
    """Создаёт приложение и подключает маршруты."""
    app = FastAPI(
        title="Маруся — система бронирования столиков",
        description="API для поиска столиков и создания бронирований.",
        version="0.1.0",
    )

    app.include_router(router)

    @app.exception_handler(AppError)
    def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        """Преобразует ошибки предметной области в ответы HTTP."""
        status_code = 400

        if isinstance(exc, TableUnavailableError):
            status_code = 409

        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
