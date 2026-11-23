"""Защищённые HTTP-маршруты администратора ресторана."""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from sqlalchemy.orm import Session

from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_current_admin
from marusya.api.dependencies import get_session
from marusya.dtos.requests import OccupancySearchRequest
from marusya.dtos.responses import BookingResponse
from marusya.dtos.responses import TableOccupancyResponse
from marusya.services import BookingService

router = APIRouter(
    prefix="/api/admin",
    tags=["Администратор"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> list[BookingResponse]:
    """Возвращает список всех бронирований для администратора."""
    bookings = service.list_bookings()

    return [BookingResponse.model_validate(booking) for booking in bookings]


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: Annotated[int, Path(gt=0)],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> BookingResponse:
    """Возвращает информацию о бронировании по идентификатору."""
    booking = service.get_booking(booking_id)
    return BookingResponse.model_validate(booking)


@router.get(
    "/occupancy",
    response_model=list[TableOccupancyResponse],
)
def get_occupancy(
    params: Annotated[OccupancySearchRequest, Query()],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> list[TableOccupancyResponse]:
    """Возвращает занятость столиков на выбранную дату."""
    occupancies = service.occupancy_for_date(params.day)

    return [
        TableOccupancyResponse.model_validate(occupancy) for occupancy in occupancies
    ]


@router.post(
    "/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: Annotated[int, Path(gt=0)],
    service: Annotated[BookingService, Depends(get_booking_service)],
    session: Annotated[Session, Depends(get_session)],
) -> BookingResponse:
    """Отменяет бронирование от имени администратора."""
    booking = service.cancel_booking(booking_id)

    response = BookingResponse.model_validate(booking)

    session.commit()

    return response
