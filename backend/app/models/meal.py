"""
SQLAlchemy models for meal logging.
"""

from __future__ import annotations

from datetime import date, datetime, UTC
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(50), nullable=False, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    entries = relationship("MealLogEntry", back_populates="meal_log", cascade="all, delete-orphan")


class MealLogEntry(Base):
    __tablename__ = "meal_log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_log_id = Column(Integer, ForeignKey("meal_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(String(255), ForeignKey("entities.id", ondelete="SET NULL"), nullable=False, index=True)
    quantity_grams = Column(Float, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    meal_log = relationship("MealLog", back_populates="entries")

