"""Создание веб-приложения FastAPI."""

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from marusya.api.admin_routes import router as admin_router
from marusya.api.routes import router
from marusya.errors import AppError
from marusya.errors import BookingNotFoundError
from marusya.errors import CancellationError
from marusya.errors import TableUnavailableError


def create_app() -> FastAPI:
    """Создаёт приложение и подключает маршруты."""
    app = FastAPI(
        title="Маруся — система бронирования столиков",
        description="API для клиентов и администраторов ресторана.",
        version="0.2.0",
    )

    app.include_router(router)
    app.include_router(admin_router)

    @app.exception_handler(AppError)
    def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        """Преобразует ошибки предметной области в HTTP-ответы."""
        status_code = 400

        if isinstance(exc, BookingNotFoundError):
            status_code = 404
        elif isinstance(exc, (TableUnavailableError, CancellationError)):
            status_code = 409

        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
