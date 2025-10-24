"""
Meals API endpoints: log meals and get daily nutrition summary.
"""

from __future__ import annotations

from datetime import date, datetime, UTC
from typing import List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.auth import get_current_active_user
from .. import models
from ..models import Entity
from ..models.meal import MealLog, MealLogEntry, Meal, MealSource
from ..schemas.meals import (
    MealLogCreate,
    MealLogResponse,
    MealLogEntryResponse,
    DailyNutritionSummary,
    MealResponse,
    LogMealRequest,
    CalendarLinksResponse,
    DailyCaloriesSummaryResponse,
    LoggedMealSummary,
    LogManualCaloriesRequest,
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


# ============================================================================
# Complete Meal (Recipe) Endpoints
# ============================================================================

@router.get("", response_model=List[MealResponse])
async def get_meals(
    source: Optional[str] = Query(None, description="Filter by source: 'generated' or 'logged'"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> List[MealResponse]:
    """
    Get all meals for the current user, optionally filtered by source.

    - source=generated: Returns meal templates (AI-generated, not yet logged)
    - source=logged: Returns consumed meals (logged to specific dates)
    - source=None: Returns all meals
    """
    query = db.query(Meal).filter(Meal.user_id == current_user.id)

    if source:
        source_upper = source.upper()
        if source_upper == "GENERATED":
            query = query.filter(Meal.source == MealSource.GENERATED)
        elif source_upper == "LOGGED":
            query = query.filter(Meal.source == MealSource.LOGGED)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source filter. Must be 'generated' or 'logged', got: {source}"
            )

    meals = query.order_by(Meal.created_at.desc()).all()

    return [
        MealResponse(
            id=meal.id,
            user_id=meal.user_id,
            name=meal.name,
            meal_type=meal.meal_type,
            calories=meal.calories,
            description=meal.description,
            ingredients=meal.ingredients,
            servings=meal.servings,
            prep_time_minutes=meal.prep_time_minutes,
            cook_time_minutes=meal.cook_time_minutes,
            instructions=meal.instructions,
            nutrition_info=meal.nutrition_info,
            source=meal.source.value,
            date_logged=meal.date_logged,
            created_at=meal.created_at.isoformat() if meal.created_at else "",
            updated_at=meal.updated_at.isoformat() if meal.updated_at else "",
        )
        for meal in meals
    ]


@router.post("/log-from-template/{template_id}", response_model=MealResponse)
async def log_meal_from_template(
    template_id: int = Path(..., description="ID of the meal template to log"),
    payload: LogMealRequest = ...,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> MealResponse:
    """
    Log a meal template as a consumed meal.

    This endpoint:
    1. Fetches the original GENERATED meal template
    2. Creates a NEW meal record copying all data from the template
    3. Sets source=LOGGED and date_logged to the specified date
    4. Leaves the original template unchanged

    For MVP (Option A): Frontend auto-logs to today's date when user clicks "Log Meal"
    """
    # Fetch the template
    template = db.query(Meal).filter(
        Meal.id == template_id,
        Meal.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal template {template_id} not found or does not belong to current user"
        )

    # Verify it's actually a template
    if template.source != MealSource.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meal {template_id} is not a template (source={template.source.value}). Only GENERATED meals can be logged."
        )

    try:
        # Create a new meal record copying all data from template
        logged_meal = Meal(
            user_id=current_user.id,
            name=template.name,
            meal_type=template.meal_type,
            calories=template.calories,
            description=template.description,
            ingredients=template.ingredients,
            servings=template.servings,
            prep_time_minutes=template.prep_time_minutes,
            cook_time_minutes=template.cook_time_minutes,
            instructions=template.instructions,
            nutrition_info=template.nutrition_info,
            source=MealSource.LOGGED,  # CRITICAL: Mark as logged
            date_logged=payload.log_date  # CRITICAL: Set the log date
        )

        db.add(logged_meal)
        db.commit()
        db.refresh(logged_meal)

        return MealResponse(
            id=logged_meal.id,
            user_id=logged_meal.user_id,
            name=logged_meal.name,
            meal_type=logged_meal.meal_type,
            calories=logged_meal.calories,
            description=logged_meal.description,
            ingredients=logged_meal.ingredients,
            servings=logged_meal.servings,
            prep_time_minutes=logged_meal.prep_time_minutes,
            cook_time_minutes=logged_meal.cook_time_minutes,
            instructions=logged_meal.instructions,
            nutrition_info=logged_meal.nutrition_info,
            source=logged_meal.source.value,
            date_logged=logged_meal.date_logged,
            created_at=logged_meal.created_at.isoformat() if logged_meal.created_at else "",
            updated_at=logged_meal.updated_at.isoformat() if logged_meal.updated_at else "",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging meal: {str(e)}"
        )


@router.get("/{meal_id}/calendar-links", response_model=CalendarLinksResponse)
async def get_calendar_links(
    meal_id: int = Path(..., description="ID of the meal to create calendar links for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> CalendarLinksResponse:
    """
    Generate "Magic Links" for adding a meal to personal calendars.

    Returns pre-configured links for:
    - Google Calendar
    - Outlook Calendar

    These links allow users to add meal events without direct API integration.
    """
    # Fetch the meal
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == current_user.id
    ).first()

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal {meal_id} not found or does not belong to current user"
        )

    # Prepare event details
    title = meal.name
    description = meal.description or f"A delicious meal from FlavorLab. Calories: {meal.calories} kcal"

    # Determine event time
    # If meal is logged, use the logged date; otherwise use today
    if meal.date_logged:
        event_date = meal.date_logged
    else:
        event_date = date.today()

    # Set default meal times based on meal type
    meal_times = {
        "breakfast": (8, 0),   # 8:00 AM
        "lunch": (12, 0),      # 12:00 PM
        "dinner": (18, 0),     # 6:00 PM
        "snack": (15, 0),      # 3:00 PM
    }

    hour, minute = meal_times.get(meal.meal_type.lower() if meal.meal_type else "lunch", (12, 0))

    # Create datetime objects for start and end (30 min duration)
    start_datetime = datetime(event_date.year, event_date.month, event_date.day, hour, minute)
    end_datetime = datetime(event_date.year, event_date.month, event_date.day, hour, minute + 30)

    # Format dates for Google Calendar (UTC format without separators)
    google_start = start_datetime.strftime("%Y%m%dT%H%M%S")
    google_end = end_datetime.strftime("%Y%m%dT%H%M%S")
    google_dates = f"{google_start}/{google_end}"

    # Format dates for Outlook (ISO 8601)
    outlook_start = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    outlook_end = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Build Google Calendar link
    google_params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": google_dates,
        "details": description,
    }
    google_link = f"https://calendar.google.com/calendar/render?{urlencode(google_params)}"

    # Build Outlook Calendar link
    outlook_params = {
        "subject": title,
        "startdt": outlook_start,
        "enddt": outlook_end,
        "body": description,
    }
    outlook_link = f"https://outlook.live.com/calendar/0/deeplink/compose?{urlencode(outlook_params)}"

    return CalendarLinksResponse(
        google=google_link,
        outlook=outlook_link
    )


@router.post("/{meal_id}/log", response_model=DailyCaloriesSummaryResponse)
async def log_meal_for_today(
    meal_id: int = Path(..., description="ID of the meal to log"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Create a NEW logged meal entry from an existing meal template.

    This endpoint:
    1. Finds the specified meal template and verifies ownership
    2. Verifies it is a GENERATED template (not already logged)
    3. CREATES A NEW meal record with source=LOGGED and date_logged=today
    4. Preserves the original template for future use
    5. Calculates total calories consumed today
    6. Fetches user's daily calorie goal
    7. Returns complete dashboard summary

    CRITICAL: This creates a new database record. The template remains unchanged
    and can be logged multiple times, with each log getting its own timestamp.
    """
    from ..models.calorie_tracking import DailyCalorieGoal

    # Get today's date
    today = date.today()

    # Find the meal TEMPLATE to use as source
    template = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal template with ID {meal_id} not found"
        )

    # Verify this is a template (source=GENERATED), not an already-logged meal
    if template.source != MealSource.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meal {meal_id} is not a template (source={template.source.value}). Only GENERATED meals can be logged."
        )

    # CRITICAL FIX: Create a NEW meal record for the log entry
    # This preserves the original template and allows multiple logs
    logged_meal = Meal(
        user_id=current_user.id,
        name=template.name,
        meal_type=template.meal_type,
        calories=template.calories,
        description=template.description,
        ingredients=template.ingredients,
        servings=template.servings,
        prep_time_minutes=template.prep_time_minutes,
        cook_time_minutes=template.cook_time_minutes,
        instructions=template.instructions,
        nutrition_info=template.nutrition_info,
        source=MealSource.LOGGED,  # Mark as logged entry
        date_logged=today,  # Set log date
        # created_at and updated_at will be auto-set to NOW by database
    )

    db.add(logged_meal)
    db.commit()
    db.refresh(logged_meal)

    # Calculate total consumed today
    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)

    # Get user's daily calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == current_user.id
    ).first()

    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000  # Default 2000
    remaining = daily_goal - total_consumed

    # Build logged meals summary
    logged_meals = [
        LoggedMealSummary(
            log_id=m.id,
            name=m.name,
            calories=int(m.calories or 0),
            meal_type=m.meal_type or "Unknown",
            logged_at=m.updated_at.isoformat() if m.updated_at else datetime.now(UTC).isoformat()
        )
        for m in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=daily_goal,
        total_consumed=int(total_consumed),
        remaining=remaining,
        logged_meals_today=logged_meals
    )


@router.delete("/{meal_id}", response_model=DailyCaloriesSummaryResponse)
async def delete_logged_meal(
    meal_id: int = Path(..., description="ID of the logged meal to delete"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Delete a logged meal and return updated dashboard summary.

    This endpoint:
    1. Finds the specified logged meal and verifies ownership
    2. Deletes the meal from the database
    3. Recalculates total calories consumed today
    4. Returns updated dashboard summary
    """
    from ..models.calorie_tracking import DailyCalorieGoal

    # Get today's date
    today = date.today()

    # Find the meal
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == current_user.id,
        Meal.source == MealSource.LOGGED,
        Meal.date_logged == today
    ).first()

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Logged meal with ID {meal_id} not found or not logged today"
        )

    # Delete the meal
    db.delete(meal)
    db.commit()

    # Calculate total consumed today after deletion
    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)

    # Get user's daily calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == current_user.id
    ).first()

    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000  # Default 2000
    remaining = daily_goal - total_consumed

    # Build logged meals summary
    logged_meals = [
        LoggedMealSummary(
            log_id=m.id,
            name=m.name,
            calories=int(m.calories or 0),
            meal_type=m.meal_type or "Unknown",
            logged_at=m.updated_at.isoformat() if m.updated_at else datetime.now(UTC).isoformat()
        )
        for m in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=daily_goal,
        total_consumed=int(total_consumed),
        remaining=remaining,
        logged_meals_today=logged_meals
    )


