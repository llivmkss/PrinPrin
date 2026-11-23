"""Тесты паттерна GoF Abstract Factory и запуска деморежима."""

from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from sqlalchemy.orm import Session

from marusya.database.repositories import SqlAdminRepository
from marusya.database.repositories import SqlBookingRepository
from marusya.database.repositories import SqlTableRepository
from marusya.models import Admin
from marusya.models import Table
from marusya.repository_factories import InMemoryRepositoryFactory
from marusya.repository_factories import SqlRepositoryFactory
from marusya.run_demo import main as run_demo
from marusya.security import PasswordHasher
from marusya.services import AuthService
from marusya.services import BookingService


class TestRepositoryFactories(TestCase):
    """Проверяет создание согласованных семейств репозиториев."""

    def setUp(self) -> None:
        """Создаёт изолированное семейство InMemory-репозиториев."""
        self.hasher = PasswordHasher()

        self.factory = InMemoryRepositoryFactory(
            tables=[
                Table(number=1, capacity=2, zone="Основной зал"),
                Table(number=2, capacity=4, zone="У окна"),
            ],
            admins=[
                Admin(
                    login="admin",
                    password_hash=self.hasher.make_hash("test-password"),
                ),
            ],
        )

    def test_memory_table_repository_is_shared(self) -> None:
        """Одна фабрика возвращает одно хранилище столиков."""
        first = self.factory.create_table_repository()
        second = self.factory.create_table_repository()

        self.assertIs(first, second)
        self.assertEqual(len(first.list_all()), 2)

    def test_memory_booking_repository_is_shared(self) -> None:
        """Все сервисы используют общие InMemory-бронирования."""
        first = self.factory.create_booking_repository()
        second = self.factory.create_booking_repository()

        self.assertIs(first, second)

    def test_memory_admin_repository_is_shared(self) -> None:
        """Хранилище администраторов повторно используется."""
        first = self.factory.create_admin_repository()
        second = self.factory.create_admin_repository()

        self.assertIs(first, second)
        self.assertIsNotNone(first.get_by_login("admin"))

    def test_memory_factories_are_isolated(self) -> None:
        """Разные фабрики создают независимые хранилища."""
        other = InMemoryRepositoryFactory(
            tables=[Table(number=3, capacity=6, zone="Терраса")],
            admins=[],
        )

        self.assertIsNot(
            self.factory.create_booking_repository(),
            other.create_booking_repository(),
        )

        self.assertEqual(
            len(other.create_table_repository().list_all()),
            1,
        )

    def test_memory_family_works_with_booking_service(self) -> None:
        """Бизнес-сервис работает с репозиториями фабрики."""
        service = BookingService(
            self.factory.create_table_repository(),
            self.factory.create_booking_repository(),
            clock=lambda: datetime(2029, 1, 1),
        )

        booking = service.create_booking(
            table_number=1,
            start=datetime(2030, 5, 12, 19, 0),
            guests=2,
            customer_name="Анна",
            customer_phone="+79991234567",
        )

        saved = self.factory.create_booking_repository().get(booking.id)

        self.assertIsNotNone(saved)
        self.assertEqual(saved.id, booking.id)
        self.assertEqual(saved.customer_name, "Анна")

    def test_memory_family_works_with_auth_service(self) -> None:
        """Администратор проходит проверку через репозиторий фабрики."""
        service = AuthService(
            self.factory.create_admin_repository(),
            self.hasher,
        )

        admin = service.login("admin", "test-password")

        self.assertEqual(admin.login, "admin")

    def test_sql_factory_uses_supplied_session(self) -> None:
        """SQL-фабрика создаёт репозитории с переданной сессией."""
        session = Mock(spec=Session)
        session.get.return_value = None

        factory = SqlRepositoryFactory(session)

        tables = factory.create_table_repository()
        bookings = factory.create_booking_repository()
        admins = factory.create_admin_repository()

        self.assertIsInstance(tables, SqlTableRepository)
        self.assertIsInstance(bookings, SqlBookingRepository)
        self.assertIsInstance(admins, SqlAdminRepository)

        self.assertIsNone(tables.get(1))
        session.get.assert_called_once()

    def test_demo_launcher_uses_demo_application(self) -> None:
        """Точка входа запускает локальное приложение без БД."""
        with patch("marusya.run_demo.uvicorn.run") as mocked_run:
            run_demo()

        mocked_run.assert_called_once()

        app = mocked_run.call_args.args[0]
        options = mocked_run.call_args.kwargs

        self.assertTrue(app.state.demo_mode)
        self.assertEqual(options["host"], "127.0.0.1")
        self.assertEqual(options["port"], 8000)
