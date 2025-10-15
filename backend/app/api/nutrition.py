"""
Nutrition API endpoints for FlavorLab.

This module provides REST API endpoints for user nutrition tracking,
including calorie goals, macronutrient targets, and water intake.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from .. import models
from ..schemas.nutrition import (
    NutritionData,
    CalorieGoalData,
    MacroData,
    WaterData,
)
from ..services.auth import get_current_active_user
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Nutrition"])


@router.get("/{user_id}/nutrition", response_model=NutritionData)
async def get_user_nutrition(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> NutritionData:
    """
    Get nutrition tracking data for a specific user.

    This endpoint returns the user's nutrition goals and current progress,
    including calories, macronutrients (protein, carbs, fat), and water intake.

    Args:
        user_id: ID of the user to fetch nutrition data for
        current_user: Currently authenticated user
        db: Database session

    Returns:
        NutritionData: Complete nutrition tracking data

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Authorization: User can only access their own nutrition data
    # (In a future version, admin users could access any user's data)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's nutrition data"
        )

    # Fetch the user from database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Extract targets from user preferences
    preferences = user.preferences or {}
    calorie_goal = preferences.get("calorie_goal", 0.0)
    macro_targets = preferences.get("macro_targets", {})

    # Get individual macro targets with defaults
    protein_target = float(macro_targets.get("protein", 0.0))
    carbs_target = float(macro_targets.get("carbs", 0.0))
    fat_target = float(macro_targets.get("fat", 0.0))
    water_target = float(macro_targets.get("water", 0.0))

    # For MVP, current values are 0 (actual tracking will be implemented later)
    # In production, you would fetch these from a daily_nutrition_log table or similar
    current_calories = 0.0
    current_protein = 0.0
    current_carbs = 0.0
    current_fat = 0.0
    current_water = 0.0

    # Calculate percentage for calories
    calorie_percentage = 0.0
    if calorie_goal > 0:
        calorie_percentage = min((current_calories / calorie_goal) * 100, 100.0)

    # Construct the nutrition data response
    nutrition_data = NutritionData(
        calories=CalorieGoalData(
            current=current_calories,
            target=float(calorie_goal),
            percentage=calorie_percentage
        ),
        protein=MacroData(
            current=current_protein,
            target=protein_target,
            unit="g"
        ),
        carbs=MacroData(
            current=current_carbs,
            target=carbs_target,
            unit="g"
        ),
        fat=MacroData(
            current=current_fat,
            target=fat_target,
            unit="g"
        ),
        water=WaterData(
            current=current_water,
            target=water_target,
            unit="ml"
        )
    )

    return nutrition_data
