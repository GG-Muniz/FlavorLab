"""
SQLAlchemy models for meal logging.
"""

from __future__ import annotations

from datetime import date, datetime, UTC
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.orm import relationship

from ..database import Base


class MealSource(PyEnum):
    """Source of meal data."""
    GENERATED = "GENERATED"  # AI-generated meal templates
    LOGGED = "LOGGED"  # User-logged consumed meals


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
    """
    Complete meal/recipe model (used for AI-generated meal plans and calendar integration).
    Separate from MealLog which tracks consumed ingredients.
    """
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic meal info
    name = Column(String(255), nullable=False)
    meal_type = Column(String(50), nullable=False, index=True)  # breakfast, lunch, dinner, snack
    source = Column(Enum(MealSource), nullable=False, default=MealSource.GENERATED)
    date_logged = Column(Date, nullable=True, index=True)  # Date when meal was logged/consumed

    # Nutrition
    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)

    # Recipe details
    description = Column(Text, nullable=True)
    servings = Column(Integer, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)

    # Structured data (JSON)
    ingredients = Column(JSON, nullable=True)  # List of ingredient objects
    instructions = Column(JSON, nullable=True)  # List of instruction steps
    nutrition_info = Column(JSON, nullable=True)  # Full nutrition breakdown

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

