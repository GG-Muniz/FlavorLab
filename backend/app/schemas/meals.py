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

    model_config = {"from_attributes": True}


class MealLogResponse(BaseModel):
    id: int
    log_date: date
    meal_type: str
    entries: List[MealLogEntryResponse]

    model_config = {"from_attributes": True}


class DailyNutritionSummary(BaseModel):
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float


class MealResponse(BaseModel):
    id: int
    user_id: int
    name: str
    meal_type: Optional[str] = None
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    instructions: Optional[List[str]] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    source: str
    date_logged: Optional[date] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class LogMealRequest(BaseModel):
    log_date: date = Field(..., description="Date to log the meal (YYYY-MM-DD)")


class CalendarLinksResponse(BaseModel):
    google: str = Field(..., description="Google Calendar magic link")
    outlook: str = Field(..., description="Outlook Calendar magic link")


class LoggedMealSummary(BaseModel):
    log_id: int
    name: str
    calories: float
    meal_type: str
    logged_at: str
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    fiber: Optional[float] = Field(None, description="Fiber in grams")


class MacroData(BaseModel):
    consumed: float = Field(..., description="Amount consumed in grams")
    goal: float = Field(..., description="Daily goal in grams")


class MacroTotals(BaseModel):
    protein: MacroData = Field(..., description="Protein consumed and goal")
    carbs: MacroData = Field(..., description="Carbohydrates consumed and goal")
    fat: MacroData = Field(..., description="Fat consumed and goal")
    fiber: MacroData = Field(..., description="Fiber consumed and goal")


class DailyCaloriesSummaryResponse(BaseModel):
    daily_goal: Optional[float] = Field(None, description="User's daily calorie goal")
    total_consumed: float = Field(..., description="Total calories consumed today")
    remaining: Optional[float] = Field(None, description="Remaining calories for the day")
    logged_meals_today: List[LoggedMealSummary] = Field(..., description="All meals logged for today")
    macros: MacroTotals = Field(..., description="Daily macronutrient totals")
    current_streak: int = Field(default=0, description="Current meal logging streak in days")
    entry_date: date = Field(..., description="Date for this summary")


class SetCalorieGoalRequest(BaseModel):
    goal_calories: float = Field(..., gt=0, description="Daily calorie goal (must be positive)")


class LogManualCaloriesRequest(BaseModel):
    meal_type: str = Field(..., description="Meal type (e.g., Breakfast, Lunch, Dinner, Snack)")
    calories: float = Field(..., gt=0, description="Calories consumed (must be positive)")
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    fiber: Optional[float] = Field(None, description="Fiber in grams")


