"""Тесты FastAPI без подключения к реальной базе данных."""

from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from fastapi.testclient import TestClient

from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_session
from marusya.api.main import app
from marusya.models import Table
from marusya.repositories import InMemoryBookingRepository
from marusya.repositories import InMemoryTableRepository
from marusya.services import BookingService


class TestBookingAPI(TestCase):
    """Проверяет основные HTTP-маршруты бронирования."""

    def setUp(self) -> None:
        """Создаёт изолированные зависимости для каждого теста."""
        tables = InMemoryTableRepository(
            [
                Table(number=1, capacity=2, zone="Основной зал"),
                Table(number=2, capacity=4, zone="У окна"),
            ]
        )
        bookings = InMemoryBookingRepository()

        self.service = BookingService(
            tables,
            bookings,
            clock=lambda: datetime(2029, 1, 1),
        )
        self.session = Mock()

        app.dependency_overrides[get_booking_service] = lambda: self.service
        app.dependency_overrides[get_session] = lambda: self.session

        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(self.client.close)

    @staticmethod
    def booking_data() -> dict[str, str | int]:
        """Возвращает корректные данные для создания бронирования."""
        return {
            "table_number": 1,
            "start": "2030-05-12T19:00:00",
            "guests": 2,
            "customer_name": "Анна",
            "customer_phone": "+79991234567",
        }

    def test_restaurant_information(self) -> None:
        """API возвращает название ресторана."""
        response = self.client.get("/api/restaurant")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Маруся")

    def test_available_tables(self) -> None:
        """Возвращает столики с достаточной вместимостью."""
        response = self.client.get(
            "/api/tables/available",
            params={
                "start": "2030-05-12T19:00:00",
                "guests": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [table["number"] for table in response.json()],
            [1, 2],
        )

    def test_no_suitable_tables(self) -> None:
        """При отсутствии подходящих столиков возвращает пустой список."""
        response = self.client.get(
            "/api/tables/available",
            params={
                "start": "2030-05-12T19:00:00",
                "guests": 10,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_guest_count(self) -> None:
        """Нулевое число гостей отклоняется Pydantic."""
        response = self.client.get(
            "/api/tables/available",
            params={
                "start": "2030-05-12T19:00:00",
                "guests": 0,
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_past_booking_date(self) -> None:
        """Дата в прошлом отклоняется бизнес-логикой."""
        response = self.client.get(
            "/api/tables/available",
            params={
                "start": "2020-05-12T19:00:00",
                "guests": 2,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking(self) -> None:
        """Успешная бронь возвращает статус 201 и сохраняется."""
        response = self.client.post(
            "/api/bookings",
            json=self.booking_data(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 1)
        self.assertEqual(response.json()["status"], "активно")
        self.session.commit.assert_called_once()

    def test_conflicting_booking(self) -> None:
        """Повторное бронирование занятого столика возвращает 409."""
        self.client.post(
            "/api/bookings",
            json=self.booking_data(),
        )

        response = self.client.post(
            "/api/bookings",
            json=self.booking_data(),
        )

        self.assertEqual(response.status_code, 409)
        self.session.commit.assert_called_once()

    def test_invalid_phone(self) -> None:
        """Некорректный телефон не допускается при создании брони."""
        data = self.booking_data()
        data["customer_phone"] = "12345"

        response = self.client.post(
            "/api/bookings",
            json=data,
        )

        self.assertEqual(response.status_code, 422)
        self.session.commit.assert_not_called()

    def test_openapi_documentation(self) -> None:
        """FastAPI генерирует спецификацию OpenAPI."""
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/bookings", response.json()["paths"])
