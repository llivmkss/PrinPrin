"""Действия администратора: вход, просмотр броней и занятости столиков."""

from console import Console
from errors import AuthenticationError
from formatters import format_booking, format_booking_row, format_occupancy
from models import Admin
from services import AuthService, BookingService
from validators import parse_booking_id, parse_date


class AdminMenu:
    """Сценарии администратора ресторана."""

    def __init__(
        self,
        console: Console,
        auth: AuthService,
        bookings: BookingService,
    ) -> None:
        """Принимает консоль, сервис аутентификации и сервис бронирования."""
        self._console = console
        self._auth = auth
        self._bookings = bookings

    def enter(self) -> None:
        """Выполняет вход и открывает панель администратора."""
        admin = self._authenticate()
        if admin is None:
            return
        self._console.say(f"Вы вошли как {admin.login}.")
        self._console.run_menu(
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
        bookings = self._bookings.list_bookings()
        if not bookings:
            self._console.say("Бронирований пока нет.")
            return
        for booking in bookings:
            self._console.say(format_booking_row(booking))

    def show_booking(self) -> None:
        """Показывает подробности бронирования по идентификатору."""
        booking_id = self._console.ask_parsed(
            "Идентификатор бронирования", parse_booking_id
        )
        self._console.say(format_booking(self._bookings.get_booking(booking_id)))

    def show_occupancy(self) -> None:
        """Показывает занятость всех столиков на выбранную дату."""
        day = self._console.ask_parsed("Дата (ДД.ММ.ГГГГ)", parse_date)
        for occupancy in self._bookings.occupancy_for_date(day):
            self._console.say(format_occupancy(occupancy))

    def _authenticate(self) -> Admin | None:
        """Запрашивает логин и пароль, пока вход не удался или клиент не отказался."""
        while True:
            login = self._console.ask("Логин")
            password = self._console.ask_secret("Пароль")
            try:
                return self._auth.login(login, password)
            except AuthenticationError as error:
                self._console.say(str(error))
                if not self._console.confirm("Повторить ввод?"):
                    return None
