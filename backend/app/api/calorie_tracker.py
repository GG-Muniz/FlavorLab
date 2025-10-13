"""
FastAPI endpoints for calorie tracking.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..services.auth import get_current_active_user
from ..services.calorie_service import (
    set_user_daily_calorie_goal,
    log_user_calorie_intake,
    get_daily_calorie_summary_data
)
from ..schemas.calorie import (
    DailyCalorieGoalSet,
    CalorieIntakeLog,
    DailyCalorieSummaryResponse,
    UserCalorieGoalResponse,
    CalorieIntakeLogResponse,
    CalorieIntakeEntryResponse
)

# Create router
router = APIRouter(prefix="/calorie", tags=["calorie-tracking"])


@router.put("/goal", response_model=UserCalorieGoalResponse)
async def set_daily_calorie_goal(
    goal_data: DailyCalorieGoalSet,
    # TEMPORARY: Auth disabled for development - Remove this comment when auth is ready
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Set or update the user's daily calorie goal.

    Args:
        goal_data: Daily calorie goal data
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserCalorieGoalResponse with updated goal
    """
    try:
        # TEMPORARY: Hardcoded user_id for development
        # TODO: Replace with current_user.id when auth is enabled
        user_id = 1

        calorie_goal = set_user_daily_calorie_goal(
            db=db,
            user_id=user_id,
            goal_calories=goal_data.goal_calories
        )

        return UserCalorieGoalResponse(
            goal_calories=calorie_goal.goal_calories,
            last_updated=calorie_goal.last_updated,
            message="Calorie goal updated successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting calorie goal: {str(e)}"
        )


@router.post("/intake", response_model=CalorieIntakeLogResponse)
async def log_calorie_intake(
    intake_data: CalorieIntakeLog,
    # TEMPORARY: Auth disabled for development - Remove this comment when auth is ready
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Log a calorie intake entry for the current user.

    Args:
        intake_data: Calorie intake data
        current_user: Current authenticated user
        db: Database session

    Returns:
        CalorieIntakeLogResponse with entry and updated summary
    """
    try:
        # TEMPORARY: Hardcoded user_id for development
        # TODO: Replace with current_user.id when auth is enabled
        user_id = 1

        # Log the intake
        intake_entry = log_user_calorie_intake(
            db=db,
            user_id=user_id,
            meal_type=intake_data.meal_type,
            calories_consumed=intake_data.calories_consumed
        )

        # Get updated summary with all calculated fields
        (goal_calories, total_intake, entries, percentage,
         remaining_calories, goal_met_or_exceeded, calories_over_goal) = get_daily_calorie_summary_data(
            db=db,
            user_id=user_id
        )

        summary = DailyCalorieSummaryResponse(
            goal_calories=goal_calories,
            total_intake=total_intake,
            remaining_calories=remaining_calories,
            percentage=percentage,
            goal_exceeded=goal_met_or_exceeded,
            excess_calories=calories_over_goal,
            entries=[CalorieIntakeEntryResponse.model_validate(entry) for entry in entries],
            entry_date=date.today()
        )

        return CalorieIntakeLogResponse(
            entry=CalorieIntakeEntryResponse.model_validate(intake_entry),
            summary=summary,
            message="Calorie intake logged successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging calorie intake: {str(e)}"
        )


@router.get("/summary", response_model=DailyCalorieSummaryResponse)
async def get_calorie_summary(
    target_date: Optional[date] = Query(None, description="Date for summary (defaults to today)"),
    # TEMPORARY: Auth disabled for development - Remove this comment when auth is ready
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get daily calorie summary for the current user.

    Args:
        target_date: Optional date for summary (defaults to today)
        current_user: Current authenticated user
        db: Database session

    Returns:
        DailyCalorieSummaryResponse with calorie summary
    """
    try:
        # TEMPORARY: Hardcoded user_id for development
        # TODO: Replace with current_user.id when auth is enabled
        user_id = 1

        # Get summary with all calculated fields
        (goal_calories, total_intake, entries, percentage,
         remaining_calories, goal_met_or_exceeded, calories_over_goal) = get_daily_calorie_summary_data(
            db=db,
            user_id=user_id,
            target_date=target_date
        )

        return DailyCalorieSummaryResponse(
            goal_calories=goal_calories,
            total_intake=total_intake,
            remaining_calories=remaining_calories,
            percentage=percentage,
            goal_exceeded=goal_met_or_exceeded,
            excess_calories=calories_over_goal,
            entries=[CalorieIntakeEntryResponse.model_validate(entry) for entry in entries],
            entry_date=target_date or date.today()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving calorie summary: {str(e)}"
        )
