"""
SQLAlchemy models for calorie tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base


class DailyCalorieGoal(Base):
    """Model for storing user's daily calorie goals."""

    __tablename__ = "daily_calorie_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    goal_calories = Column(Integer, nullable=False)
    # Macro goals (in grams)
    goal_protein_g = Column(Float, nullable=True)
    goal_carbs_g = Column(Float, nullable=True)
    goal_fat_g = Column(Float, nullable=True)
    goal_fiber_g = Column(Float, nullable=True, default=25.0)  # Fixed 25g fiber goal
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="calorie_goal")


class CalorieIntakeEntry(Base):
    """Model for storing user's daily calorie intake entries."""

    __tablename__ = "calorie_intake_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(String(50), nullable=False)  # Breakfast, Lunch, Dinner, Snack
    calories_consumed = Column(Integer, nullable=False)
    entry_date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="calorie_intakes")
