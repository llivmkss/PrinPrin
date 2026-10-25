"""Действия клиента: информация о ресторане, бронирование, отмена."""

from datetime import datetime

from console import CANCEL_WORD, Console
from errors import TableUnavailableError
from formatters import format_booking, format_restaurant, format_table
from models import Restaurant, Table
from services import BookingService
from validators import (
    parse_booking_id,
    parse_date,
    parse_guests,
    parse_table_number,
    parse_time,
    validate_name,
    validate_phone,
)


class ClientMenu:
    """Сценарии клиента ресторана."""

    def __init__(
        self,
        console: Console,
        restaurant: Restaurant,
        bookings: BookingService,
    ) -> None:
        """Принимает консоль, данные о ресторане и сервис бронирования."""
        self._console = console
        self._restaurant = restaurant
        self._bookings = bookings

    def show_info(self) -> None:
        """Показывает информацию о ресторане."""
        self._console.say(format_restaurant(self._restaurant))

    def book(self) -> None:
        """Ведёт клиента от выбора даты до подтверждения бронирования."""
        self._console.say(f"Для отказа на любом шаге введите «{CANCEL_WORD}».")
        start = self._ask_start()
        guests = self._console.ask_parsed("Количество гостей", parse_guests)
        table = self._choose_table(start, guests)
        if table is None:
            return
        name = self._console.ask_parsed("Ваше имя", validate_name)
        phone = self._console.ask_parsed("Телефон (+7XXXXXXXXXX)", validate_phone)
        while True:
            try:
                booking = self._bookings.create_booking(
                    table.number, start, guests, name, phone
                )
            except TableUnavailableError as error:
                self._console.say(f"{error} Выберите другой столик.")
                table = self._choose_table(start, guests)
                if table is None:
                    return
            else:
                break
        self._console.say("Бронирование создано. Сохраните номер для отмены!")
        self._console.say(format_booking(booking))

    def cancel(self) -> None:
        """Отменяет бронирование по идентификатору после подтверждения."""
        booking_id = self._console.ask_parsed(
            "Идентификатор бронирования", parse_booking_id
        )
        booking = self._bookings.get_booking(booking_id)
        self._bookings.ensure_cancellable(booking)
        self._console.say(format_booking(booking))
        if not self._console.confirm("Отменить это бронирование?"):
            self._console.say("Бронирование сохранено.")
            return
        self._bookings.cancel_booking(booking_id)
        self._console.say("Бронирование отменено.")

    def _ask_start(self) -> datetime:
        """Запрашивает дату и время посещения."""
        day = self._console.ask_parsed("Дата посещения (ДД.ММ.ГГГГ)", parse_date)
        at = self._console.ask_parsed("Время посещения (ЧЧ:ММ)", parse_time)
        return datetime.combine(day, at)

    def _choose_table(self, start: datetime, guests: int) -> Table | None:
        """Показывает свободные столики и возвращает выбранный или None."""
        tables = self._bookings.find_available_tables(start, guests)
        if not tables:
            self._console.say(
                "На выбранные дату, время и количество гостей свободных столиков "
                "нет. Попробуйте изменить параметры поиска."
            )
            return None
        self._console.say("Свободные столики:")
        for table in tables:
            self._console.say(format_table(table))
        by_number = {table.number: table for table in tables}
        while True:
            number = self._console.ask_parsed("Номер столика", parse_table_number)
            if number in by_number:
                return by_number[number]
            self._console.say("Выберите столик из списка выше.")
