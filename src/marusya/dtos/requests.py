"""Схемы входящих запросов к веб-приложению ресторана «Маруся»."""

from datetime import date

from pydantic import BaseModel
from pydantic import Field
from pydantic import NaiveDatetime
from pydantic import field_validator

from marusya.errors import ValidationError as DomainValidationError
from marusya.models import Booking


class AvailableTablesRequest(BaseModel):
    """Параметры поиска свободных столиков."""

    start: NaiveDatetime = Field(
        description="Дата и время начала бронирования без часового пояса.",
        examples=["2030-05-12T19:00:00"],
    )
    guests: int = Field(
        gt=0,
        description="Количество гостей.",
        examples=[2],
    )


class CreateBookingRequest(BaseModel):
    """Данные для создания бронирования."""

    table_number: int = Field(
        gt=0,
        description="Номер выбранного столика.",
        examples=[3],
    )
    start: NaiveDatetime = Field(
        description="Дата и время начала бронирования без часового пояса.",
        examples=["2030-05-12T19:00:00"],
    )
    guests: int = Field(
        gt=0,
        description="Количество гостей.",
        examples=[2],
    )
    customer_name: str = Field(
        min_length=1,
        max_length=50,
        description="Имя клиента.",
        examples=["Анна"],
    )
    customer_phone: str = Field(
        min_length=1,
        description="Телефон клиента в российском формате.",
        examples=["+79991234567"],
    )

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value: str) -> str:
        """Проверяет имя существующим правилом предметной области."""
        try:
            return Booking.validate_name(value)
        except DomainValidationError as error:
            raise ValueError(str(error)) from error

    @field_validator("customer_phone")
    @classmethod
    def validate_customer_phone(cls, value: str) -> str:
        """Проверяет и нормализует телефон существующим правилом."""
        try:
            return Booking.validate_phone(value)
        except DomainValidationError as error:
            raise ValueError(str(error)) from error


class AdminLoginRequest(BaseModel):
    """Данные для входа администратора."""

    login: str = Field(
        min_length=1,
        description="Логин администратора.",
        examples=["admin"],
    )
    password: str = Field(
        min_length=1,
        repr=False,
        description="Пароль администратора.",
        examples=["example-password"],
    )


class OccupancySearchRequest(BaseModel):
    """Дата для просмотра занятости столиков."""

    day: date = Field(
        description="Дата, на которую требуется показать занятость.",
        examples=["2030-05-12"],
    )
