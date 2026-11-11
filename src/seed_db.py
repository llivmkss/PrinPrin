"""Заполнение базы начальными данными: столики, особенности, администратор."""

from sqlalchemy import select

from src.database import models as db
from src.database.session import SessionFactory
from src.security import PasswordHasher
from src.seed import ADMIN_LOGIN
from src.seed import ADMIN_PASSWORD
from src.seed import TABLES

# Особенности столиков: название -> номера столиков (можно менять).
FEATURES: dict[str, list[int]] = {
    "Розетка у столика": [1, 2, 3],
    "Детский стул": [3, 4, 6, 7],
    "Тихое место": [1, 5],
}


def seed() -> None:
    """Добавляет столики, особенности и администратора, если база пуста."""
    with SessionFactory() as session:
        if session.scalar(select(db.DiningTable).limit(1)) is not None:
            print("База уже заполнена, ничего не добавлено.")
            return

        tables = {
            table.number: db.DiningTable(
                number=table.number,
                capacity=table.capacity,
                zone=table.zone,
                is_available=table.is_available,
            )
            for table in TABLES
        }
        session.add_all(tables.values())

        for name, numbers in FEATURES.items():
            session.add(
                db.Feature(name=name, tables=[tables[number] for number in numbers])
            )

        session.add(
            db.Admin(
                login=ADMIN_LOGIN,
                password_hash=PasswordHasher().make_hash(ADMIN_PASSWORD),
            )
        )
        session.commit()
        print("Начальные данные добавлены.")


if __name__ == "__main__":
    seed()
