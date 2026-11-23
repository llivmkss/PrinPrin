"""Зависимости FastAPI для работы с базой данных и сервисами."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from marusya.database.repositories import SqlAdminRepository
from marusya.database.repositories import SqlBookingRepository
from marusya.database.repositories import SqlTableRepository
from marusya.database.session import SessionFactory
from marusya.errors import AuthenticationError
from marusya.models import Admin
from marusya.security import PasswordHasher
from marusya.services import AuthService
from marusya.services import BookingService

basic_security = HTTPBasic()


def get_session() -> Iterator[Session]:
    """Предоставляет отдельную сессию базы данных для HTTP-запроса."""
    with SessionFactory() as session:
        yield session


def get_booking_service(
    session: Annotated[Session, Depends(get_session)],
) -> BookingService:
    """Создаёт сервис бронирования с SQL-репозиториями."""
    return BookingService(
        SqlTableRepository(session),
        SqlBookingRepository(session),
    )


def get_auth_service(
    session: Annotated[Session, Depends(get_session)],
) -> AuthService:
    """Создаёт сервис аутентификации администратора."""
    return AuthService(
        SqlAdminRepository(session),
        PasswordHasher(),
    )


def get_current_admin(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Admin:
    """Проверяет учётные данные администратора для защищённого API."""
    try:
        return auth_service.login(
            credentials.username,
            credentials.password,
        )
    except AuthenticationError as error:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль.",
            headers={"WWW-Authenticate": "Basic"},
        ) from error
