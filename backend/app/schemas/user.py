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
    preferences: Optional[Dict[str, Any]] = None

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


class HealthGoalsUpdate(BaseModel):
    """Schema for updating user's health goals."""
    selectedGoals: List[int] = Field(
        ...,
        description="Array of selected health goal IDs (1-8)",
        min_length=1,
        max_length=8
    )

    @field_validator('selectedGoals')
    def validate_goal_ids(cls, v):
        """Validate that all goal IDs are between 1 and 8."""
        if not v:
            raise ValueError('At least one health goal must be selected')

        for goal_id in v:
            if goal_id < 1 or goal_id > 8:
                raise ValueError(f'Health goal ID must be between 1 and 8, got {goal_id}')

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError('Duplicate health goal IDs are not allowed')

        return v


class UserSurveyData(BaseModel):
    """
    Schema for complete user survey submission from the onboarding flow.

    This schema captures the full survey data from the frontend for future LLM use
    while also providing the data needed to integrate with the existing meal planner.

    Fields match the frontend formData structure exactly.
    """
    healthPillars: List[str] = Field(
        ...,
        description="List of selected health pillar names (e.g., 'Increased Energy')",
        min_length=1
    )
    dietaryRestrictions: List[str] = Field(
        default_factory=list,
        description="List of dietary restrictions (e.g., 'vegetarian', 'vegan', 'gluten-free')"
    )
    mealComplexity: str = Field(
        ...,
        description="Preferred meal complexity level (e.g., 'simple', 'moderate', 'complex')"
    )
    dislikedIngredients: List[str] = Field(
        default_factory=list,
        description="List of ingredients the user dislikes"
    )
    mealsPerDay: str = Field(
        ...,
        description="Number of meals per day (e.g., '3', '4', '5')"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="List of food allergies"
    )
    primaryGoal: str = Field(
        ...,
        description="Primary health or fitness goal"
    )

    @field_validator('healthPillars')
    def validate_health_pillars(cls, v):
        """Validate that health pillars list is not empty."""
        if not v:
            raise ValueError('At least one health pillar must be selected')
        return v

    @field_validator('mealComplexity')
    def validate_meal_complexity(cls, v):
        """Validate meal complexity value."""
        valid_complexities = ['simple', 'moderate', 'complex']
        if v.lower() not in valid_complexities:
            raise ValueError(f'Meal complexity must be one of: {", ".join(valid_complexities)}')
        return v.lower()

    @field_validator('mealsPerDay')
    def validate_meals_per_day(cls, v):
        """Validate meals per day is a valid number."""
        try:
            meals = int(v)
            if meals < 1 or meals > 10:
                raise ValueError('Meals per day must be between 1 and 10')
        except ValueError:
            raise ValueError('Meals per day must be a valid number')
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
    # SQLAlchemy JSON type handles serialization automatically
    return UserProfileResponse.model_validate(user)


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

