"""Проверки веб-интерфейса и демонстрационного режима."""

from unittest import TestCase

from fastapi.testclient import TestClient

from marusya.api.main import create_app


class TestWebInterface(TestCase):
    """Проверяет сайт и API без PostgreSQL."""

    def setUp(self) -> None:
        """Создаёт отдельное приложение с InMemory-хранилищем."""
        self.app = create_app(demo_mode=True)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_home_page(self) -> None:
        """Главная страница отображается корректно."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("МАРУСЯ", response.text)
        self.assertIn("Найдите свой столик", response.text)

    def test_demo_notice(self) -> None:
        """На странице видно предупреждение о деморежиме."""
        response = self.client.get("/")

        self.assertIn("Демонстрационный режим", response.text)

    def test_stylesheet(self) -> None:
        """CSS доступен через статический маршрут."""
        response = self.client.get("/static/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn(".hero", response.text)

    def test_javascript(self) -> None:
        """JavaScript доступен через статический маршрут."""
        response = self.client.get("/static/app.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/bookings", response.text)

    def test_demo_available_tables(self) -> None:
        """В деморежиме столики доступны без PostgreSQL."""
        response = self.client.get(
            "/api/tables/available",
            params={
                "start": "2030-05-12T19:00:00",
                "guests": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_demo_creates_booking(self) -> None:
        """Созданная бронь влияет на доступность столика."""
        data = {
            "table_number": 1,
            "start": "2030-05-12T19:00:00",
            "guests": 2,
            "customer_name": "Анна",
            "customer_phone": "+79991234567",
        }

        created = self.client.post("/api/bookings", json=data)

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["table_number"], 1)

        available = self.client.get(
            "/api/tables/available",
            params={
                "start": "2030-05-12T19:00:00",
                "guests": 2,
            },
        )

        self.assertEqual(available.status_code, 200)
        numbers = [table["number"] for table in available.json()]
        self.assertNotIn(1, numbers)

    def test_normal_mode_does_not_enable_demo(self) -> None:
        """Обычный режим не подменяет зависимости демонстрационными."""
        app = create_app(demo_mode=False)

        self.assertFalse(app.state.demo_mode)
        self.assertEqual(app.dependency_overrides, {})
