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


# ============================================================================
# Meal (Complete Recipe) Schemas
# ============================================================================

class MealResponse(BaseModel):
    """Response schema for a complete meal/recipe."""
    id: int
    user_id: int
    name: str
    meal_type: Optional[str] = None
    calories: int
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


