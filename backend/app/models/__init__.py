"""
FlavorLab models package.

This package contains all SQLAlchemy models for the FlavorLab application.
"""

from .entity import Entity, IngredientEntity, NutrientEntity, CompoundEntity
from .relationship import RelationshipEntity
from .category import Category, IngredientCategory
from .user import User
from .calorie_tracking import DailyCalorieGoal, CalorieIntakeEntry
from .water_tracking import DailyWaterGoal, WaterIntakeEntry
from .meal import MealLog, MealLogEntry, Meal
from .daily_note import DailyNote

__all__ = [
    "Entity",
    "IngredientEntity",
    "NutrientEntity",
    "CompoundEntity",
    "RelationshipEntity",
    "User",
    "DailyCalorieGoal",
    "CalorieIntakeEntry",
    "DailyWaterGoal",
    "WaterIntakeEntry",
    "MealLog",
    "MealLogEntry",
    "Meal",
    "DailyNote",
    "Category",
    "IngredientCategory",
]
