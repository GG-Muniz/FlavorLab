"""
Pydantic schemas for calorie tracking API.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DailyCalorieGoalSet(BaseModel):
    goal_calories: float = Field(
        ..., gt=0, le=10000, description="Daily calorie goal (must be positive and reasonable)"
    )


class CalorieIntakeLog(BaseModel):
    meal_type: str = Field(..., description="Type of meal (Breakfast, Lunch, Dinner, Snack)")
    calories_consumed: float = Field(..., gt=0, le=5000, description="Calories consumed in this meal")

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, value: str) -> str:
        allowed_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        if value not in allowed_types:
            raise ValueError(f"meal_type must be one of {allowed_types}")
        return value


class CalorieIntakeEntryResponse(BaseModel):
    id: int
    meal_type: str
    calories_consumed: float
    entry_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class LoggedMealEntry(BaseModel):
    log_id: int
    name: str
    calories: float
    meal_type: str
    logged_at: str
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0


class DailyCalorieSummaryResponse(BaseModel):
    goal_calories: Optional[float] = Field(None, description="User's daily calorie goal")
    total_intake: float = Field(..., description="Total calories consumed today")
    remaining_calories: Optional[float] = Field(
        None, description="Remaining calories (goal - intake), set to 0 when goal is met/exceeded"
    )
    percentage: float = Field(..., description="Percentage of goal consumed (capped at 100)")
    goal_exceeded: bool = Field(False, description="True if user has met or exceeded their daily goal")
    excess_calories: Optional[float] = Field(
        None, description="Calories over goal if exceeded, otherwise None"
    )
    entries: List[CalorieIntakeEntryResponse] = Field(
        default_factory=list,
        description="Legacy list of intake entries (retained for backwards compatibility)",
    )
    logged_meals_today: List[LoggedMealEntry] = Field(
        default_factory=list,
        description="List of today's intake entries enriched with macros",
    )
    entry_date: date = Field(..., description="Date for this summary")


class UserCalorieGoalResponse(BaseModel):
    goal_calories: float
    last_updated: datetime
    message: str = "Calorie goal updated successfully"


class CalorieIntakeLogResponse(BaseModel):
    entry: CalorieIntakeEntryResponse
    summary: DailyCalorieSummaryResponse
    message: str = "Calorie intake logged successfully"
