"""
Pydantic schemas for meal logging and daily nutrition summary.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MealLogEntryCreate(BaseModel):
    ingredient_id: str = Field(..., description="Entity ID of ingredient")
    quantity_grams: float = Field(..., ge=0, description="Quantity in grams")


class MealLogCreate(BaseModel):
    log_date: date = Field(..., description="Log date (YYYY-MM-DD)")
    meal_type: str = Field(..., description="Meal type (e.g., Breakfast, Lunch)")
    entries: List[MealLogEntryCreate] = Field(..., min_items=1)


class MealLogEntryResponse(BaseModel):
    id: int
    ingredient_id: str
    quantity_grams: float

    model_config = {
        "from_attributes": True
    }


class MealLogResponse(BaseModel):
    id: int
    log_date: date
    meal_type: str
    entries: List[MealLogEntryResponse]

    model_config = {
        "from_attributes": True
    }


class DailyNutritionSummary(BaseModel):
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float


# ============================================================================
# Meal (Complete Recipe) Schemas
# ============================================================================

class MealResponse(BaseModel):
    """Response schema for a complete meal/recipe."""
    id: int
    user_id: int
    name: str
    meal_type: Optional[str] = None
    calories: float
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    instructions: Optional[List[str]] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    source: str  # "GENERATED" or "LOGGED"
    date_logged: Optional[date] = None
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True
    }


class LogMealRequest(BaseModel):
    """Request schema for logging a meal template."""
    log_date: date = Field(..., description="Date to log the meal (YYYY-MM-DD)")


class CalendarLinksResponse(BaseModel):
    """Response schema for calendar integration links."""
    google: str = Field(..., description="Google Calendar magic link")
    outlook: str = Field(..., description="Outlook Calendar magic link")


class LoggedMealSummary(BaseModel):
    """Summary of a single logged meal for dashboard display."""
    log_id: int
    name: str
    calories: float
    meal_type: str
    logged_at: str  # ISO datetime string
    # Optional macro fields for proportional scaling
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    fiber: Optional[float] = Field(None, description="Fiber in grams")


class MacroData(BaseModel):
    """Individual macro data with consumed and goal values."""
    consumed: float = Field(..., description="Amount consumed in grams")
    goal: float = Field(..., description="Daily goal in grams")

class MacroTotals(BaseModel):
    """Macronutrient totals for the day with consumed and goal values."""
    protein: MacroData = Field(..., description="Protein consumed and goal")
    carbs: MacroData = Field(..., description="Carbohydrates consumed and goal")
    fat: MacroData = Field(..., description="Fat consumed and goal")
    fiber: MacroData = Field(..., description="Fiber consumed and goal")


class DailyCaloriesSummaryResponse(BaseModel):
    """Complete dashboard summary response after logging a meal."""
    daily_goal: int = Field(..., description="User's daily calorie goal")
    total_consumed: int = Field(..., description="Total calories consumed today")
    remaining: int = Field(..., description="Remaining calories for the day")
    logged_meals_today: List[LoggedMealSummary] = Field(..., description="All meals logged for today")
    macros: MacroTotals = Field(..., description="Daily macronutrient totals")


class SetCalorieGoalRequest(BaseModel):
    """Request schema for setting user's daily calorie goal."""
    goal_calories: float = Field(..., gt=0, description="Daily calorie goal (must be positive)")


class LogManualCaloriesRequest(BaseModel):
    """Request schema for manually logging calories."""
    meal_type: str = Field(..., description="Meal type (e.g., Breakfast, Lunch, Dinner, Snack)")
    calories: float = Field(..., gt=0, description="Calories consumed (must be positive)")
    # Optional macro fields for proportional scaling
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    fiber: Optional[float] = Field(None, description="Fiber in grams")


