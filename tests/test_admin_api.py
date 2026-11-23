"""Тесты защищённых административных маршрутов FastAPI."""

from base64 import b64encode
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from fastapi.testclient import TestClient

from marusya.api.dependencies import get_auth_service
from marusya.api.dependencies import get_booking_service
from marusya.api.dependencies import get_session
from marusya.api.main import app
from marusya.models import Admin
from marusya.models import BookingStatus
from marusya.models import Table
from marusya.repositories import InMemoryAdminRepository
from marusya.repositories import InMemoryBookingRepository
from marusya.repositories import InMemoryTableRepository
from marusya.security import PasswordHasher
from marusya.services import AuthService
from marusya.services import BookingService


class TestAdminAPI(TestCase):
    """Проверяет административные маршруты без PostgreSQL."""

    def setUp(self) -> None:
        """Подготавливает сервисы и тестовую учётную запись."""
        tables = InMemoryTableRepository(
            [
                Table(number=1, capacity=2, zone="Основной зал"),
                Table(number=2, capacity=4, zone="У окна"),
            ]
        )
        bookings = InMemoryBookingRepository()

        self.booking_service = BookingService(
            tables,
            bookings,
            clock=lambda: datetime(2029, 1, 1),
        )

        self.booking = self.booking_service.create_booking(
            table_number=1,
            start=datetime(2030, 5, 12, 19, 0),
            guests=2,
            customer_name="Анна",
            customer_phone="+79991234567",
        )

        hasher = PasswordHasher()
        admins = InMemoryAdminRepository(
            [
                Admin(
                    login="admin",
                    password_hash=hasher.make_hash("test-password"),
                ),
            ]
        )
        self.auth_service = AuthService(admins, hasher)
        self.session = Mock()

        app.dependency_overrides[get_booking_service] = lambda: self.booking_service
        app.dependency_overrides[get_auth_service] = lambda: self.auth_service
        app.dependency_overrides[get_session] = lambda: self.session

        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.addCleanup(app.dependency_overrides.clear)

    @staticmethod
    def auth_headers(
        password: str = "test-password",
    ) -> dict[str, str]:
        """Создаёт заголовок HTTP Basic для тестовой учётной записи."""
        credentials = f"admin:{password}"
        encoded = b64encode(credentials.encode("utf-8")).decode("ascii")

        return {"Authorization": f"Basic {encoded}"}

    def test_admin_requires_authentication(self) -> None:
        """Без авторизации список бронирований недоступен."""
        response = self.client.get("/api/admin/bookings")

        self.assertEqual(response.status_code, 401)

    def test_admin_rejects_wrong_password(self) -> None:
        """Неверный пароль администратора отклоняется."""
        response = self.client.get(
            "/api/admin/bookings",
            headers=self.auth_headers("wrong-password"),
        )

        self.assertEqual(response.status_code, 401)

    def test_admin_lists_bookings(self) -> None:
        """Авторизованный администратор видит бронирования."""
        response = self.client.get(
            "/api/admin/bookings",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.booking.id)

    def test_admin_gets_booking(self) -> None:
        """Администратор получает бронирование по идентификатору."""
        response = self.client.get(
            f"/api/admin/bookings/{self.booking.id}",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["customer_name"], "Анна")

    def test_admin_booking_not_found(self) -> None:
        """Несуществующее бронирование возвращает ошибку 404."""
        response = self.client.get(
            "/api/admin/bookings/999",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_views_occupancy(self) -> None:
        """Администратор видит занятость столиков на дату."""
        response = self.client.get(
            "/api/admin/occupancy",
            params={"day": "2030-05-12"},
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)

        occupancies = response.json()

        self.assertEqual(len(occupancies), 2)
        self.assertEqual(occupancies[0]["table"]["number"], 1)
        self.assertEqual(
            occupancies[0]["bookings"][0]["id"],
            self.booking.id,
        )
        self.assertEqual(occupancies[1]["bookings"], [])

    def test_admin_cancels_booking(self) -> None:
        """Администратор отменяет бронь, а изменение сохраняется."""
        response = self.client.post(
            f"/api/admin/bookings/{self.booking.id}/cancel",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "отменено")

        booking = self.booking_service.get_booking(self.booking.id)

        self.assertEqual(booking.status, BookingStatus.CANCELLED)
        self.session.commit.assert_called_once()

    def test_admin_cannot_cancel_twice(self) -> None:
        """Повторная отмена возвращает конфликт 409."""
        url = f"/api/admin/bookings/{self.booking.id}/cancel"

        first = self.client.post(
            url,
            headers=self.auth_headers(),
        )
        second = self.client.post(
            url,
            headers=self.auth_headers(),
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.session.commit.assert_called_once()

    def test_admin_cannot_cancel_missing_booking(self) -> None:
        """Нельзя отменить несуществующее бронирование."""
        response = self.client.post(
            "/api/admin/bookings/999/cancel",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 404)
        self.session.commit.assert_not_called()

    def test_unauthorized_user_cannot_cancel(self) -> None:
        """Пользователь без пароля не может отменить чужую бронь."""
        response = self.client.post(
            f"/api/admin/bookings/{self.booking.id}/cancel",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            self.booking_service.get_booking(self.booking.id).status,
            BookingStatus.ACTIVE,
        )
        self.session.commit.assert_not_called()

    def test_invalid_booking_id(self) -> None:
        """Нулевой идентификатор бронирования отклоняется."""
        response = self.client.get(
            "/api/admin/bookings/0",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 422)
