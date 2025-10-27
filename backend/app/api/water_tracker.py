"""
FastAPI endpoints for water (hydration) tracking.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.water_service import (
    set_user_daily_water_goal,
    log_user_water_intake,
    get_daily_water_summary_data,
)
from ..schemas.water import (
    DailyWaterGoalSet,
    WaterIntakeLog,
    DailyWaterSummaryResponse,
    UserWaterGoalResponse,
    WaterIntakeEntryResponse,
)

router = APIRouter(prefix="/water", tags=["water-tracking"])


@router.put("/goal", response_model=UserWaterGoalResponse)
async def set_daily_water_goal(
    goal_data: DailyWaterGoalSet,
    db: Session = Depends(get_db)
):
    try:
        user_id = 1  # TODO: replace with current_user.id when auth wired
        goal = set_user_daily_water_goal(db=db, user_id=user_id, goal_ml=goal_data.goal_ml)
        return UserWaterGoalResponse(goal_ml=goal.goal_ml, last_updated=goal.last_updated, message="Water goal updated successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error setting water goal: {str(e)}")


@router.post("/intake", response_model=WaterIntakeEntryResponse)
async def log_water_intake(
    intake: WaterIntakeLog,
    db: Session = Depends(get_db)
):
    try:
        user_id = 1
        entry = log_user_water_intake(db=db, user_id=user_id, volume_ml=intake.volume_ml)
        return WaterIntakeEntryResponse.model_validate(entry)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error logging water intake: {str(e)}")


@router.get("/summary", response_model=DailyWaterSummaryResponse)
async def get_water_summary(
    target_date: Optional[date] = Query(None, description="Date for summary (defaults to today)"),
    db: Session = Depends(get_db)
):
    try:
        user_id = 1
        goal_ml, total_ml, entries, pct, remaining, exceeded, over_ml = get_daily_water_summary_data(
            db=db, user_id=user_id, target_date=target_date
        )
        return DailyWaterSummaryResponse(
            goal_ml=goal_ml,
            total_intake_ml=total_ml,
            percentage=pct,
            remaining_ml=remaining,
            goal_exceeded=exceeded,
            excess_ml=over_ml,
            entries=[WaterIntakeEntryResponse.model_validate(e) for e in entries],
            entry_date=target_date or date.today(),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving water summary: {str(e)}")


