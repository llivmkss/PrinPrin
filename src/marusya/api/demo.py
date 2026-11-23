"""Демонстрационный режим API без подключения к PostgreSQL."""

from fastapi import FastAPI

from marusya.api.dependencies import get_auth_service
from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_session
from marusya.models import Admin
from marusya.repositories import InMemoryAdminRepository
from marusya.repositories import InMemoryBookingRepository
from marusya.repositories import InMemoryTableRepository
from marusya.security import PasswordHasher
from marusya.seed import ADMIN_LOGIN
from marusya.seed import ADMIN_PASSWORD
from marusya.seed import TABLES
from marusya.services import AuthService
from marusya.services import BookingService


class DemoUnitOfWork:
    """Имитирует подтверждение транзакции для InMemory-хранилища."""

    def commit(self) -> None:
        """InMemory-репозитории сохраняют изменения сразу."""


def configure_demo(app: FastAPI) -> None:
    """Подменяет зависимости приложения демонстрационными."""
    booking_service = BookingService(
        InMemoryTableRepository(TABLES),
        InMemoryBookingRepository(),
    )

    hasher = PasswordHasher()
    auth_service = AuthService(
        InMemoryAdminRepository(
            [
                Admin(
                    login=ADMIN_LOGIN,
                    password_hash=hasher.make_hash(ADMIN_PASSWORD),
                ),
            ]
        ),
        hasher,
    )

    def demo_booking_service() -> BookingService:
        """Возвращает общий сервис бронирования для всех запросов."""
        return booking_service

    def demo_auth_service() -> AuthService:
        """Возвращает сервис авторизации с тестовым администратором."""
        return auth_service

    def demo_session() -> DemoUnitOfWork:
        """Предоставляет имитацию транзакции без базы данных."""
        return DemoUnitOfWork()

    app.dependency_overrides[get_booking_service] = demo_booking_service
    app.dependency_overrides[get_auth_service] = demo_auth_service
    app.dependency_overrides[get_session] = demo_session
