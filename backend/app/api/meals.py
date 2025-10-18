"""
Meals API endpoints: log meals and get daily nutrition summary.
"""

from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.auth import get_current_active_user
from .. import models
from ..models import Entity
from ..models.meal import MealLog, MealLogEntry
from ..schemas.meals import (
    MealLogCreate,
    MealLogResponse,
    MealLogEntryResponse,
    DailyNutritionSummary,
)


router = APIRouter(prefix="/meals", tags=["Meals"])


@router.post("/log", response_model=MealLogResponse)
async def log_meal(
    payload: MealLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> MealLogResponse:
    """Create a meal log with entries for the current user."""
    try:
        # Create parent log
        meal_log = MealLog(
            user_id=current_user.id,
            log_date=payload.log_date,
            meal_type=payload.meal_type,
        )
        db.add(meal_log)
        db.flush()  # assign id

        # Create entries
        for e in payload.entries:
            entry = MealLogEntry(
                meal_log_id=meal_log.id,
                ingredient_id=e.ingredient_id,
                quantity_grams=float(e.quantity_grams),
            )
            db.add(entry)

        db.commit()
        db.refresh(meal_log)

        # Build response
        entries_resp: List[MealLogEntryResponse] = [
            MealLogEntryResponse.model_validate(entry) for entry in meal_log.entries
        ]
        return MealLogResponse(
            id=meal_log.id,
            log_date=meal_log.log_date,
            meal_type=meal_log.meal_type,
            entries=entries_resp,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging meal: {str(e)}",
        )


@router.get("/summary/{log_date}", response_model=DailyNutritionSummary)
async def get_daily_summary(
    log_date: date = Path(..., description="Summary date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyNutritionSummary:
    """
    Aggregate daily nutrition by summing entries joined with ingredient nutrition per 100g.
    Calculation for each entry: (quantity_grams / 100) * per100g_value
    """
    # Fetch all entries for the user/date
    logs: List[MealLog] = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id, MealLog.log_date == log_date)
        .all()
    )

    if not logs:
        return DailyNutritionSummary(
            total_calories=0.0, total_protein_g=0.0, total_carbs_g=0.0, total_fat_g=0.0
        )

    # Collect all entries
    entry_ids: List[int] = [log.id for log in logs]
    entries: List[MealLogEntry] = (
        db.query(MealLogEntry).filter(MealLogEntry.meal_log_id.in_(entry_ids)).all()
    )

    if not entries:
        return DailyNutritionSummary(
            total_calories=0.0, total_protein_g=0.0, total_carbs_g=0.0, total_fat_g=0.0
        )

    # Load ingredients mapping for faster joins
    ingredient_ids = list({e.ingredient_id for e in entries})
    if not ingredient_ids:
        return DailyNutritionSummary(
            total_calories=0.0, total_protein_g=0.0, total_carbs_g=0.0, total_fat_g=0.0
        )

    ingredients = (
        db.query(Entity).filter(Entity.id.in_(ingredient_ids)).all()
    )
    by_id = {str(ing.id): ing for ing in ingredients}

    total_calories = 0.0
    total_protein_g = 0.0
    total_carbs_g = 0.0
    total_fat_g = 0.0

    def _value(attrs, key):
        v = (attrs or {}).get(key)
        if isinstance(v, dict):
            return float(v.get("value", 0.0) or 0.0)
        return float(v or 0.0)

    for entry in entries:
        ing = by_id.get(str(entry.ingredient_id))
        if not ing:
            # Skip unknown ingredients
            continue
        attrs = ing.attributes or {}
        factor = (float(entry.quantity_grams) or 0.0) / 100.0
        total_calories += factor * _value(attrs, "calories")
        total_protein_g += factor * _value(attrs, "protein_g")
        total_carbs_g += factor * _value(attrs, "carbs_g")
        total_fat_g += factor * _value(attrs, "fat_g")

    return DailyNutritionSummary(
        total_calories=round(total_calories, 2),
        total_protein_g=round(total_protein_g, 2),
        total_carbs_g=round(total_carbs_g, 2),
        total_fat_g=round(total_fat_g, 2),
    )


