"""Сборка приложения: создание объектов и связывание их зависимостей."""

from sqlalchemy.orm import Session

from marusya.cli.admin_menu import AdminMenu
from marusya.cli.app import ConsoleApp
from marusya.cli.client_menu import ClientMenu
from marusya.cli.console import Console
from marusya.database.repositories import SqlAdminRepository
from marusya.database.repositories import SqlBookingRepository
from marusya.database.repositories import SqlTableRepository
from marusya.database.session import SessionFactory
from marusya.cli.formatters import Formatter
from marusya.security import PasswordHasher
from marusya.seed import RESTAURANT
from marusya.services import AuthService
from marusya.services import BookingService


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
