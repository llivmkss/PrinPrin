"""Хранилища данных: абстрактные интерфейсы и реализации в оперативной памяти."""

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Iterator
from itertools import count

from src.models import Admin
from src.models import Booking
from src.models import Table


class TableRepository(ABC):
    """Интерфейс хранилища столиков."""

    @abstractmethod
    def get(self, number: int) -> Table | None:
        """Возвращает столик по номеру или None, если такого нет."""

    @abstractmethod
    def list_all(self) -> list[Table]:
        """Возвращает все столики, отсортированные по номеру."""


class BookingRepository(ABC):
    """Интерфейс хранилища бронирований."""

    @abstractmethod
    def next_id(self) -> int:
        """Выдаёт новый уникальный идентификатор бронирования."""

    @abstractmethod
    def add(self, booking: Booking) -> None:
        """Сохраняет новое бронирование."""

    @abstractmethod
    def update(self, booking: Booking) -> None:
        """Заменяет сохранённое бронирование с тем же идентификатором."""

    @abstractmethod
    def get(self, booking_id: int) -> Booking | None:
        """Возвращает бронирование по идентификатору или None."""

    @abstractmethod
    def list_all(self) -> list[Booking]:
        """Возвращает все бронирования, включая отменённые."""

    @abstractmethod
    def list_by_table(self, table_number: int) -> list[Booking]:
        """Возвращает все бронирования указанного столика."""


class AdminRepository(ABC):
    """Интерфейс хранилища администраторов."""

    @abstractmethod
    def get_by_login(self, login: str) -> Admin | None:
        """Возвращает администратора по логину или None."""


class InMemoryTableRepository(TableRepository):
    """Хранит столики в словаре, пока работает программа."""

    def __init__(self, tables: Iterable[Table]) -> None:
        """Заполняет хранилище переданными столиками."""
        self.__tables: dict[int, Table] = {table.number: table for table in tables}

    def get(self, number: int) -> Table | None:
        """Возвращает столик по номеру или None, если такого нет."""
        return self.__tables.get(number)

    def list_all(self) -> list[Table]:
        """Возвращает все столики, отсортированные по номеру."""
        return sorted(self.__tables.values(), key=lambda table: table.number)


class InMemoryBookingRepository(BookingRepository):
    """Хранит бронирования в словаре, пока работает программа."""

    def __init__(self) -> None:
        """Создаёт пустое хранилище и счётчик идентификаторов."""
        self.__bookings: dict[int, Booking] = {}
        self.__ids: Iterator[int] = count(1)

    def next_id(self) -> int:
        """Выдаёт новый уникальный идентификатор бронирования."""
        return next(self.__ids)

    def add(self, booking: Booking) -> None:
        """Сохраняет новое бронирование."""
        self.__bookings[booking.id] = booking

    def update(self, booking: Booking) -> None:
        """Заменяет сохранённое бронирование с тем же идентификатором."""
        self.__bookings[booking.id] = booking

    def get(self, booking_id: int) -> Booking | None:
        """Возвращает бронирование по идентификатору или None."""
        return self.__bookings.get(booking_id)

    def list_all(self) -> list[Booking]:
        """Возвращает все бронирования, включая отменённые."""
        return list(self.__bookings.values())

    def list_by_table(self, table_number: int) -> list[Booking]:
        """Возвращает все бронирования указанного столика."""
        return [
            booking
            for booking in self.__bookings.values()
            if booking.table_number == table_number
        ]


class InMemoryAdminRepository(AdminRepository):
    """Хранит администраторов в словаре, пока работает программа."""

    def __init__(self, admins: Iterable[Admin]) -> None:
        """Заполняет хранилище переданными администраторами."""
        self.__admins: dict[str, Admin] = {admin.login: admin for admin in admins}

    def get_by_login(self, login: str) -> Admin | None:
        """Возвращает администратора по логину или None."""
        return self.__admins.get(login)
