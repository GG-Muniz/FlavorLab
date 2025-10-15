"""
Pydantic schemas for nutrition-related API endpoints.

This module defines the request/response schemas for user nutrition tracking,
including calorie goals, macronutrient targets, and water intake.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CalorieGoalData(BaseModel):
    """Schema for calorie goal data."""
    current: float = Field(default=0.0, description="Current calories consumed")
    target: float = Field(default=0.0, description="Target calorie goal")
    percentage: float = Field(default=0.0, description="Percentage of goal achieved (0-100)")


class MacroData(BaseModel):
    """Schema for macronutrient data (protein, carbs, fat)."""
    current: float = Field(default=0.0, description="Current amount consumed")
    target: float = Field(default=0.0, description="Target amount")
    unit: str = Field(default="g", description="Unit of measurement (grams)")


class WaterData(BaseModel):
    """Schema for water intake data."""
    current: float = Field(default=0.0, description="Current water intake")
    target: float = Field(default=0.0, description="Target water intake")
    unit: str = Field(default="ml", description="Unit of measurement (milliliters)")


class NutritionData(BaseModel):
    """
    Complete nutrition data schema.

    This schema represents the full nutrition tracking data for a user,
    including calories, macronutrients, and water intake.
    """
    calories: CalorieGoalData = Field(default_factory=CalorieGoalData, description="Calorie tracking data")
    protein: MacroData = Field(default_factory=MacroData, description="Protein tracking data")
    carbs: MacroData = Field(default_factory=MacroData, description="Carbohydrate tracking data")
    fat: MacroData = Field(default_factory=MacroData, description="Fat tracking data")
    water: WaterData = Field(default_factory=WaterData, description="Water intake tracking data")


class NutritionPreferences(BaseModel):
    """
    Schema for storing nutrition preferences in user.preferences.

    This schema defines the structure expected in the user's preferences JSON field.
    """
    calorie_goal: Optional[float] = Field(None, description="Daily calorie goal")
    macro_targets: Optional[dict] = Field(
        None,
        description="Macronutrient targets",
        examples=[{
            "protein": 150,
            "carbs": 200,
            "fat": 65,
            "water": 2000
        }]
    )
