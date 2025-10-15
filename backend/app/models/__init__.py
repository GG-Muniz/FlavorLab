"""
FlavorLab models package.

This package contains all SQLAlchemy models for the FlavorLab application.
"""

from .entity import Entity, IngredientEntity, NutrientEntity, CompoundEntity
from .relationship import RelationshipEntity
from .user import User
from .calorie_tracking import DailyCalorieGoal, CalorieIntakeEntry

__all__ = [
    "Entity",
    "IngredientEntity",
    "NutrientEntity",
    "CompoundEntity",
    "RelationshipEntity",
    "User",
    "DailyCalorieGoal",
    "CalorieIntakeEntry"
]
