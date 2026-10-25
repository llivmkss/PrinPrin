"""Проверка и разбор данных, введённых пользователем."""

import re
from datetime import date, datetime, time

from errors import ValidationError

_PHONE_SEPARATORS = re.compile(r"[\s\-()]")
_PHONE_PATTERN = re.compile(r"(\+7|8)\d{10}")
_MAX_NAME_LENGTH = 50


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


def validate_phone(raw: str) -> str:
    """Проверяет формат телефона и возвращает его без пробелов, скобок и дефисов."""
    phone = _PHONE_SEPARATORS.sub("", raw)
    if not _PHONE_PATTERN.fullmatch(phone):
        raise ValidationError(
            "Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX."
        )
    return phone


def ensure_positive_guests(guests: int) -> int:
    """Проверяет, что количество гостей — положительное целое число."""
    if guests <= 0:
        raise ValidationError("Количество гостей должно быть больше нуля.")
    return guests


def parse_positive_int(raw: str, field: str) -> int:
    """Преобразует строку в положительное целое число или сообщает об ошибке."""
    try:
        value = int(raw.strip())
    except ValueError:
        raise ValidationError(
            f"Поле «{field}» должно быть целым положительным числом."
        ) from None
    if value <= 0:
        raise ValidationError(f"Поле «{field}» должно быть больше нуля.")
    return value


def parse_guests(raw: str) -> int:
    """Разбирает количество гостей."""
    return parse_positive_int(raw, "Количество гостей")


def parse_table_number(raw: str) -> int:
    """Разбирает номер столика."""
    return parse_positive_int(raw, "Номер столика")


def parse_booking_id(raw: str) -> int:
    """Разбирает идентификатор бронирования."""
    return parse_positive_int(raw, "Идентификатор бронирования")


def parse_date(raw: str) -> date:
    """Разбирает дату в формате ДД.ММ.ГГГГ."""
    try:
        return datetime.strptime(raw.strip(), "%d.%m.%Y").date()
    except ValueError:
        raise ValidationError("Дата должна быть в формате ДД.ММ.ГГГГ.") from None


def parse_time(raw: str) -> time:
    """Разбирает время в формате ЧЧ:ММ."""
    try:
        return datetime.strptime(raw.strip(), "%H:%M").time()
    except ValueError:
        raise ValidationError("Время должно быть в формате ЧЧ:ММ.") from None
