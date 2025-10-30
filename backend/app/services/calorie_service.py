"""
Service functions for calorie tracking.
"""
from datetime import date, datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from ..models.calorie_tracking import DailyCalorieGoal, CalorieIntakeEntry


def set_user_daily_calorie_goal(db: Session, user_id: int, goal_calories: float) -> DailyCalorieGoal:
    """
    Create or update the user's daily calorie goal and compute macro targets.
    """
    protein_goal = round((goal_calories * 0.30) / 4, 1)
    carbs_goal = round((goal_calories * 0.40) / 4, 1)
    fat_goal = round((goal_calories * 0.30) / 9, 1)
    fiber_goal = 25.0

    existing_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == user_id).first()
    if existing_goal:
        existing_goal.goal_calories = goal_calories
        existing_goal.goal_protein_g = protein_goal
        existing_goal.goal_carbs_g = carbs_goal
        existing_goal.goal_fat_g = fat_goal
        existing_goal.goal_fiber_g = fiber_goal
        existing_goal.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(existing_goal)
        return existing_goal

    new_goal = DailyCalorieGoal(
        user_id=user_id,
        goal_calories=goal_calories,
        goal_protein_g=protein_goal,
        goal_carbs_g=carbs_goal,
        goal_fat_g=fat_goal,
        goal_fiber_g=fiber_goal,
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


def log_user_calorie_intake(
    db: Session,
    user_id: int,
    meal_type: str,
    calories_consumed: float,
    entry_date: Optional[date] = None,
) -> CalorieIntakeEntry:
    if entry_date is None:
        entry_date = date.today()

    new_entry = CalorieIntakeEntry(
        user_id=user_id,
        meal_type=meal_type,
        calories_consumed=calories_consumed,
        entry_date=entry_date,
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


def get_daily_calorie_summary_data(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None,
) -> Tuple[Optional[float], float, List[CalorieIntakeEntry], float, float, bool, Optional[float]]:
    if target_date is None:
        target_date = date.today()

    calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == user_id).first()
    goal_calories = calorie_goal.goal_calories if calorie_goal else None

    intake_entries = (
        db.query(CalorieIntakeEntry)
        .filter(
            CalorieIntakeEntry.user_id == user_id,
            CalorieIntakeEntry.entry_date == target_date,
        )
        .order_by(CalorieIntakeEntry.created_at.desc())
        .all()
    )

    total_intake = sum(entry.calories_consumed for entry in intake_entries)

    if goal_calories and goal_calories > 0:
        raw_percentage = (total_intake / goal_calories) * 100
        percentage = round(min(raw_percentage, 100.0), 2)

        actual_remaining = goal_calories - total_intake
        goal_met_or_exceeded = total_intake >= goal_calories
        remaining_calories = max(0, actual_remaining)
        calories_over_goal = total_intake - goal_calories if goal_met_or_exceeded else None
    else:
        percentage = 0.0
        remaining_calories = 0
        goal_met_or_exceeded = False
        calories_over_goal = None

    return (
        goal_calories,
        total_intake,
        intake_entries,
        percentage,
        remaining_calories,
        goal_met_or_exceeded,
        calories_over_goal,
    )


def get_user_calorie_goal(db: Session, user_id: int) -> Optional[DailyCalorieGoal]:
    return db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == user_id).first()
