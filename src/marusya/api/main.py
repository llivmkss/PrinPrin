
"""Создание веб-приложения FastAPI."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from marusya.api.admin_routes import router as admin_router
from marusya.api.demo import configure_demo
from marusya.api.routes import router
from marusya.errors import AppError
from marusya.errors import BookingNotFoundError
from marusya.errors import CancellationError
from marusya.errors import TableUnavailableError
from marusya.web.routes import router as web_router

STATIC_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "web" / "static"
)


def create_app(*, demo_mode: bool | None = None) -> FastAPI:
    """Создаёт веб-приложение и подключает маршруты."""
    app = FastAPI(
        title="Маруся — система бронирования столиков",
        description="API и веб-интерфейс ресторана «Маруся».",
        version="0.3.0",
    )

    if demo_mode is None:
        demo_mode = os.getenv("MARUSYA_DEMO_MODE") == "1"

    app.state.demo_mode = demo_mode

    app.include_router(router)
    app.include_router(admin_router)
    app.include_router(web_router)

    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIRECTORY),
        name="static",
    )

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

    if demo_mode:
        configure_demo(app)

    return app


app = create_app()
