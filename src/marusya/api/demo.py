"""Демонстрационный режим API без PostgreSQL."""

from fastapi import FastAPI

from marusya.api.dependencies import get_auth_service
from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_session
from marusya.models import Admin
from marusya.repository_factories import InMemoryRepositoryFactory
from marusya.security import PasswordHasher
from marusya.seed import ADMIN_LOGIN
from marusya.seed import ADMIN_PASSWORD
from marusya.seed import TABLES
from marusya.services import AuthService
from marusya.services import BookingService


class DemoUnitOfWork:
    """Имитирует подтверждение транзакции в InMemory-режиме."""

    def commit(self) -> None:
        """InMemory-репозитории сохраняют изменения сразу."""


def configure_demo(app: FastAPI) -> None:
    """Подменяет SQL-зависимости демонстрационными."""
    hasher = PasswordHasher()

    factory = InMemoryRepositoryFactory(
        tables=TABLES,
        admins=[
            Admin(
                login=ADMIN_LOGIN,
                password_hash=hasher.make_hash(ADMIN_PASSWORD),
            ),
        ],
    )

    booking_service = BookingService(
        factory.create_table_repository(),
        factory.create_booking_repository(),
    )

    auth_service = AuthService(
        factory.create_admin_repository(),
        hasher,
    )

    def demo_booking_service() -> BookingService:
        """Возвращает общий сервис бронирования."""
        return booking_service

    def demo_auth_service() -> AuthService:
        """Возвращает общий сервис аутентификации."""
        return auth_service

    def demo_session() -> DemoUnitOfWork:
        """Возвращает имитацию транзакции."""
        return DemoUnitOfWork()

    app.dependency_overrides[get_booking_service] = demo_booking_service
    app.dependency_overrides[get_auth_service] = demo_auth_service
    app.dependency_overrides[get_session] = demo_session
