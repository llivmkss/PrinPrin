"""Бизнес-логика: бронирование столиков и аутентификация администратора."""

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import replace
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

from src.errors import AuthenticationError
from src.errors import BookingNotFoundError
from src.errors import CancellationError
from src.errors import TableUnavailableError
from src.errors import ValidationError
from src.models import BOOKING_DURATION
from src.models import Admin
from src.models import Booking
from src.models import BookingStatus
from src.models import Table
from src.repositories import AdminRepository
from src.repositories import BookingRepository
from src.repositories import TableRepository
from src.security import PasswordHasher

Clock = Callable[[], datetime]


@dataclass(frozen=True)
class TableOccupancy:
    """Занятость одного столика: сам столик и его действующие брони за день."""

    table: Table
    bookings: list[Booking]


class BookingService:
    """Поиск свободных столиков, создание, просмотр и отмена бронирований."""

    def __init__(
        self,
        tables: TableRepository,
        bookings: BookingRepository,
        clock: Clock = datetime.now,
    ) -> None:
        """Принимает хранилища и источник текущего времени (для проверок и тестов)."""
        self.__tables: TableRepository = tables
        self.__bookings: BookingRepository = bookings
        self.__clock: Clock = clock

    def find_available_tables(self, start: datetime, guests: int) -> list[Table]:
        """Возвращает столики, свободные на время брони и вмещающие всех гостей."""
        self.__check_request(start, guests)
        end = start + BOOKING_DURATION
        return [
            table
            for table in self.__tables.list_all()
            if self.__is_suitable(table, guests)
            and not self.__has_conflict(table.number, start, end)
        ]

    def create_booking(
        self,
        table_number: int,
        start: datetime,
        guests: int,
        customer_name: str,
        customer_phone: str,
    ) -> Booking:
        """Создаёт бронирование, повторно проверив доступность выбранного столика."""
        self.__check_request(start, guests)
        table = self.__tables.get(table_number)
        if table is None:
            raise TableUnavailableError("Столика с таким номером не существует.")
        if not self.__is_suitable(table, guests):
            raise TableUnavailableError(
                "Этот столик не подходит по вместимости или недоступен."
            )
        if self.__has_conflict(table_number, start, start + BOOKING_DURATION):
            raise TableUnavailableError("Этот столик уже занят на выбранное время.")
        booking = Booking(
            id=self.__bookings.next_id(),
            table_number=table_number,
            guests=guests,
            start=start,
            customer_name=customer_name,
            customer_phone=customer_phone,
        )
        self.__bookings.add(booking)
        return booking

    def get_booking(self, booking_id: int) -> Booking:
        """Возвращает бронирование по идентификатору или сообщает, что его нет."""
        booking = self.__bookings.get(booking_id)
        if booking is None:
            raise BookingNotFoundError(
                "Бронирование с таким идентификатором не найдено."
            )
        return booking

    def ensure_cancellable(self, booking: Booking) -> None:
        """Бросает ошибку, если бронирование уже отменено или его срок истёк."""
        if not booking.is_active():
            raise CancellationError("Это бронирование уже было отменено.")
        if booking.end <= self.__clock():
            raise CancellationError(
                "Срок действия бронирования истёк, отмена невозможна."
            )

    def cancel_booking(self, booking_id: int) -> Booking:
        """Помечает бронирование отменённым, не удаляя запись из хранилища."""
        booking = self.get_booking(booking_id)
        self.ensure_cancellable(booking)
        cancelled = replace(booking, status=BookingStatus.CANCELLED)
        self.__bookings.update(cancelled)
        return cancelled

    def list_bookings(self) -> list[Booking]:
        """Возвращает все бронирования, включая отменённые, по времени начала."""
        return sorted(self.__bookings.list_all(), key=lambda booking: booking.start)

    def occupancy_for_date(self, day: date) -> list[TableOccupancy]:
        """Возвращает для каждого столика его действующие брони на указанную дату."""
        day_start = datetime.combine(day, time.min)
        day_end = day_start + timedelta(days=1)
        occupancies: list[TableOccupancy] = []
        for table in self.__tables.list_all():
            bookings = sorted(
                (
                    booking
                    for booking in self.__bookings.list_by_table(table.number)
                    if booking.is_active() and booking.overlaps(day_start, day_end)
                ),
                key=lambda booking: booking.start,
            )
            occupancies.append(TableOccupancy(table, bookings))
        return occupancies

    def __check_request(self, start: datetime, guests: int) -> None:
        """Проверяет, что время не в прошлом, а количество гостей положительное."""
        if start < self.__clock():
            raise ValidationError("Дата и время бронирования не могут быть в прошлом.")
        Booking.validate_guests(guests)

    @staticmethod
    def __is_suitable(table: Table, guests: int) -> bool:
        """Проверяет, что столик доступен и вмещает указанное число гостей."""
        return table.is_available and table.capacity >= guests

    def __has_conflict(
        self,
        table_number: int,
        start: datetime,
        end: datetime,
        exclude_id: int | None = None,
    ) -> bool:
        """Ищет пересечение с действующими бронями; exclude_id исключает одну из них."""
        return any(
            booking.is_active()
            and booking.id != exclude_id
            and booking.overlaps(start, end)
            for booking in self.__bookings.list_by_table(table_number)
        )


class AuthService:
    """Проверка логина и пароля администратора."""

    def __init__(self, admins: AdminRepository, hasher: PasswordHasher) -> None:
        """Принимает хранилище администраторов и объект проверки паролей."""
        self.__admins: AdminRepository = admins
        self.__hasher: PasswordHasher = hasher

    def login(self, login: str, password: str) -> Admin:
        """Возвращает администратора при верных данных, иначе бросает ошибку."""
        admin = self.__admins.get_by_login(login.strip())
        if admin is None or not self.__hasher.verify(password, admin.password_hash):
            raise AuthenticationError("Неверный логин или пароль.")
        return admin
