"""
SQLAlchemy model for daily journal notes.
"""

from __future__ import annotations

from datetime import date, datetime, UTC
from sqlalchemy import Column, Integer, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class DailyNote(Base):
    """
    Daily journal notes for user reflections.
    Maps to existing daily_notes table in database.
    """
    __tablename__ = "daily_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    note_date = Column(Date, nullable=False, index=True)
    note_text = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationship to User model (optional, can be added if User model has reciprocal relationship)
    # user = relationship("User", back_populates="daily_notes")
