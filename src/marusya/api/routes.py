"""Маршруты API для информации о ресторане и бронирований."""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from sqlalchemy.orm import Session

from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_session
from marusya.dtos.requests import AvailableTablesRequest
from marusya.dtos.requests import CreateBookingRequest
from marusya.dtos.responses import BookingResponse
from marusya.dtos.responses import RestaurantResponse
from marusya.dtos.responses import TableResponse
from marusya.seed import RESTAURANT
from marusya.services import BookingService

router = APIRouter(prefix="/api", tags=["Бронирование"])


@router.get("/restaurant", response_model=RestaurantResponse)
def get_restaurant() -> RestaurantResponse:
    """Возвращает информацию о ресторане."""
    return RestaurantResponse.model_validate(RESTAURANT)


@router.get("/tables/available", response_model=list[TableResponse])
def get_available_tables(
    params: Annotated[AvailableTablesRequest, Query()],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> list[TableResponse]:
    """Ищет свободные столики на выбранное время."""
    tables = service.find_available_tables(
        start=params.start,
        guests=params.guests,
    )

    return [TableResponse.model_validate(table) for table in tables]


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=201,
)
def create_booking(
    request: CreateBookingRequest,
    service: Annotated[BookingService, Depends(get_booking_service)],
    session: Annotated[Session, Depends(get_session)],
) -> BookingResponse:
    """Создаёт бронирование и сохраняет его в базе данных."""
    booking = service.create_booking(
        table_number=request.table_number,
        start=request.start,
        guests=request.guests,
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
    )

    response = BookingResponse.model_validate(booking)

    session.commit()

    return response
