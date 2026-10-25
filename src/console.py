"""Ввод и вывод в консоли: вопросы пользователю, подтверждения, меню."""

import getpass
from collections.abc import Callable
from typing import TypeVar

from errors import AppError, ValidationError

T = TypeVar("T")

CANCEL_WORD = "отмена"
_YES_ANSWERS = {"да", "д", "yes", "y"}


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
        self._reader = reader
        self._writer = writer
        self._secret_reader = secret_reader

    def say(self, text: str = "") -> None:
        """Выводит строку текста."""
        self._writer(text)

    def ask(self, prompt: str) -> str:
        """Запрашивает строку; слово «отмена» прерывает текущее действие."""
        answer = self._reader(f"{prompt}: ").strip()
        if answer.lower() == CANCEL_WORD:
            raise InputCancelled
        return answer

    def ask_secret(self, prompt: str) -> str:
        """Запрашивает пароль без отображения вводимых символов."""
        return self._secret_reader(f"{prompt}: ")

    def ask_parsed(self, prompt: str, parser: Callable[[str], T]) -> T:
        """Повторяет вопрос, пока parser не примет ответ без ошибки валидации."""
        while True:
            try:
                return parser(self.ask(prompt))
            except ValidationError as error:
                self.say(str(error))

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
            choice = self._reader("Выберите пункт: ").strip()
            if choice == "0":
                return
            if not choice.isdigit() or not 1 <= int(choice) <= len(actions):
                self.say("Такого пункта нет в меню.")
                continue
            self._run_action(actions[int(choice) - 1][1])

    def _run_action(self, action: Callable[[], None]) -> None:
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
