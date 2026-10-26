"""Главное меню консольного приложения."""

from contextlib import suppress

from src.admin_menu import AdminMenu
from src.client_menu import ClientMenu
from src.console import Console


class ConsoleApp:
    """Собирает главное меню из действий клиента и входа администратора."""

    def __init__(
        self,
        console: Console,
        client: ClientMenu,
        admin: AdminMenu,
    ) -> None:
        """Принимает консоль и два меню приложения."""
        self.__console: Console = console
        self.__client: ClientMenu = client
        self.__admin: AdminMenu = admin

    def run(self) -> None:
        """Запускает главное меню и работает до выбора пункта «Выход»."""
        self.__console.say("Онлайн-бронирование столиков")
        with suppress(EOFError, KeyboardInterrupt):
            self.__console.run_menu(
                "Главное меню",
                [
                    ("Информация о ресторане", self.__client.show_info),
                    ("Забронировать столик", self.__client.book),
                    ("Отменить бронирование", self.__client.cancel),
                    ("Вход для администратора", self.__admin.enter),
                ],
                "Выход",
            )
        self.__console.say("До свидания!")
