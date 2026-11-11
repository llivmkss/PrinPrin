"""Сборка приложения: создание объектов и связывание их зависимостей."""

from sqlalchemy.orm import Session

from src.admin_menu import AdminMenu
from src.cli import ConsoleApp
from src.client_menu import ClientMenu
from src.console import Console
from src.database.repositories import SqlAdminRepository
from src.database.repositories import SqlBookingRepository
from src.database.repositories import SqlTableRepository
from src.database.session import SessionFactory
from src.formatters import Formatter
from src.security import PasswordHasher
from src.seed import RESTAURANT
from src.services import AuthService
from src.services import BookingService


def build_app() -> ConsoleApp:
    """Создаёт полностью настроенное консольное приложение."""
    hasher = PasswordHasher()
    console = Console()
    formatter = Formatter()

    def make_booking_service(session: Session) -> BookingService:
        return BookingService(
            SqlTableRepository(session),
            SqlBookingRepository(session),
        )

    def make_client_menu(session: Session) -> ClientMenu:
        return ClientMenu(console, RESTAURANT, make_booking_service(session), formatter)

    def make_admin_menu(session: Session) -> AdminMenu:
        auth_service = AuthService(SqlAdminRepository(session), hasher)
        return AdminMenu(
            console, auth_service, make_booking_service(session), formatter
        )

    return ConsoleApp(console, SessionFactory, make_client_menu, make_admin_menu)
