"""Исключения предметной области."""


class AppError(Exception):
    """Базовое исключение приложения. Его текст безопасно показывать клиенту."""


class ValidationError(AppError):
    """Пользователь ввёл некорректные данные."""


class TableUnavailableError(AppError):
    """Выбранный столик не существует, не подходит или уже занят."""


class BookingNotFoundError(AppError):
    """Бронирование с указанным идентификатором не найдено."""


class CancellationError(AppError):
    """Бронирование нельзя отменить: оно уже отменено или срок его действия истёк."""


class AuthenticationError(AppError):
    """Неверный логин или пароль администратора."""
