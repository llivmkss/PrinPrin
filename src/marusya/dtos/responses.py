"""Схемы ответов веб-приложения ресторана «Маруся»."""

from datetime import datetime
from datetime import time

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from marusya.models import BookingStatus


class DomainResponse(BaseModel):
    """Базовая схема для преобразования объектов предметной области."""

    model_config = ConfigDict(from_attributes=True)


class RestaurantResponse(DomainResponse):
    """Информация о ресторане."""

    name: str = Field(
        description="Название ресторана.",
        examples=["Маруся"],
    )
    address: str = Field(
        description="Адрес ресторана.",
        examples=["г. Волгоград, ул. Аллея героев, 1"],
    )
    opens_at: time = Field(
        description="Время открытия.",
        examples=["09:00:00"],
    )
    closes_at: time = Field(
        description="Время закрытия.",
        examples=["23:00:00"],
    )
    phone: str = Field(
        description="Контактный телефон.",
        examples=["+7 (8442) 59-59-24"],
    )


class TableResponse(DomainResponse):
    """Информация о столике."""

    number: int = Field(
        description="Номер столика.",
        examples=[3],
    )
    capacity: int = Field(
        description="Вместимость столика.",
        examples=[4],
    )
    zone: str = Field(
        description="Зона ресторана.",
        examples=["Основной зал"],
    )
    is_available: bool = Field(
        description="Доступен ли столик для бронирования.",
        examples=[True],
    )


class BookingResponse(DomainResponse):
    """Информация о бронировании."""

    id: int = Field(
        description="Идентификатор бронирования.",
        examples=[1],
    )
    table_number: int = Field(
        description="Номер забронированного столика.",
        examples=[3],
    )
    guests: int = Field(
        description="Количество гостей.",
        examples=[2],
    )
    start: datetime = Field(
        description="Дата и время начала бронирования.",
        examples=["2030-05-12T19:00:00"],
    )
    end: datetime = Field(
        description="Дата и время окончания бронирования.",
        examples=["2030-05-12T21:00:00"],
    )
    customer_name: str = Field(
        description="Имя клиента.",
        examples=["Анна"],
    )
    customer_phone: str = Field(
        description="Телефон клиента.",
        examples=["+79991234567"],
    )
    status: BookingStatus = Field(
        description="Статус бронирования.",
        examples=["активно"],
    )


class TableOccupancyResponse(DomainResponse):
    """Занятость столика и список его действующих бронирований."""

    table: TableResponse = Field(
        description="Информация о столике.",
    )
    bookings: list[BookingResponse] = Field(
        description="Действующие бронирования столика за выбранный день.",
    )
