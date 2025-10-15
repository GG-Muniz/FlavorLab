"""
SQLAlchemy models for FlavorLab users.

This module defines the User model for basic authentication
and user management in the FlavorLab system.
"""

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, Date
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """
    Basic user model for FlavorLab authentication.
    
    This is a simple user model suitable for MVP with email/password
    authentication. Can be extended later for more complex auth needs.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    # Additional personal data
    age = Column(Integer, nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    # Avatar URL (served via FastAPI static files)
    avatar_url = Column(String(512), nullable=True)
    # Extended profile
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(32), nullable=True)
    activity_level = Column(String(32), nullable=True)
    health_goals = Column(JSON)  # list / json
    dietary_preferences = Column(JSON)  # list / json
    
    # Preferences (stored as JSON for flexibility)
    preferences = Column(JSON)  # JSON string
    
    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))
    last_login = Column(DateTime)

    # Relationships (from calorie tracking feature)
    calorie_goal = relationship("DailyCalorieGoal", back_populates="user", uselist=False, cascade="all, delete-orphan")
    calorie_intakes = relationship("CalorieIntakeEntry", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    def get_full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username or self.email.split('@')[0]
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has valid credentials)."""
        return self.is_active and self.is_verified
    
    def update_last_login(self):
        """Updates the last login time to the current time."""
        self.last_login = datetime.datetime.now(datetime.UTC)
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user to dictionary representation.

        Args:
            include_sensitive: Whether to include sensitive information like hashed_password

        Returns:
            Dictionary representation of the user
        """
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "first_name": self.first_name,
            "last_name": self.last_name,
            # Union of profile fields and preferences
            "age": self.age,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "avatar_url": self.avatar_url,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "activity_level": self.activity_level,
            "health_goals": self.health_goals,
            "dietary_preferences": self.dietary_preferences,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

        if include_sensitive:
            data["hashed_password"] = self.hashed_password

        return data
