"""Действия клиента: информация о ресторане, бронирование, отмена."""

from datetime import datetime

from src.console import CANCEL_WORD
from src.console import Console
from src.errors import TableUnavailableError
from src.formatters import Formatter
from src.models import Booking
from src.models import Restaurant
from src.models import Table
from src.services import BookingService


class ClientMenu:
    """Сценарии клиента ресторана."""

    def __init__(
        self,
        console: Console,
        restaurant: Restaurant,
        bookings: BookingService,
        formatter: Formatter,
    ) -> None:
        """Принимает консоль, данные о ресторане, сервис бронирования и форматтер."""
        self.__console: Console = console
        self.__restaurant: Restaurant = restaurant
        self.__bookings: BookingService = bookings
        self.__formatter: Formatter = formatter

    def show_info(self) -> None:
        """Показывает информацию о ресторане."""
        self.__console.say(self.__formatter.format_restaurant(self.__restaurant))

    def book(self) -> None:
        """Ведёт клиента от выбора даты до подтверждения бронирования."""
        self.__console.say(f"Для отказа на любом шаге введите «{CANCEL_WORD}».")
        start = self.__ask_start()
        guests = self.__console.ask_positive_int("Количество гостей")
        table = self.__choose_table(start, guests)
        if table is None:
            return
        name = self.__console.ask_parsed("Ваше имя", Booking.validate_name)
        phone = self.__console.ask_parsed(
            "Телефон (+7XXXXXXXXXX)", Booking.validate_phone
        )
        while True:
            try:
                booking = self.__bookings.create_booking(
                    table.number, start, guests, name, phone
                )
            except TableUnavailableError as error:
                self.__console.say(f"{error} Выберите другой столик.")
                table = self.__choose_table(start, guests)
                if table is None:
                    return
            else:
                break
        self.__console.say("Бронирование создано. Сохраните номер для отмены!")
        self.__console.say(self.__formatter.format_booking(booking))

    def cancel(self) -> None:
        """Отменяет бронирование по идентификатору после подтверждения."""
        booking_id = self.__console.ask_positive_int("Идентификатор бронирования")
        booking = self.__bookings.get_booking(booking_id)
        self.__bookings.ensure_cancellable(booking)
        self.__console.say(self.__formatter.format_booking(booking))
        if not self.__console.confirm("Отменить это бронирование?"):
            self.__console.say("Бронирование сохранено.")
            return
        self.__bookings.cancel_booking(booking_id)
        self.__console.say("Бронирование отменено.")

    def __ask_start(self) -> datetime:
        """Запрашивает дату и время посещения."""
        day = self.__console.ask_date("Дата посещения")
        at = self.__console.ask_time("Время посещения")
        return datetime.combine(day, at)

    def __choose_table(self, start: datetime, guests: int) -> Table | None:
        """Показывает свободные столики и возвращает выбранный или None."""
        tables = self.__bookings.find_available_tables(start, guests)
        if not tables:
            self.__console.say(
                "На выбранные дату, время и количество гостей свободных столиков "
                "нет. Попробуйте изменить параметры поиска."
            )
            return None
        self.__console.say("Свободные столики:")
        for table in tables:
            self.__console.say(self.__formatter.format_table(table))
        tables_by_number = {table.number: table for table in tables}
        while True:
            number = self.__console.ask_positive_int("Номер столика")
            if number in tables_by_number:
                return tables_by_number[number]
            self.__console.say("Выберите столик из списка выше.")
