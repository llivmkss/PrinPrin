"""Ввод и вывод в консоли: вопросы пользователю, подтверждения, меню."""

import getpass
from collections.abc import Callable
from datetime import date
from datetime import datetime
from datetime import time
from functools import partial
from typing import TypeVar

from src.errors import AppError
from src.errors import ValidationError

T = TypeVar("T")

CANCEL_WORD: str = "отмена"
_YES_ANSWERS: set[str] = {"да", "д", "yes", "y"}


class InputCancelled(Exception):
    """Пользователь ввёл слово «отмена» и отказался от текущего действия."""


class Console:
    """Обёртка над вводом и выводом; функции ввода и вывода можно подменять."""

    def __init__(
        self,
        reader: Callable[[str], str] = input,
        writer: Callable[[str], None] = print,
        secret_reader: Callable[[str], str] = getpass.getpass,
    ) -> None:
        """Принимает функции чтения, вывода и скрытого чтения пароля."""
        self.__reader: Callable[[str], str] = reader
        self.__writer: Callable[[str], None] = writer
        self.__secret_reader: Callable[[str], str] = secret_reader

    def say(self, text: str = "") -> None:
        """Выводит строку текста."""
        self.__writer(text)

    def ask(self, prompt: str) -> str:
        """Запрашивает строку; слово «отмена» прерывает текущее действие."""
        answer = self.__reader(f"{prompt}: ").strip()
        if answer.lower() == CANCEL_WORD:
            raise InputCancelled
        return answer

    def ask_secret(self, prompt: str) -> str:
        """Запрашивает пароль без отображения вводимых символов."""
        return self.__secret_reader(f"{prompt}: ")

    def ask_parsed(self, prompt: str, parser: Callable[[str], T]) -> T:
        """Повторяет вопрос, пока parser не примет ответ без ошибки валидации."""
        while True:
            try:
                return parser(self.ask(prompt))
            except ValidationError as error:
                self.say(str(error))

    def ask_positive_int(self, prompt: str) -> int:
        """Запрашивает целое положительное число, пока ответ не станет верным."""
        return self.ask_parsed(prompt, partial(self.__parse_positive_int, field=prompt))

    def ask_date(self, prompt: str) -> date:
        """Запрашивает дату в формате ДД.ММ.ГГГГ, пока ответ не станет верным."""
        return self.ask_parsed(f"{prompt} (ДД.ММ.ГГГГ)", self.__parse_date)

    def ask_time(self, prompt: str) -> time:
        """Запрашивает время в формате ЧЧ:ММ, пока ответ не станет верным."""
        return self.ask_parsed(f"{prompt} (ЧЧ:ММ)", self.__parse_time)

    def confirm(self, prompt: str) -> bool:
        """Задаёт вопрос «да/нет» и возвращает True только на утвердительный ответ."""
        return self.ask(f"{prompt} (да/нет)").lower() in _YES_ANSWERS

    def run_menu(
        self,
        title: str,
        actions: list[tuple[str, Callable[[], None]]],
        exit_label: str,
    ) -> None:
        """Показывает меню и выполняет выбранные действия, пока не выбран пункт 0."""
        while True:
            self.say()
            self.say(title)
            for number, (label, _) in enumerate(actions, start=1):
                self.say(f"{number}. {label}")
            self.say(f"0. {exit_label}")
            choice = self.__reader("Выберите пункт: ").strip()
            if choice == "0":
                return
            if not choice.isdigit() or not 1 <= int(choice) <= len(actions):
                self.say("Такого пункта нет в меню.")
                continue
            self.__run_action(actions[int(choice) - 1][1])

    def __run_action(self, action: Callable[[], None]) -> None:
        """Выполняет действие и превращает любые сбои в понятные сообщения."""
        try:
            action()
        except InputCancelled:
            self.say("Действие отменено.")
        except AppError as error:
            self.say(str(error))
        except EOFError:
            raise
        except Exception:
            self.say("Произошла внутренняя ошибка. Повторите попытку позже.")

    @staticmethod
    def __parse_positive_int(raw: str, field: str) -> int:
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

    @staticmethod
    def __parse_date(raw: str) -> date:
        """Разбирает дату в формате ДД.ММ.ГГГГ."""
        try:
            return datetime.strptime(raw.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise ValidationError("Дата должна быть в формате ДД.ММ.ГГГГ.") from None

    @staticmethod
    def __parse_time(raw: str) -> time:
        """Разбирает время в формате ЧЧ:ММ."""
        try:
            return datetime.strptime(raw.strip(), "%H:%M").time()
        except ValueError:
            raise ValidationError("Время должно быть в формате ЧЧ:ММ.") from None
