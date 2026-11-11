"""Главное меню консольного приложения."""

from collections.abc import Callable
from contextlib import suppress

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from src.admin_menu import AdminMenu
from src.client_menu import ClientMenu
from src.console import Console


class ConsoleApp:
    """Собирает главное меню из действий клиента и входа администратора."""

    def __init__(
        self,
        console: Console,
        session_factory: sessionmaker[Session],
        client_factory: Callable[[Session], ClientMenu],
        admin_factory: Callable[[Session], AdminMenu],
    ) -> None:
        """Принимает консоль, фабрику сессий и фабрики двух меню приложения."""
        self.__console: Console = console
        self.__session_factory: sessionmaker[Session] = session_factory
        self.__client_factory: Callable[[Session], ClientMenu] = client_factory
        self.__admin_factory: Callable[[Session], AdminMenu] = admin_factory

    def run(self) -> None:
        """Запускает главное меню и работает до выбора пункта «Выход»."""
        self.__console.say("Онлайн-бронирование столиков")
        with suppress(EOFError, KeyboardInterrupt):
            self.__console.run_menu(
                "Главное меню",
                [
                    (
                        "Информация о ресторане",
                        self.__in_client_session(ClientMenu.show_info),
                    ),
                    (
                        "Забронировать столик",
                        self.__in_client_session(ClientMenu.book),
                    ),
                    (
                        "Отменить бронирование",
                        self.__in_client_session(ClientMenu.cancel),
                    ),
                    (
                        "Вход для администратора",
                        self.__in_admin_session(AdminMenu.enter),
                    ),
                ],
                "Выход",
            )
        self.__console.say("До свидания!")

    def __in_client_session(
        self, action: Callable[[ClientMenu], None]
    ) -> Callable[[], None]:
        """Оборачивает действие клиента: своя сессия и сохранение в конце."""

        def run() -> None:
            with self.__session_factory() as session:
                action(self.__client_factory(session))
                session.commit()

        return run

    def __in_admin_session(
        self, action: Callable[[AdminMenu], None]
    ) -> Callable[[], None]:
        """Оборачивает действие администратора: своя сессия и сохранение в конце."""

        def run() -> None:
            with self.__session_factory() as session:
                action(self.__admin_factory(session))
                session.commit()

        return run
