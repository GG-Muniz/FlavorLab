"""
Pydantic schemas for calorie tracking API.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DailyCalorieGoalSet(BaseModel):
    """Schema for setting daily calorie goal."""
    goal_calories: float = Field(..., gt=0, le=10000, description="Daily calorie goal (must be positive and reasonable)")


class CalorieIntakeLog(BaseModel):
    """Schema for logging calorie intake."""
    meal_type: str = Field(..., description="Type of meal (Breakfast, Lunch, Dinner, Snack)")
    calories_consumed: float = Field(..., gt=0, le=5000, description="Calories consumed in this meal")

    @field_validator('meal_type')
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        """Validate meal type is one of the allowed values."""
        allowed_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        if v not in allowed_types:
            raise ValueError(f'meal_type must be one of {allowed_types}')
        return v


class CalorieIntakeEntryResponse(BaseModel):
    """Schema for calorie intake entry response."""
    id: int
    meal_type: str
    calories_consumed: float
    entry_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class DailyCalorieSummaryResponse(BaseModel):
    """Schema for daily calorie summary response."""
    goal_calories: Optional[float] = Field(None, description="User's daily calorie goal")
    total_intake: float = Field(..., description="Total calories consumed today")
    remaining_calories: Optional[float] = Field(None, description="Remaining calories (goal - intake), set to 0 when goal is met/exceeded")
    percentage: float = Field(..., description="Percentage of goal consumed (capped at 100)")
    goal_exceeded: bool = Field(False, description="True if user has met or exceeded their daily goal")
    excess_calories: Optional[float] = Field(None, description="Calories over goal if exceeded, otherwise None")
    entries: List[CalorieIntakeEntryResponse] = Field(default_factory=list, description="List of today's intake entries")
    entry_date: date = Field(..., description="Date for this summary")


class UserCalorieGoalResponse(BaseModel):
    """Schema for user calorie goal response."""
    goal_calories: float
    last_updated: datetime
    message: str = "Calorie goal updated successfully"


class CalorieIntakeLogResponse(BaseModel):
    """Schema for calorie intake log response with updated summary."""
    entry: CalorieIntakeEntryResponse
    summary: DailyCalorieSummaryResponse
    message: str = "Calorie intake logged successfully"
