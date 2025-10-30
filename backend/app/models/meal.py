"""
SQLAlchemy models for meal logging and meal templates.
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.orm import relationship

from ..database import Base


class MealSource(PyEnum):
    GENERATED = "GENERATED"
    LOGGED = "LOGGED"


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


class Meal(Base):
    """Complete meal/recipe model used for meal templates and calendar integration."""

    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    meal_type = Column(String(50), nullable=False, index=True)
    source = Column(Enum(MealSource), nullable=False, default=MealSource.GENERATED)
    date_logged = Column(Date, nullable=True, index=True)
    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    servings = Column(Integer, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    ingredients = Column(JSON, nullable=True)
    instructions = Column(JSON, nullable=True)
    nutrition_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

