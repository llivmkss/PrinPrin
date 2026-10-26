"""Точка входа: запуск консольного приложения бронирования столиков."""

from src.bootstrap import build_app


def main() -> None:
    """Собирает приложение и запускает его."""
    build_app().run()


if __name__ == "__main__":
    main()
