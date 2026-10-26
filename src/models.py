"""Модели предметной области: ресторан, столик, бронирование, администратор."""

import re
from dataclasses import dataclass
from datetime import datetime
from datetime import time
from datetime import timedelta
from enum import Enum

from src.errors import ValidationError

BOOKING_DURATION: timedelta = timedelta(hours=2)

_PHONE_SEPARATORS: re.Pattern[str] = re.compile(r"[\s\-()]")
_PHONE_PATTERN: re.Pattern[str] = re.compile(r"(\+7|8)\d{10}")
_MAX_NAME_LENGTH: int = 50


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

    def __post_init__(self) -> None:
        """Проверяет при создании, что номер и вместимость положительные."""
        if self.number <= 0:
            raise ValidationError("Номер столика должен быть больше нуля.")
        if self.capacity <= 0:
            raise ValidationError("Вместимость столика должна быть больше нуля.")


@dataclass
class Booking:
    """Бронирование одного столика на BOOKING_DURATION, начиная с момента start."""

    id: int
    table_number: int
    guests: int
    start: datetime
    customer_name: str
    customer_phone: str
    status: BookingStatus = BookingStatus.ACTIVE

    def __post_init__(self) -> None:
        """Проверяет данные при создании и очищает имя и телефон от лишнего."""
        self.validate_guests(self.guests)
        self.customer_name = self.validate_name(self.customer_name)
        self.customer_phone = self.validate_phone(self.customer_phone)

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

    @staticmethod
    def validate_name(raw: str) -> str:
        """Проверяет имя клиента и возвращает его без лишних пробелов."""
        name = raw.strip()
        if not name:
            raise ValidationError("Имя не может быть пустым.")
        if len(name) > _MAX_NAME_LENGTH:
            raise ValidationError(
                f"Имя не должно быть длиннее {_MAX_NAME_LENGTH} символов."
            )
        if not any(char.isalpha() for char in name):
            raise ValidationError("Имя должно содержать буквы.")
        return name

    @staticmethod
    def validate_phone(raw: str) -> str:
        """Проверяет формат телефона и возвращает его без пробелов и скобок."""
        phone = _PHONE_SEPARATORS.sub("", raw)
        if not _PHONE_PATTERN.fullmatch(phone):
            raise ValidationError(
                "Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX."
            )
        return phone

    @staticmethod
    def validate_guests(guests: int) -> int:
        """Проверяет, что количество гостей — положительное целое число."""
        if guests <= 0:
            raise ValidationError("Количество гостей должно быть больше нуля.")
        return guests


@dataclass(frozen=True)
class Admin:
    """Администратор: логин и хеш пароля (пароль в открытом виде не хранится)."""

    login: str
    password_hash: str
