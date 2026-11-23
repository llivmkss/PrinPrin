"""Запуск демонстрационного веб-приложения одной командой."""

import uvicorn

from marusya.api.main import create_app


def main() -> None:
    """Запускает FastAPI с InMemory-хранилищами на localhost."""
    app = create_app(demo_mode=True)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
