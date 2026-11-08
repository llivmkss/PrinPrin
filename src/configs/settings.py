import os

DEFAULT_DATABASE_URL = "postgresql+psycopg://marusya:marusya@localhost:5432/marusya"


class Settings:
    """Настройки приложения, читаемые из переменных окружения."""

    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


settings = Settings()