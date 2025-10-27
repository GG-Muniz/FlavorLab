"""
SQLAlchemy models for water (hydration) tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class DailyWaterGoal(Base):
    """User's daily water (ml) goal."""

    __tablename__ = "daily_water_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    goal_ml = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class WaterIntakeEntry(Base):
    """Water intake entry (ml) per user and day."""

    __tablename__ = "water_intake_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    volume_ml = Column(Integer, nullable=False)
    entry_date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")


