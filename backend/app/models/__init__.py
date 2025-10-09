"""
FlavorLab models package.

This package contains all SQLAlchemy models for the FlavorLab application.
"""

from .entity import Entity, IngredientEntity, NutrientEntity, CompoundEntity
from .relationship import RelationshipEntity
from .user import User

__all__ = [
    "Entity",
    "IngredientEntity", 
    "NutrientEntity",
    "CompoundEntity",
    "RelationshipEntity",
    "User"
]
