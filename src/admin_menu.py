"""Действия администратора: вход, просмотр броней и занятости столиков."""

from src.console import Console
from src.errors import AuthenticationError
from src.formatters import Formatter
from src.models import Admin
from src.services import AuthService
from src.services import BookingService


class AdminMenu:
    """Сценарии администратора ресторана."""

    def __init__(
        self,
        console: Console,
        auth: AuthService,
        bookings: BookingService,
        formatter: Formatter,
    ) -> None:
        """Принимает консоль, сервисы аутентификации и бронирования и форматтер."""
        self.__console: Console = console
        self.__auth: AuthService = auth
        self.__bookings: BookingService = bookings
        self.__formatter: Formatter = formatter

    def enter(self) -> None:
        """Выполняет вход и открывает панель администратора."""
        admin = self.__authenticate()
        if admin is None:
            return
        self.__console.say(f"Вы вошли как {admin.login}.")
        self.__console.run_menu(
            "Панель администратора",
            [
                ("Список бронирований", self.show_bookings),
                ("Информация о бронировании", self.show_booking),
                ("Занятость столиков на дату", self.show_occupancy),
            ],
            "Выйти из панели администратора",
        )

    def show_bookings(self) -> None:
        """Показывает список всех бронирований."""
        bookings = self.__bookings.list_bookings()
        if not bookings:
            self.__console.say("Бронирований пока нет.")
            return
        for booking in bookings:
            self.__console.say(self.__formatter.format_booking_row(booking))

    def show_booking(self) -> None:
        """Показывает подробности бронирования по идентификатору."""
        booking_id = self.__console.ask_positive_int("Идентификатор бронирования")
        booking = self.__bookings.get_booking(booking_id)
        self.__console.say(self.__formatter.format_booking(booking))

    def show_occupancy(self) -> None:
        """Показывает занятость всех столиков на выбранную дату."""
        day = self.__console.ask_date("Дата")
        for occupancy in self.__bookings.occupancy_for_date(day):
            self.__console.say(self.__formatter.format_occupancy(occupancy))

    def __authenticate(self) -> Admin | None:
        """Запрашивает логин и пароль, пока вход не удался или клиент не отказался."""
        while True:
            login = self.__console.ask("Логин")
            password = self.__console.ask_secret("Пароль")
            try:
                return self.__auth.login(login, password)
            except AuthenticationError as error:
                self.__console.say(str(error))
                if not self.__console.confirm("Повторить ввод?"):
                    return None
