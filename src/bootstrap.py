"""Сборка приложения: создание объектов и связывание их зависимостей."""

from admin_menu import AdminMenu
from cli import ConsoleApp
from client_menu import ClientMenu
from console import Console
from models import Admin
from repositories import (
    InMemoryAdminRepository,
    InMemoryBookingRepository,
    InMemoryTableRepository,
)
from security import PasswordHasher
from seed import ADMIN_LOGIN, ADMIN_PASSWORD, RESTAURANT, TABLES
from services import AuthService, BookingService


def build_app() -> ConsoleApp:
    """Создаёт полностью настроенное консольное приложение."""
    hasher = PasswordHasher()
    admin = Admin(ADMIN_LOGIN, hasher.make_hash(ADMIN_PASSWORD))
    booking_service = BookingService(
        InMemoryTableRepository(TABLES),
        InMemoryBookingRepository(),
    )
    auth_service = AuthService(InMemoryAdminRepository([admin]), hasher)
    console = Console()
    return ConsoleApp(
        console,
        ClientMenu(console, RESTAURANT, booking_service),
        AdminMenu(console, auth_service, booking_service),
    )
