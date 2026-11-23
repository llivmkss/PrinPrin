"""Хранилища данных на SQLAlchemy и PostgreSQL."""

from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.orm import Session

from marusya.database import models as db
from marusya.models import Admin
from marusya.models import Booking
from marusya.models import BookingStatus
from marusya.models import Table
from marusya.repositories import AdminRepository
from marusya.repositories import BookingRepository
from marusya.repositories import TableRepository

_STATUS_TO_DB: dict[BookingStatus, str] = {
    BookingStatus.ACTIVE: "active",
    BookingStatus.CANCELLED: "cancelled",
}
_STATUS_FROM_DB: dict[str, BookingStatus] = {
    value: key for key, value in _STATUS_TO_DB.items()
}


class SqlTableRepository(TableRepository):
    """Хранит столики в таблице tables."""

    def __init__(self, session: Session) -> None:
        """Принимает открытую сессию; сам сессию не создаёт."""
        self.__session: Session = session

    def get(self, number: int) -> Table | None:
        """Возвращает столик по номеру или None, если такого нет."""
        row = self.__session.get(db.DiningTable, number)
        return None if row is None else self.__to_domain(row)

    def list_all(self) -> list[Table]:
        """Возвращает все столики, отсортированные по номеру."""
        statement = select(db.DiningTable).order_by(db.DiningTable.number)
        return [self.__to_domain(row) for row in self.__session.scalars(statement)]

    @staticmethod
    def __to_domain(row: db.DiningTable) -> Table:
        """Превращает строку таблицы в объект предметной области."""
        return Table(
            number=row.number,
            capacity=row.capacity,
            zone=row.zone,
            is_available=row.is_available,
        )


class SqlBookingRepository(BookingRepository):
    """Хранит бронирования в таблице bookings."""

    def __init__(self, session: Session) -> None:
        """Принимает открытую сессию; сам сессию не создаёт."""
        self.__session: Session = session

    def next_id(self) -> int:
        """Берёт следующий номер из счётчика базы данных."""
        statement = text("SELECT nextval(pg_get_serial_sequence('bookings', 'id'))")
        return int(self.__session.scalar(statement))

    def add(self, booking: Booking) -> None:
        """Сохраняет новое бронирование."""
        row = db.Booking(id=booking.id)
        self.__fill(row, booking)
        self.__session.add(row)
        self.__session.flush()

    def update(self, booking: Booking) -> None:
        """Заменяет сохранённое бронирование с тем же идентификатором."""
        row = self.__session.get(db.Booking, booking.id)
        if row is None:
            raise LookupError(f"Бронирование {booking.id} не найдено в базе.")
        self.__fill(row, booking)
        self.__session.flush()

    def get(self, booking_id: int) -> Booking | None:
        """Возвращает бронирование по идентификатору или None."""
        row = self.__session.get(db.Booking, booking_id)
        return None if row is None else self.__to_domain(row)

    def list_all(self) -> list[Booking]:
        """Возвращает все бронирования, включая отменённые."""
        statement = select(db.Booking).order_by(db.Booking.id)
        return [self.__to_domain(row) for row in self.__session.scalars(statement)]

    def list_by_table(self, table_number: int) -> list[Booking]:
        """Возвращает все бронирования указанного столика."""
        statement = (
            select(db.Booking)
            .where(db.Booking.table_number == table_number)
            .order_by(db.Booking.id)
        )
        return [self.__to_domain(row) for row in self.__session.scalars(statement)]

    @staticmethod
    def __fill(row: db.Booking, booking: Booking) -> None:
        """Переносит поля бронирования в строку таблицы."""
        row.table_number = booking.table_number
        row.guests = booking.guests
        row.start = booking.start
        row.customer_name = booking.customer_name
        row.customer_phone = booking.customer_phone
        row.status = _STATUS_TO_DB[booking.status]

    @staticmethod
    def __to_domain(row: db.Booking) -> Booking:
        """Превращает строку таблицы в объект предметной области."""
        return Booking(
            id=row.id,
            table_number=row.table_number,
            guests=row.guests,
            start=row.start,
            customer_name=row.customer_name,
            customer_phone=row.customer_phone,
            status=_STATUS_FROM_DB[row.status],
        )


class SqlAdminRepository(AdminRepository):
    """Хранит администраторов в таблице admins."""

    def __init__(self, session: Session) -> None:
        """Принимает открытую сессию; сам сессию не создаёт."""
        self.__session: Session = session

    def get_by_login(self, login: str) -> Admin | None:
        """Возвращает администратора по логину или None."""
        statement = select(db.Admin).where(db.Admin.login == login)
        row = self.__session.scalars(statement).first()
        if row is None:
            return None
        return Admin(login=row.login, password_hash=row.password_hash)
