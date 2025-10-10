"""
Pydantic schemas for meal plan-related API endpoints.

This module defines the request/response schemas for meal plan generation
and management, including meals, daily plans, and weekly meal plans.
"""

from typing import List
from pydantic import BaseModel, Field


class MealItem(BaseModel):
    """Schema for a single meal item."""
    type: str = Field(..., description="Type of meal (breakfast, lunch, dinner, snack)")
    name: str = Field(..., description="Name of the meal")
    calories: int = Field(..., description="Estimated calories for this meal")
    description: str = Field(..., description="Description of the meal and its ingredients")


class DailyMealPlan(BaseModel):
    """Schema for a single day's meal plan."""
    day: str = Field(..., description="Day of the week or date")
    meals: List[MealItem] = Field(..., description="List of meals for this day")


class MealPlanResponse(BaseModel):
    """
    Schema for the complete meal plan response.

    This represents a weekly or multi-day meal plan with all meals organized by day.
    """
    plan: List[DailyMealPlan] = Field(..., description="List of daily meal plans")
    total_days: int = Field(..., description="Total number of days in the plan")
    average_calories_per_day: int = Field(..., description="Average daily calorie intake")


class MealPlanRequest(BaseModel):
    """Schema for meal plan generation request."""
    num_days: int = Field(
        default=7,
        ge=1,
        le=14,
        description="Number of days for the meal plan (1-14)"
    )
    preferences: dict = Field(
        default_factory=dict,
        description="Optional preferences for meal generation"
    )
