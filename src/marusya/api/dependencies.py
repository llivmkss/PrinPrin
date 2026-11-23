"""Зависимости FastAPI для работы с базой данных и сервисами."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from marusya.database.repositories import SqlBookingRepository
from marusya.database.repositories import SqlTableRepository
from marusya.database.session import SessionFactory
from marusya.services import BookingService


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
