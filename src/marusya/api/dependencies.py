"""Зависимости FastAPI: сессия, сервисы и авторизация."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from marusya.database.session import SessionFactory
from marusya.errors import AuthenticationError
from marusya.models import Admin
from marusya.repository_factories import SqlRepositoryFactory
from marusya.security import PasswordHasher
from marusya.services import AuthService
from marusya.services import BookingService

basic_security = HTTPBasic()


def get_session() -> Iterator[Session]:
    """Предоставляет SQLAlchemy Session для HTTP-запроса."""
    with SessionFactory() as session:
        yield session


def get_booking_service(
    session: Annotated[Session, Depends(get_session)],
) -> BookingService:
    """Создаёт сервис бронирования через SQL-фабрику."""
    factory = SqlRepositoryFactory(session)

    return BookingService(
        factory.create_table_repository(),
        factory.create_booking_repository(),
    )


def get_auth_service(
    session: Annotated[Session, Depends(get_session)],
) -> AuthService:
    """Создаёт сервис аутентификации через SQL-фабрику."""
    factory = SqlRepositoryFactory(session)

    return AuthService(
        factory.create_admin_repository(),
        PasswordHasher(),
    )


def get_current_admin(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Admin:
    """Проверяет учётные данные администратора."""
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
