"""Абстрактная фабрика семейств репозиториев (GoF Abstract Factory)."""

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable

from sqlalchemy.orm import Session

from marusya.database.repositories import SqlAdminRepository
from marusya.database.repositories import SqlBookingRepository
from marusya.database.repositories import SqlTableRepository
from marusya.models import Admin
from marusya.models import Table
from marusya.repositories import AdminRepository
from marusya.repositories import BookingRepository
from marusya.repositories import InMemoryAdminRepository
from marusya.repositories import InMemoryBookingRepository
from marusya.repositories import InMemoryTableRepository
from marusya.repositories import TableRepository


class RepositoryFactory(ABC):
    """Общий интерфейс создания семейства репозиториев."""

    @abstractmethod
    def create_table_repository(self) -> TableRepository:
        """Создаёт или возвращает репозиторий столиков."""

    @abstractmethod
    def create_booking_repository(self) -> BookingRepository:
        """Создаёт или возвращает репозиторий бронирований."""

    @abstractmethod
    def create_admin_repository(self) -> AdminRepository:
        """Создаёт или возвращает репозиторий администраторов."""


class SqlRepositoryFactory(RepositoryFactory):
    """Создаёт SQL-репозитории с общей SQLAlchemy Session."""

    def __init__(self, session: Session) -> None:
        """Принимает сессию текущего запроса."""
        self._session = session

    def create_table_repository(self) -> TableRepository:
        """Создаёт SQL-репозиторий столиков."""
        return SqlTableRepository(self._session)

    def create_booking_repository(self) -> BookingRepository:
        """Создаёт SQL-репозиторий бронирований."""
        return SqlBookingRepository(self._session)

    def create_admin_repository(self) -> AdminRepository:
        """Создаёт SQL-репозиторий администраторов."""
        return SqlAdminRepository(self._session)


class InMemoryRepositoryFactory(RepositoryFactory):
    """Предоставляет единое семейство InMemory-репозиториев."""

    def __init__(
        self,
        tables: Iterable[Table],
        admins: Iterable[Admin],
    ) -> None:
        """Создаёт хранилища, существующие весь срок жизни фабрики."""
        self._tables = InMemoryTableRepository(tables)
        self._bookings = InMemoryBookingRepository()
        self._admins = InMemoryAdminRepository(admins)

    def create_table_repository(self) -> TableRepository:
        """Возвращает общее хранилище столиков."""
        return self._tables

    def create_booking_repository(self) -> BookingRepository:
        """Возвращает общее хранилище бронирований."""
        return self._bookings

    def create_admin_repository(self) -> AdminRepository:
        """Возвращает общее хранилище администраторов."""
        return self._admins
