"""Превращение объектов предметной области в текст для вывода в консоль."""

from models import Booking, Restaurant, Table
from services import TableOccupancy


def format_restaurant(restaurant: Restaurant) -> str:
    """Форматирует информацию о ресторане."""
    return "\n".join(
        [
            f"Ресторан «{restaurant.name}»",
            f"Адрес: {restaurant.address}",
            f"Часы работы: {restaurant.working_hours()}",
            f"Телефон: {restaurant.phone}",
        ]
    )


def format_table(table: Table) -> str:
    """Форматирует столик одной строкой."""
    return f"Столик №{table.number}: мест — {table.capacity}, зона — {table.zone}"


def format_booking(booking: Booking) -> str:
    """Форматирует подробную информацию о бронировании."""
    return "\n".join(
        [
            f"Бронирование №{booking.id}",
            f"Дата: {booking.start:%d.%m.%Y}",
            f"Время: {booking.start:%H:%M}–{booking.end:%H:%M}",
            f"Столик: №{booking.table_number}",
            f"Гостей: {booking.guests}",
            f"Имя: {booking.customer_name}",
            f"Телефон: {booking.customer_phone}",
            f"Статус: {booking.status.value}",
        ]
    )


def format_booking_row(booking: Booking) -> str:
    """Форматирует бронирование одной строкой для списка."""
    return (
        f"№{booking.id} | {booking.start:%d.%m.%Y} "
        f"{booking.start:%H:%M}–{booking.end:%H:%M} | "
        f"столик {booking.table_number} | гостей {booking.guests} | "
        f"{booking.customer_name}, {booking.customer_phone} | "
        f"{booking.status.value}"
    )


def format_occupancy(occupancy: TableOccupancy) -> str:
    """Форматирует занятость столика за день."""
    header = format_table(occupancy.table)
    if not occupancy.bookings:
        return f"{header}\n    свободен весь день"
    lines = [
        f"    {booking.start:%H:%M}–{booking.end:%H:%M} "
        f"(бронь №{booking.id}, {booking.customer_name})"
        for booking in occupancy.bookings
    ]
    return "\n".join([header, *lines])
