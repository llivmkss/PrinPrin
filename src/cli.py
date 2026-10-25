"""Главное меню консольного приложения."""

from contextlib import suppress

from admin_menu import AdminMenu
from client_menu import ClientMenu
from console import Console


class ConsoleApp:
    """Собирает главное меню из действий клиента и входа администратора."""

    def __init__(
        self,
        console: Console,
        client: ClientMenu,
        admin: AdminMenu,
    ) -> None:
        """Принимает консоль и два меню приложения."""
        self._console = console
        self._client = client
        self._admin = admin

    def run(self) -> None:
        """Запускает главное меню и работает до выбора пункта «Выход»."""
        self._console.say("Онлайн-бронирование столиков")
        with suppress(EOFError, KeyboardInterrupt):
            self._console.run_menu(
                "Главное меню",
                [
                    ("Информация о ресторане", self._client.show_info),
                    ("Забронировать столик", self._client.book),
                    ("Отменить бронирование", self._client.cancel),
                    ("Вход для администратора", self._admin.enter),
                ],
                "Выход",
            )
        self._console.say("До свидания!")
