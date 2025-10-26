"""
Service functions for calorie tracking.
"""
from datetime import date, datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.calorie_tracking import DailyCalorieGoal, CalorieIntakeEntry


def set_user_daily_calorie_goal(db: Session, user_id: int, goal_calories: int) -> DailyCalorieGoal:
    """
    Create or update the user's daily calorie goal.

    Args:
        db: Database session
        user_id: ID of the user
        goal_calories: Daily calorie goal to set

    Returns:
        DailyCalorieGoal: The created or updated calorie goal
    """
    # Check if user already has a goal
    existing_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == user_id
    ).first()

    if existing_goal:
        # Update existing goal
        existing_goal.goal_calories = goal_calories
        existing_goal.last_updated = datetime.now(UTC.utc)
        db.commit()
        db.refresh(existing_goal)
        return existing_goal
    else:
        # Create new goal
        new_goal = DailyCalorieGoal(
            user_id=user_id,
            goal_calories=goal_calories
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return new_goal


def log_user_calorie_intake(
    db: Session,
    user_id: int,
    meal_type: str,
    calories_consumed: int,
    entry_date: Optional[date] = None
) -> CalorieIntakeEntry:
    """
    Log a calorie intake entry for the user.

    Args:
        db: Database session
        user_id: ID of the user
        meal_type: Type of meal (Breakfast, Lunch, Dinner, Snack)
        calories_consumed: Calories consumed in this meal
        entry_date: Date of the entry (defaults to today)

    Returns:
        CalorieIntakeEntry: The created intake entry
    """
    if entry_date is None:
        entry_date = date.today()

    new_entry = CalorieIntakeEntry(
        user_id=user_id,
        meal_type=meal_type,
        calories_consumed=calories_consumed,
        entry_date=entry_date
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


def get_daily_calorie_summary_data(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None
) -> Tuple[Optional[int], int, List[CalorieIntakeEntry], float, int, bool, Optional[int]]:
    """
    Get daily calorie summary data for a user.

    Args:
        db: Database session
        user_id: ID of the user
        target_date: Date to get summary for (defaults to today)

    Returns:
        Tuple of (goal_calories, total_intake, entries, percentage, remaining_calories, goal_met_or_exceeded, calories_over_goal)
    """
    if target_date is None:
        target_date = date.today()

    # Get user's calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == user_id
    ).first()

    goal_calories = calorie_goal.goal_calories if calorie_goal else None

    # Get all intake entries for the target date
    intake_entries = db.query(CalorieIntakeEntry).filter(
        CalorieIntakeEntry.user_id == user_id,
        CalorieIntakeEntry.entry_date == target_date
    ).order_by(CalorieIntakeEntry.created_at.desc()).all()

    # Calculate total intake
    total_intake = sum(entry.calories_consumed for entry in intake_entries)

    # Calculate percentage (capped at 100%)
    if goal_calories and goal_calories > 0:
        raw_percentage = (total_intake / goal_calories) * 100
        # Cap the percentage at 100% to prevent the progress wheel from exceeding full circle
        percentage = round(min(raw_percentage, 100.0), 2)

        # Calculate remaining calories, goal status, and overage
        actual_remaining = goal_calories - total_intake
        goal_met_or_exceeded = total_intake >= goal_calories

        # Cap remaining_calories at 0 when goal is met/exceeded
        remaining_calories = max(0, actual_remaining)

        # Calculate calories over goal if exceeded
        calories_over_goal = total_intake - goal_calories if goal_met_or_exceeded else None
    else:
        percentage = 0.0
        remaining_calories = 0
        goal_met_or_exceeded = False
        calories_over_goal = None

    return goal_calories, total_intake, intake_entries, percentage, remaining_calories, goal_met_or_exceeded, calories_over_goal


def get_user_calorie_goal(db: Session, user_id: int) -> Optional[DailyCalorieGoal]:
    """
    Get the user's current daily calorie goal.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        DailyCalorieGoal or None if not set
    """
    return db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == user_id
    ).first()
