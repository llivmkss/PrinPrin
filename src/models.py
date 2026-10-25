"""Модели предметной области: ресторан, столик, бронирование, администратор."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum

BOOKING_DURATION = timedelta(hours=2)


class BookingStatus(Enum):
    """Статус бронирования: действующее или отменённое."""

    ACTIVE = "активно"
    CANCELLED = "отменено"


@dataclass(frozen=True)
class Restaurant:
    """Основная информация о ресторане: название, адрес, часы работы, контакты."""

    name: str
    address: str
    opens_at: time
    closes_at: time
    phone: str

    def working_hours(self) -> str:
        """Возвращает часы работы в виде строки «ЧЧ:ММ–ЧЧ:ММ»."""
        return f"{self.opens_at:%H:%M}–{self.closes_at:%H:%M}"


@dataclass(frozen=True)
class Table:
    """Столик: номер, вместимость, зона ресторана и признак доступности."""

    number: int
    capacity: int
    zone: str
    is_available: bool = True


@dataclass(frozen=True)
class Booking:
    """Бронирование одного столика на BOOKING_DURATION, начиная с момента start."""

    id: int
    table_number: int
    guests: int
    start: datetime
    customer_name: str
    customer_phone: str
    status: BookingStatus = BookingStatus.ACTIVE

    @property
    def end(self) -> datetime:
        """Момент окончания бронирования."""
        return self.start + BOOKING_DURATION

    def is_active(self) -> bool:
        """Показывает, что бронирование не отменено."""
        return self.status is BookingStatus.ACTIVE

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Проверяет пересечение с интервалом. Касание границами не конфликт."""
        return self.start < end and start < self.end


@dataclass(frozen=True)
class Admin:
    """Администратор: логин и хеш пароля (пароль в открытом виде не хранится)."""

    login: str
    password_hash: str
