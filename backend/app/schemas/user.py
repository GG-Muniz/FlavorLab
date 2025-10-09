"""
Pydantic schemas for FlavorLab users.

This module defines the request/response schemas for user-related API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserBase(BaseModel):
    """Base schema for user operations."""
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)
    is_active: Optional[bool] = True
    
    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    preferences: Optional[Dict[str, Any]] = Field(None, description="User's preferences")


class UserResponse(UserBase):
    """Schema for user responses (public data)."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier for the user")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    

class UserProfileResponse(UserResponse):
    """Schema for detailed user profile responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Unique identifier for the user")
    preferences: Optional[Dict[str, Any]] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """Pydantic model for a change password request."""
    current_password: str = Field(..., description="User's current password")
    new_password: str = Field(..., min_length=8, description="User's new password")

    @field_validator('new_password')
    def password_complexity(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserPreferences(BaseModel):
    """Schema for user preferences."""
    dietary_restrictions: Optional[list] = None
    health_goals: Optional[list] = None
    flavor_preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, bool]] = None
    privacy_settings: Optional[Dict[str, bool]] = None


class UserStatsResponse(BaseModel):
    """Schema for user statistics."""
    total_users: int
    active_users: int
    verified_users: int
    recent_registrations: int
    last_updated: Optional[datetime] = None


# Utility functions for schema conversion
def user_to_response(user, include_sensitive: bool = False) -> UserResponse:
    """Convert SQLAlchemy user to Pydantic response."""
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )


def user_to_profile_response(user) -> UserProfileResponse:
    """Convert SQLAlchemy user to detailed profile response."""
    preferences = None
    if user.preferences:
        try:
            import json
            preferences = json.loads(user.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences = {}
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        preferences=preferences
    )


def create_user_from_schema(user_data: UserCreate, hashed_password: str):
    """Create SQLAlchemy user from Pydantic schema."""
    from ..models import User
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password
    )
    return user

