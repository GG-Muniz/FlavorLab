"""
Pydantic schemas for meal logging and daily nutrition summary.
"""

from __future__ import annotations

from datetime import date
from typing import List
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


