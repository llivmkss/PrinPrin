"""Тесты веб-панели администратора без PostgreSQL."""

from base64 import b64encode
from unittest import TestCase

from fastapi.testclient import TestClient

from marusya.api.main import create_app
from marusya.seed import ADMIN_LOGIN
from marusya.seed import ADMIN_PASSWORD


class TestAdminWeb(TestCase):
    """Проверяет интерфейс и его работу с административным API."""

    def setUp(self) -> None:
        """Создаёт независимое приложение с InMemory-хранилищем."""
        self.app = create_app(demo_mode=True)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    @staticmethod
    def auth_headers() -> dict[str, str]:
        """Создаёт заголовок для тестового администратора."""
        credentials = f"{ADMIN_LOGIN}:{ADMIN_PASSWORD}"
        encoded = b64encode(credentials.encode("utf-8")).decode("ascii")

        return {"Authorization": f"Basic {encoded}"}

    def create_test_booking(self) -> dict:
        """Создаёт бронирование через клиентский API."""
        response = self.client.post(
            "/api/bookings",
            json={
                "table_number": 1,
                "start": "2030-05-12T19:00:00",
                "guests": 2,
                "customer_name": "Анна",
                "customer_phone": "+79991234567",
            },
        )

        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_admin_page(self) -> None:
        """Страница администратора открывается."""
        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Панель администратора", response.text)
        self.assertIn('id="login-form"', response.text)
        self.assertIn('id="admin-view"', response.text)

        # Пароль не должен передаваться внутри HTML-страницы.
        self.assertNotIn(ADMIN_PASSWORD, response.text)

    def test_admin_stylesheet(self) -> None:
        """Стили панели доступны браузеру."""
        response = self.client.get("/static/admin.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn(".admin-panel", response.text)

    def test_admin_javascript(self) -> None:
        """JavaScript панели доступен браузеру."""
        response = self.client.get("/static/admin.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/admin/bookings", response.text)
        self.assertIn("Authorization", response.text)

    def test_admin_data_requires_authentication(self) -> None:
        """Открытая страница не означает доступ к данным."""
        response = self.client.get("/api/admin/bookings")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_list_bookings(self) -> None:
        """После создания брони администратор видит её в API."""
        booking = self.create_test_booking()

        response = self.client.get(
            "/api/admin/bookings",
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], booking["id"])
        self.assertEqual(
            response.json()[0]["customer_name"],
            "Анна",
        )

    def test_admin_can_view_occupancy(self) -> None:
        """Администратор видит созданную бронь в расписании."""
        booking = self.create_test_booking()

        response = self.client.get(
            "/api/admin/occupancy",
            params={"day": "2030-05-12"},
            headers=self.auth_headers(),
        )

        self.assertEqual(response.status_code, 200)

        tables = response.json()
        first_table = next(item for item in tables if item["table"]["number"] == 1)

        self.assertEqual(
            first_table["bookings"][0]["id"],
            booking["id"],
        )

    def test_admin_can_cancel_booking(self) -> None:
        """Отмена меняет статус и освобождает столик."""
        booking = self.create_test_booking()

        cancelled = self.client.post(
            f"/api/admin/bookings/{booking['id']}/cancel",
            headers=self.auth_headers(),
        )

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(
            cancelled.json()["status"],
            "отменено",
        )

        occupancy = self.client.get(
            "/api/admin/occupancy",
            params={"day": "2030-05-12"},
            headers=self.auth_headers(),
        )

        self.assertEqual(occupancy.status_code, 200)

        first_table = next(
            item for item in occupancy.json() if item["table"]["number"] == 1
        )

        self.assertEqual(first_table["bookings"], [])
