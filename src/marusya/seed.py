"""Начальные данные: ресторан, столики и учётная запись администратора."""

from datetime import time

from marusya.models import Restaurant
from marusya.models import Table

RESTAURANT: Restaurant = Restaurant(
    name="Маруся",
    address="г. Волгоград, ул. Аллея героев, 1",
    opens_at=time(9, 0),
    closes_at=time(23, 0),
    phone="+7 (8442) 59-59-24",
)

TABLES: list[Table] = [
    Table(number=1, capacity=2, zone="Основной зал"),
    Table(number=2, capacity=2, zone="У окна"),
    Table(number=3, capacity=4, zone="Основной зал"),
    Table(number=4, capacity=4, zone="У окна"),
    Table(number=5, capacity=4, zone="Терраса"),
    Table(number=6, capacity=6, zone="Основной зал"),
    Table(number=7, capacity=6, zone="Терраса"),
    Table(number=8, capacity=10, zone="Банкетный зал"),
]

ADMIN_LOGIN: str = "admin"
ADMIN_PASSWORD: str = "admin123"
