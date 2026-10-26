"""Сборка приложения: создание объектов и связывание их зависимостей."""

from src.admin_menu import AdminMenu
from src.cli import ConsoleApp
from src.client_menu import ClientMenu
from src.console import Console
from src.formatters import Formatter
from src.models import Admin
from src.repositories import InMemoryAdminRepository
from src.repositories import InMemoryBookingRepository
from src.repositories import InMemoryTableRepository
from src.security import PasswordHasher
from src.seed import ADMIN_LOGIN
from src.seed import ADMIN_PASSWORD
from src.seed import RESTAURANT
from src.seed import TABLES
from src.services import AuthService
from src.services import BookingService


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
    formatter = Formatter()
    return ConsoleApp(
        console,
        ClientMenu(console, RESTAURANT, booking_service, formatter),
        AdminMenu(console, auth_service, booking_service, formatter),
    )
