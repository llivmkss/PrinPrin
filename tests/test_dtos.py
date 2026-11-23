"""Проверки Pydantic DTO без подключения к базе данных."""

from datetime import UTC
from datetime import datetime
from datetime import time
from unittest import TestCase

from pydantic import ValidationError as PydanticValidationError

from marusya.dtos.requests import AdminLoginRequest
from marusya.dtos.requests import AvailableTablesRequest
from marusya.dtos.requests import CreateBookingRequest
from marusya.dtos.responses import BookingResponse
from marusya.dtos.responses import RestaurantResponse
from marusya.dtos.responses import TableOccupancyResponse
from marusya.models import BOOKING_DURATION
from marusya.models import Booking
from marusya.models import BookingStatus
from marusya.models import Restaurant
from marusya.models import Table
from marusya.services import TableOccupancy


class TestDTOs(TestCase):
    """Проверяет валидацию запросов и преобразование ответов."""

    def test_search_rejects_zero_guests(self) -> None:
        """Нельзя искать столик для нулевого числа гостей."""
        with self.assertRaises(PydanticValidationError):
            AvailableTablesRequest(
                start=datetime(2030, 5, 12, 19, 0),
                guests=0,
            )

    def test_search_rejects_timezone_aware_start(self) -> None:
        """В текущем проекте время бронирования без часового пояса."""
        with self.assertRaises(PydanticValidationError):
            AvailableTablesRequest(
                start=datetime(2030, 5, 12, 19, 0, tzinfo=UTC),
                guests=2,
            )

    def test_booking_request_normalizes_customer(self) -> None:
        """Имя и телефон нормализуются по правилам Booking."""
        request = CreateBookingRequest(
            table_number=3,
            start=datetime(2030, 5, 12, 19, 0),
            guests=2,
            customer_name="  Анна  ",
            customer_phone="8 (999) 123-45-67",
        )

        self.assertEqual(request.customer_name, "Анна")
        self.assertEqual(request.customer_phone, "89991234567")

    def test_booking_request_rejects_empty_name(self) -> None:
        """Имя из одних пробелов не допускается."""
        with self.assertRaises(PydanticValidationError):
            CreateBookingRequest(
                table_number=3,
                start=datetime(2030, 5, 12, 19, 0),
                guests=2,
                customer_name="   ",
                customer_phone="+79991234567",
            )

    def test_booking_request_rejects_invalid_phone(self) -> None:
        """Некорректный телефон не проходит проверку."""
        with self.assertRaises(PydanticValidationError):
            CreateBookingRequest(
                table_number=3,
                start=datetime(2030, 5, 12, 19, 0),
                guests=2,
                customer_name="Анна",
                customer_phone="12345",
            )

    def test_booking_response_from_domain(self) -> None:
        """Ответ строится из Booking, включая время окончания."""
        booking = Booking(
            id=7,
            table_number=3,
            guests=2,
            start=datetime(2030, 5, 12, 19, 0),
            customer_name="Анна",
            customer_phone="+79991234567",
            status=BookingStatus.ACTIVE,
        )

        response = BookingResponse.model_validate(booking)

        self.assertEqual(response.id, 7)
        self.assertEqual(response.end, booking.start + BOOKING_DURATION)
        self.assertEqual(
            response.model_dump(mode="json")["status"],
            "активно",
        )

    def test_occupancy_response_from_domain(self) -> None:
        """Ответ о занятости преобразует вложенный объект Table."""
        occupancy = TableOccupancy(
            table=Table(number=1, capacity=2, zone="У окна"),
            bookings=[],
        )

        response = TableOccupancyResponse.model_validate(occupancy)

        self.assertEqual(response.table.number, 1)
        self.assertEqual(response.table.zone, "У окна")
        self.assertEqual(response.bookings, [])

    def test_restaurant_response_from_domain(self) -> None:
        """Информация о ресторане преобразуется в DTO."""
        restaurant = Restaurant(
            name="Маруся",
            address="Волгоград",
            opens_at=time(9, 0),
            closes_at=time(23, 0),
            phone="+79991234567",
        )

        response = RestaurantResponse.model_validate(restaurant)

        self.assertEqual(response.name, "Маруся")
        self.assertEqual(response.opens_at, time(9, 0))

    def test_admin_password_hidden_from_repr(self) -> None:
        """Пароль не выводится в текстовом представлении DTO."""
        request = AdminLoginRequest(
            login="admin",
            password="secret-password",
        )

        self.assertNotIn("secret-password", repr(request))