@router.put("/{meal_id}", response_model=DailyCaloriesSummaryResponse)
async def update_logged_meal(
    meal_id: int = Path(..., description="ID of the logged meal to update"),
    request: LogManualCaloriesRequest = ...,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Update a logged meal's calories and meal type, return updated dashboard summary.

    This endpoint:
    1. Finds the specified logged meal and verifies ownership
    2. Updates the meal's calories and meal_type
    3. Recalculates total calories consumed today
    4. Returns updated dashboard summary
    """
    from ..models.calorie_tracking import DailyCalorieGoal

    # Get today's date
    today = date.today()

    # Find the meal
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == current_user.id,
        Meal.source == MealSource.LOGGED,
        Meal.date_logged == today
    ).first()

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Logged meal with ID {meal_id} not found or not logged today"
        )

    # Update the meal
    meal.calories = request.calories
    meal.meal_type = request.meal_type
    meal.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(meal)

    # Calculate total consumed today after update
    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)

    # Get user's daily calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == current_user.id
    ).first()

    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000  # Default 2000
    remaining = daily_goal - total_consumed

    # Build logged meals summary
    logged_meals = [
        LoggedMealSummary(
            log_id=m.id,
            name=m.name,
            calories=int(m.calories or 0),
            meal_type=m.meal_type or "Unknown",
            logged_at=m.updated_at.isoformat() if m.updated_at else datetime.now(UTC).isoformat()
        )
        for m in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=daily_goal,
        total_consumed=int(total_consumed),
        remaining=remaining,
        logged_meals_today=logged_meals
    )


@router.post("/log-manual", response_model=DailyCaloriesSummaryResponse)
async def log_manual_calories(
    request: LogManualCaloriesRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Manually log calories for a meal and return updated dashboard summary.

    This endpoint:
    1. Creates a new meal record with source=LOGGED and date_logged=today
    2. Calculates total calories consumed today
    3. Fetches user's daily calorie goal
    4. Returns complete dashboard summary
    """
    from ..models.calorie_tracking import DailyCalorieGoal

    # Get today's date
    today = date.today()

    # Create manual meal entry
    manual_meal = Meal(
        user_id=current_user.id,
        name=f"Manual Entry - {request.meal_type}",
        meal_type=request.meal_type,
        calories=request.calories,
        source=MealSource.LOGGED,
        date_logged=today,
        description=f"Manually logged {request.calories} calories for {request.meal_type}",
        ingredients=[],
        instructions=[],
        nutrition_info={"calories": request.calories}
    )

    db.add(manual_meal)
    db.commit()
    db.refresh(manual_meal)

    # Calculate total consumed today
    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)

    # Get user's daily calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == current_user.id
    ).first()

    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000  # Default 2000
    remaining = daily_goal - total_consumed

    # Build logged meals summary
    logged_meals = [
        LoggedMealSummary(
            log_id=m.id,
            name=m.name,
            calories=int(m.calories or 0),
            meal_type=m.meal_type or "Unknown",
            logged_at=m.updated_at.isoformat() if m.updated_at else datetime.now(UTC).isoformat()
        )
        for m in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=daily_goal,
        total_consumed=int(total_consumed),
        remaining=remaining,
        logged_meals_today=logged_meals
    )


