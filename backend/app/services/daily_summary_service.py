"""
Daily Summary Service - Provides daily nutrition summary for dashboard.

This service works with the Meal model to provide dashboard statistics.
"""

from datetime import date, datetime, UTC
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..models.meal import Meal
from ..models.calorie_tracking import DailyCalorieGoal


def create_daily_summary(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Create daily nutrition summary for the dashboard.

    Args:
        user_id: ID of the user
        db: Database session

    Returns:
        Dictionary with daily_goal, total_consumed, remaining, logged_meals_today
    """
    # Get today's date
    today = date.today()

    # Get user's daily calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == user_id
    ).first()

    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000  # Default 2000

    # Query ALL meals logged today for this user
    todays_meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date_logged == today
    ).all()

    # Calculate total consumed
    total_consumed = sum(meal.calories or 0 for meal in todays_meals)

    # Calculate macro totals
    total_protein = sum(meal.protein_g or 0 for meal in todays_meals)
    total_carbs = sum(meal.carbs_g or 0 for meal in todays_meals)
    total_fat = sum(meal.fat_g or 0 for meal in todays_meals)
    total_fiber = sum(meal.fiber_g or 0 for meal in todays_meals)

    # Calculate remaining
    remaining = daily_goal - total_consumed

    # Calculate percentage and goal exceeded status
    percentage = min(100.0, (total_consumed / daily_goal * 100) if daily_goal > 0 else 0.0)
    goal_exceeded = total_consumed >= daily_goal
    excess_calories = max(0, total_consumed - daily_goal) if goal_exceeded else None

    # Build logged meals list
    logged_meals: List[Dict[str, Any]] = []

    for meal in todays_meals:
        # Get meal name - handle manual entries
        meal_name = meal.name
        if meal.source == 'LOGGED' and meal_name.startswith('Manual Entry'):
            # Use meal_type as the display name for manual entries
            meal_name = meal.meal_type or 'Unknown'

        # Get timestamp
        if meal.created_at:
            timestamp = meal.created_at.replace(tzinfo=UTC) if meal.created_at.tzinfo is None else meal.created_at
        else:
            timestamp = datetime.now(UTC)

        logged_meals.append({
            "log_id": meal.id,
            "name": meal_name,
            "calories": float(meal.calories or 0),
            "meal_type": meal.meal_type or "Unknown",
            "logged_at": timestamp.isoformat(),
            # Add macro fields for proportional scaling
            "protein": meal.protein_g or 0,
            "carbs": meal.carbs_g or 0,
            "fat": meal.fat_g or 0,
            "fiber": meal.fiber_g or 0
        })

    # Get macro goals from calorie goal record
    protein_goal = calorie_goal.goal_protein_g if calorie_goal and calorie_goal.goal_protein_g else 150.0
    carbs_goal = calorie_goal.goal_carbs_g if calorie_goal and calorie_goal.goal_carbs_g else 200.0
    fat_goal = calorie_goal.goal_fat_g if calorie_goal and calorie_goal.goal_fat_g else 67.0
    fiber_goal = calorie_goal.goal_fiber_g if calorie_goal and calorie_goal.goal_fiber_g else 25.0

    # Return complete state with new macro structure
    return {
        "daily_goal": int(daily_goal),
        "total_consumed": int(total_consumed),
        "remaining": int(remaining),
        "logged_meals_today": logged_meals,
        "macros": {
            "protein": {
                "consumed": round(total_protein, 1),
                "goal": round(protein_goal, 1)
            },
            "carbs": {
                "consumed": round(total_carbs, 1),
                "goal": round(carbs_goal, 1)
            },
            "fat": {
                "consumed": round(total_fat, 1),
                "goal": round(fat_goal, 1)
            },
            "fiber": {
                "consumed": round(total_fiber, 1),
                "goal": round(fiber_goal, 1)
            }
        }
    }
