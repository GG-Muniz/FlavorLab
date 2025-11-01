"""
Meals API endpoints: log meals, manage meal templates, and compute daily nutrition summaries.
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
from ..services.streak_service import calculate_current_streak
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


def extract_macro_nutrients(nutrition_info):
    if not nutrition_info:
        return {"protein_g": None, "carbs_g": None, "fat_g": None, "fiber_g": None}

    def parse_nutrient(value):
        if not value:
            return None
        try:
            return float(str(value).replace("g", "").strip())
        except (ValueError, TypeError):
            return None

    return {
        "protein_g": parse_nutrient(nutrition_info.get("protein")),
        "carbs_g": parse_nutrient(nutrition_info.get("carbs")),
        "fat_g": parse_nutrient(nutrition_info.get("fat")),
        "fiber_g": parse_nutrient(nutrition_info.get("fiber")),
    }


def create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal):
    protein_goal = calorie_goal.goal_protein_g if calorie_goal and calorie_goal.goal_protein_g else 150.0
    carbs_goal = calorie_goal.goal_carbs_g if calorie_goal and calorie_goal.goal_carbs_g else 200.0
    fat_goal = calorie_goal.goal_fat_g if calorie_goal and calorie_goal.goal_fat_g else 67.0
    fiber_goal = calorie_goal.goal_fiber_g if calorie_goal and calorie_goal.goal_fiber_g else 25.0

    return {
        "protein": {"consumed": round(total_protein, 1), "goal": round(protein_goal, 1)},
        "carbs": {"consumed": round(total_carbs, 1), "goal": round(carbs_goal, 1)},
        "fat": {"consumed": round(total_fat, 1), "goal": round(fat_goal, 1)},
        "fiber": {"consumed": round(total_fiber, 1), "goal": round(fiber_goal, 1)},
    }


router = APIRouter(prefix="/meals", tags=["Meals"])


@router.post("/log", response_model=DailyCaloriesSummaryResponse)
async def log_meal(
    payload: MealLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    from ..models.calorie_tracking import DailyCalorieGoal

    try:
        user_id = current_user.id

        meal_log = MealLog(
            user_id=user_id,
            log_date=payload.log_date,
            meal_type=payload.meal_type,
        )
        db.add(meal_log)
        db.flush()

        for entry_payload in payload.entries:
            entry = MealLogEntry(
                meal_log_id=meal_log.id,
                ingredient_id=entry_payload.ingredient_id,
                quantity_grams=float(entry_payload.quantity_grams),
            )
            db.add(entry)

        ingredient_ids = [entry.ingredient_id for entry in payload.entries]
        ingredients = db.query(Entity).filter(Entity.id.in_(ingredient_ids)).all()
        by_id = {str(ing.id): ing for ing in ingredients}

        def _value(attrs, key):
            value = (attrs or {}).get(key)
            if isinstance(value, dict):
                return float(value.get("value", 0.0) or 0.0)
            return float(value or 0.0)

        total_calories = total_protein = total_carbs = total_fat = total_fiber = 0.0
        for entry in payload.entries:
            ingredient = by_id.get(str(entry.ingredient_id))
            if not ingredient:
                continue
            attrs = ingredient.attributes or {}
            factor = (float(entry.quantity_grams) or 0.0) / 100.0
            total_calories += factor * _value(attrs, "calories")
            total_protein += factor * _value(attrs, "protein_g")
            total_carbs += factor * _value(attrs, "carbs_g")
            total_fat += factor * _value(attrs, "fat_g")
            total_fiber += factor * _value(attrs, "fiber_g")

        logged_meal = Meal(
            user_id=user_id,
            name=f"Manual Entry - {payload.meal_type}",
            meal_type=payload.meal_type,
            calories=round(total_calories, 1),
            protein_g=round(total_protein, 1),
            carbs_g=round(total_carbs, 1),
            fat_g=round(total_fat, 1),
            fiber_g=round(total_fiber, 1),
            source=MealSource.LOGGED,
            date_logged=payload.log_date,
        )
        db.add(logged_meal)

        db.commit()
        db.refresh(meal_log)
        db.refresh(logged_meal)

        todays_meals = db.query(Meal).filter(
            Meal.user_id == user_id,
            Meal.date_logged == payload.log_date,
            Meal.source == MealSource.LOGGED,
        ).all()

        total_consumed = sum(m.calories or 0 for m in todays_meals)
        total_protein = sum(m.protein_g or 0 for m in todays_meals)
        total_carbs = sum(m.carbs_g or 0 for m in todays_meals)
        total_fat = sum(m.fat_g or 0 for m in todays_meals)
        total_fiber = sum(m.fiber_g or 0 for m in todays_meals)

        calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == user_id).first()
        daily_goal = calorie_goal.goal_calories if calorie_goal else 2000.0
        remaining = float(daily_goal) - float(total_consumed)

        logged_meals = [
            LoggedMealSummary(
                log_id=meal.id,
                name=meal.name,
                calories=float(meal.calories or 0),
                meal_type=meal.meal_type or "Unknown",
                logged_at=meal.updated_at.isoformat() if meal.updated_at else datetime.now(UTC).isoformat(),
                protein=meal.protein_g,
                carbs=meal.carbs_g,
                fat=meal.fat_g,
                fiber=meal.fiber_g,
            )
            for meal in todays_meals
        ]

        macros = create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal)
        current_streak = calculate_current_streak(db, user_id)

        return DailyCaloriesSummaryResponse(
            daily_goal=float(daily_goal),
            total_consumed=float(total_consumed),
            remaining=max(0.0, round(remaining, 1)),
            logged_meals_today=logged_meals,
            macros=macros,
            current_streak=current_streak,
            entry_date=payload.log_date,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/summary/{log_date}", response_model=DailyNutritionSummary)
async def get_daily_summary(
    log_date: date = Path(..., description="Summary date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyNutritionSummary:
    meals = (
        db.query(Meal)
        .filter(Meal.user_id == current_user.id, Meal.date_logged == log_date)
        .all()
    )

    if not meals:
        return DailyNutritionSummary(
            total_calories=0.0,
            total_protein_g=0.0,
            total_carbs_g=0.0,
            total_fat_g=0.0,
            total_fiber_g=0.0,
        )

    total_calories = sum(float(meal.calories or 0) for meal in meals)
    total_protein = sum(float(meal.protein_g or 0) for meal in meals)
    total_carbs = sum(float(meal.carbs_g or 0) for meal in meals)
    total_fat = sum(float(meal.fat_g or 0) for meal in meals)
    total_fiber = sum(float(meal.fiber_g or 0) for meal in meals)

    return DailyNutritionSummary(
        total_calories=round(total_calories, 2),
        total_protein_g=round(total_protein, 2),
        total_carbs_g=round(total_carbs, 2),
        total_fat_g=round(total_fat, 2),
        total_fiber_g=round(total_fiber, 2),
    )


@router.get("", response_model=List[MealResponse])
async def get_meals(
    source: Optional[str] = Query(None, description="Filter by source: 'generated' or 'logged'"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> List[MealResponse]:
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
                detail="Invalid source filter. Must be 'generated' or 'logged'",
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
    template = (
        db.query(Meal)
        .filter(Meal.id == template_id, Meal.user_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal template {template_id} not found or does not belong to current user",
        )

    if template.source != MealSource.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meal {template_id} is not a template (source={template.source.value}).",
        )

    try:
        macro_nutrients = extract_macro_nutrients(template.nutrition_info)

        logged_meal = Meal(
            user_id=current_user.id,
            name=template.name,
            meal_type=template.meal_type,
            calories=template.calories,
            protein_g=macro_nutrients["protein_g"],
            carbs_g=macro_nutrients["carbs_g"],
            fat_g=macro_nutrients["fat_g"],
            fiber_g=macro_nutrients["fiber_g"],
            description=template.description,
            ingredients=template.ingredients,
            servings=template.servings,
            prep_time_minutes=template.prep_time_minutes,
            cook_time_minutes=template.cook_time_minutes,
            instructions=template.instructions,
            nutrition_info=template.nutrition_info,
            source=MealSource.LOGGED,
            date_logged=payload.log_date,
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
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error logging meal: {exc}")


@router.get("/{meal_id}/calendar-links", response_model=CalendarLinksResponse)
async def get_calendar_links(
    meal_id: int = Path(..., description="ID of the meal to create calendar links for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> CalendarLinksResponse:
    meal = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meal {meal_id} not found or does not belong to current user")

    title = meal.name
    description = meal.description or f"A delicious meal from FlavorLab. Calories: {meal.calories} kcal"
    event_date = meal.date_logged or date.today()

    meal_times = {
        "breakfast": (8, 0),
        "lunch": (12, 0),
        "dinner": (18, 0),
        "snack": (15, 0),
    }
    hour, minute = meal_times.get((meal.meal_type or "lunch").lower(), (12, 0))

    start_datetime = datetime(event_date.year, event_date.month, event_date.day, hour, minute)
    end_datetime = datetime(event_date.year, event_date.month, event_date.day, hour, minute + 30)

    google_start = start_datetime.strftime("%Y%m%dT%H%M%S")
    google_end = end_datetime.strftime("%Y%m%dT%H%M%S")
    google_link = "https://calendar.google.com/calendar/render?" + urlencode(
        {
            "action": "TEMPLATE",
            "text": title,
            "dates": f"{google_start}/{google_end}",
            "details": description,
        }
    )

    outlook_link = "https://outlook.live.com/calendar/0/deeplink/compose?" + urlencode(
        {
            "subject": title,
            "startdt": start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "enddt": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "body": description,
        }
    )

    return CalendarLinksResponse(google=google_link, outlook=outlook_link)


@router.post("/{meal_id}/log", response_model=DailyCaloriesSummaryResponse)
async def log_meal_for_today(
    meal_id: int = Path(..., description="ID of the meal to log"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    from ..models.calorie_tracking import DailyCalorieGoal

    today = date.today()

    template = (
        db.query(Meal)
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meal {meal_id} not found")

    if template.source != MealSource.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meal {meal_id} is not a template (source={template.source.value}).",
        )

    macro_nutrients = extract_macro_nutrients(template.nutrition_info)

    logged_meal = Meal(
        user_id=current_user.id,
        name=template.name,
        meal_type=template.meal_type,
        calories=template.calories,
        protein_g=macro_nutrients["protein_g"],
        carbs_g=macro_nutrients["carbs_g"],
        fat_g=macro_nutrients["fat_g"],
        fiber_g=macro_nutrients["fiber_g"],
        description=template.description,
        ingredients=template.ingredients,
        servings=template.servings,
        prep_time_minutes=template.prep_time_minutes,
        cook_time_minutes=template.cook_time_minutes,
        instructions=template.instructions,
        nutrition_info=template.nutrition_info,
        source=MealSource.LOGGED,
        date_logged=today,
    )

    db.add(logged_meal)
    db.commit()
    db.refresh(logged_meal)

    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today,
        Meal.source == MealSource.LOGGED,
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)
    total_protein = sum(m.protein_g or 0 for m in todays_meals)
    total_carbs = sum(m.carbs_g or 0 for m in todays_meals)
    total_fat = sum(m.fat_g or 0 for m in todays_meals)
    total_fiber = sum(m.fiber_g or 0 for m in todays_meals)

    calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == current_user.id).first()
    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000.0
    remaining = float(daily_goal) - float(total_consumed)

    logged_meals = [
        LoggedMealSummary(
            log_id=meal_entry.id,
            name=meal_entry.name,
            calories=float(meal_entry.calories or 0),
            meal_type=meal_entry.meal_type or "Unknown",
            logged_at=meal_entry.updated_at.isoformat() if meal_entry.updated_at else datetime.now(UTC).isoformat(),
            protein=meal_entry.protein_g,
            carbs=meal_entry.carbs_g,
            fat=meal_entry.fat_g,
            fiber=meal_entry.fiber_g,
        )
        for meal_entry in todays_meals
    ]

    macros = create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal)

    return DailyCaloriesSummaryResponse(
        daily_goal=float(daily_goal),
        total_consumed=float(total_consumed),
        remaining=max(0.0, round(remaining, 1)),
        logged_meals_today=logged_meals,
        macros=macros,
        current_streak=calculate_current_streak(db, current_user.id),
        entry_date=today,
    )


@router.delete("/{meal_id}", response_model=DailyCaloriesSummaryResponse)
async def delete_logged_meal(
    meal_id: int = Path(..., description="ID of the logged meal to delete"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    from ..models.calorie_tracking import DailyCalorieGoal

    today = date.today()

    meal = (
        db.query(Meal)
        .filter(
            Meal.id == meal_id,
            Meal.user_id == current_user.id,
            Meal.source == MealSource.LOGGED,
        )
        .first()
    )

    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Logged meal {meal_id} not found")

    db.delete(meal)
    db.commit()

    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today,
        Meal.source == MealSource.LOGGED,
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)
    total_protein = sum(m.protein_g or 0 for m in todays_meals)
    total_carbs = sum(m.carbs_g or 0 for m in todays_meals)
    total_fat = sum(m.fat_g or 0 for m in todays_meals)
    total_fiber = sum(m.fiber_g or 0 for m in todays_meals)

    calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == current_user.id).first()
    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000.0
    remaining = float(daily_goal) - float(total_consumed)

    logged_meals = [
        LoggedMealSummary(
            log_id=meal_entry.id,
            name=meal_entry.name,
            calories=float(meal_entry.calories or 0),
            meal_type=meal_entry.meal_type or "Unknown",
            logged_at=meal_entry.updated_at.isoformat() if meal_entry.updated_at else datetime.now(UTC).isoformat(),
            protein=meal_entry.protein_g,
            carbs=meal_entry.carbs_g,
            fat=meal_entry.fat_g,
            fiber=meal_entry.fiber_g,
        )
        for meal_entry in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=float(daily_goal),
        total_consumed=float(total_consumed),
        remaining=max(0.0, round(remaining, 1)),
        logged_meals_today=logged_meals,
        macros=create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal),
        current_streak=calculate_current_streak(db, current_user.id),
        entry_date=today,
    )


@router.put("/{meal_id}", response_model=DailyCaloriesSummaryResponse)
async def update_logged_meal(
    meal_id: int = Path(..., description="ID of the logged meal to update"),
    request: LogManualCaloriesRequest = ...,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    from ..models.calorie_tracking import DailyCalorieGoal

    today = date.today()

    meal = (
        db.query(Meal)
        .filter(
            Meal.id == meal_id,
            Meal.user_id == current_user.id,
            Meal.source == MealSource.LOGGED,
        )
        .first()
    )

    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Logged meal {meal_id} not found")

    meal.calories = request.calories
    meal.meal_type = request.meal_type
    meal.updated_at = datetime.now(UTC)

    if request.protein is not None:
        meal.protein_g = request.protein
    if request.carbs is not None:
        meal.carbs_g = request.carbs
    if request.fat is not None:
        meal.fat_g = request.fat
    if request.fiber is not None:
        meal.fiber_g = request.fiber

    db.commit()
    db.refresh(meal)

    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today,
        Meal.source == MealSource.LOGGED,
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)
    total_protein = sum(m.protein_g or 0 for m in todays_meals)
    total_carbs = sum(m.carbs_g or 0 for m in todays_meals)
    total_fat = sum(m.fat_g or 0 for m in todays_meals)
    total_fiber = sum(m.fiber_g or 0 for m in todays_meals)

    calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == current_user.id).first()
    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000.0
    remaining = float(daily_goal) - float(total_consumed)

    logged_meals = [
        LoggedMealSummary(
            log_id=meal_entry.id,
            name=meal_entry.name,
            calories=float(meal_entry.calories or 0),
            meal_type=meal_entry.meal_type or "Unknown",
            logged_at=meal_entry.updated_at.isoformat() if meal_entry.updated_at else datetime.now(UTC).isoformat(),
            protein=meal_entry.protein_g,
            carbs=meal_entry.carbs_g,
            fat=meal_entry.fat_g,
            fiber=meal_entry.fiber_g,
        )
        for meal_entry in todays_meals
    ]

    macros = create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal)

    return DailyCaloriesSummaryResponse(
        daily_goal=float(daily_goal),
        total_consumed=float(total_consumed),
        remaining=max(0.0, round(remaining, 1)),
        logged_meals_today=logged_meals,
        macros=macros,
        current_streak=calculate_current_streak(db, current_user.id),
        entry_date=today,
    )


@router.post("/log-manual", response_model=DailyCaloriesSummaryResponse)
async def log_manual_calories(
    request: LogManualCaloriesRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    from ..models.calorie_tracking import DailyCalorieGoal

    today = date.today()

    manual_meal = Meal(
        user_id=current_user.id,
        name=f"Manual Entry - {request.meal_type}",
        meal_type=request.meal_type,
        calories=request.calories,
        protein_g=request.protein if request.protein is not None else 0.0,
        carbs_g=request.carbs if request.carbs is not None else 0.0,
        fat_g=request.fat if request.fat is not None else 0.0,
        fiber_g=request.fiber if request.fiber is not None else 0.0,
        source=MealSource.LOGGED,
        date_logged=today,
        description=f"Manually logged {request.calories} calories for {request.meal_type}",
        ingredients=[],
        instructions=[],
        nutrition_info={"calories": request.calories},
    )

    db.add(manual_meal)
    db.commit()
    db.refresh(manual_meal)

    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today,
        Meal.source == MealSource.LOGGED,
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)
    total_protein = sum(m.protein_g or 0 for m in todays_meals)
    total_carbs = sum(m.carbs_g or 0 for m in todays_meals)
    total_fat = sum(m.fat_g or 0 for m in todays_meals)
    total_fiber = sum(m.fiber_g or 0 for m in todays_meals)

    calorie_goal = db.query(DailyCalorieGoal).filter(DailyCalorieGoal.user_id == current_user.id).first()
    daily_goal = calorie_goal.goal_calories if calorie_goal else 2000.0
    remaining = float(daily_goal) - float(total_consumed)

    logged_meals = [
        LoggedMealSummary(
            log_id=meal_entry.id,
            name=meal_entry.name,
            calories=float(meal_entry.calories or 0),
            meal_type=meal_entry.meal_type or "Unknown",
            logged_at=meal_entry.updated_at.isoformat() if meal_entry.updated_at else datetime.now(UTC).isoformat(),
            protein=meal_entry.protein_g,
            carbs=meal_entry.carbs_g,
            fat=meal_entry.fat_g,
            fiber=meal_entry.fiber_g,
        )
        for meal_entry in todays_meals
    ]

    macros = create_macro_response(total_protein, total_carbs, total_fat, total_fiber, calorie_goal)

    return DailyCaloriesSummaryResponse(
        daily_goal=float(daily_goal),
        total_consumed=float(total_consumed),
        remaining=max(0.0, round(remaining, 1)),
        logged_meals_today=logged_meals,
        macros=macros,
        current_streak=calculate_current_streak(db, current_user.id),
        entry_date=today,
    )
