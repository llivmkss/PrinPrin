from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.database.base import Base

table_features = Table(
    "table_features",
    Base.metadata,
    Column(
        "table_number",
        ForeignKey("tables.number", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "feature_id",
        ForeignKey("features.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class DiningTable(Base):
    """Столик ресторана."""

    __tablename__ = "tables"

    number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    capacity: Mapped[int] = mapped_column()
    zone: Mapped[str] = mapped_column(String(50))
    is_available: Mapped[bool] = mapped_column(default=True)

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="table",
        passive_deletes=True,
    )
    features: Mapped[list["Feature"]] = relationship(
        secondary=table_features,
        back_populates="tables",
    )

    __table_args__ = (
        CheckConstraint("number > 0", name="number_positive"),
        CheckConstraint("capacity > 0", name="capacity_positive"),
    )


class Feature(Base):
    """Особенность столика: у окна, розетка, детское кресло."""

    __tablename__ = "features"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    tables: Mapped[list["DiningTable"]] = relationship(
        secondary=table_features,
        back_populates="features",
    )


class Booking(Base):
    """Бронирование столика."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    table_number: Mapped[int] = mapped_column(
        ForeignKey("tables.number", ondelete="RESTRICT"),
        index=True,
    )
    guests: Mapped[int] = mapped_column()
    start: Mapped[datetime] = mapped_column(DateTime)
    customer_name: Mapped[str] = mapped_column(String(50))
    customer_phone: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")

    table: Mapped["DiningTable"] = relationship(back_populates="bookings")

    __table_args__ = (
        CheckConstraint("guests > 0", name="guests_positive"),
        CheckConstraint("status IN ('active', 'cancelled')", name="status_valid"),
    )


class Admin(Base):
    """Администратор: логин и хеш пароля."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))