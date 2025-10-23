"""
User API endpoints for FlavorLab.

This module provides REST API endpoints for user operations including
registration, authentication, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
import datetime
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import UploadFile, File
import os
import shutil
from uuid import uuid4
import logging
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from .. import models
from ..models.entity import IngredientEntity
from ..models.health_pillars import HEALTH_PILLARS, get_pillar_name
from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    ChangePasswordRequest,
    HealthGoalsUpdate,
    UserSurveyData,
    Token,
    TokenData,
    UserStatsResponse,
    UserLogin,
    PasswordReset,
    PasswordResetConfirm,
)
from ..schemas.meals import (
    DailyCaloriesSummaryResponse,
    SetCalorieGoalRequest,
)
from ..schemas.meal_plan import (
    MealPlanResponse,
    MealPlanRequest,
    MealItem,
    DailyMealPlan,
    LLMMealPlanResponse,
)
from ..services.auth import AuthService, get_current_active_user, get_current_verified_user
from ..database import get_db
from ..config import get_settings

router = APIRouter(prefix="/users", tags=["Users"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Normalize emails for robust comparison
        input_email = (user_data.email or "").strip().lower()
        demo_email = (getattr(settings, 'demo_email', 'demo@flavorlab.com') or "").strip().lower()
        logger.info("/users/register: input_email=%s demo_email=%s", input_email, demo_email)

        # Special case: demo email acts as overwrite (for testing convenience)
        demo_local, _, demo_domain = demo_email.partition('@')
        demo_pattern = rf"^{re.escape(demo_local)}(\+[^@]+)?@{re.escape(demo_domain)}$"
        alt_demo_pattern = rf"^{re.escape(demo_local)}(\+[^@]+)?@flavorlab\.local$"
        is_demo = bool(re.fullmatch(demo_pattern, input_email) or re.fullmatch(alt_demo_pattern, input_email))
        if is_demo:
            # Delete any existing demo user to guarantee a fresh registration
            deleted = AuthService.delete_user_by_email(db, input_email)
            if deleted:
                logger.info("/users/register: demo path - deleted existing demo user for fresh signup")
            # Create demo user (always active/verified)
            user = AuthService.create_user(
                db=db,
                email=input_email,
                password=user_data.password,
                username=user_data.username or 'demo',
                first_name=user_data.first_name or 'Demo',
                last_name=user_data.last_name or 'User',
                is_active=True,
                is_verified=True
            )
            return UserResponse.model_validate(user)
        else:
            # Check if user already exists (case-insensitive)
            existing_user = db.query(models.User).filter(func.lower(models.User.email) == input_email).first()
            if existing_user:
                logger.info("/users/register: non-demo existing user found, rejecting: %s", input_email)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check if username is taken (if provided)
        if user_data.username:
            existing_username = db.query(models.User).filter(models.User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create user
        user = AuthService.create_user(
            db=db,
            email=input_email,
            password=user_data.password,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=user_data.is_active
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@router.post("/login", response_model=Token, summary="User Login", tags=["Authentication"])
async def login_for_access_token(request: Request, db: Session = Depends(get_db)) -> Token:
    """Authenticate and return an access token. Accepts JSON or form-encoded credentials."""
    email: Optional[str] = None
    password: Optional[str] = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        if isinstance(body, dict):
            email = body.get("email") or body.get("username")
            password = body.get("password")
    else:
        form = await request.form()
        email = form.get("email") or form.get("username")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email/username and password required")

    user = AuthService.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated")

    access_token = AuthService.create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfileResponse: User profile information
    """
    try:
        return UserProfileResponse.model_validate(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update current user's profile information.
    
    Args:
        user_data: User update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Updated user information
    """
    try:
        # Check if username is taken (if being updated)
        if user_data.username and user_data.username != current_user.username:
            existing_username = db.query(models.User).filter(models.User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update fields
        if user_data.username is not None:
            current_user.username = user_data.username
        if user_data.first_name is not None:
            current_user.first_name = user_data.first_name
        if user_data.last_name is not None:
            current_user.last_name = user_data.last_name
        if user_data.age is not None:
            current_user.age = user_data.age
        if user_data.height_cm is not None:
            current_user.height_cm = user_data.height_cm
        if user_data.weight_kg is not None:
            current_user.weight_kg = user_data.weight_kg
        if user_data.date_of_birth is not None:
            try:
                # Accept datetime or date string; store date only
                if isinstance(user_data.date_of_birth, datetime.datetime):
                    current_user.date_of_birth = user_data.date_of_birth.date()
                else:
                    current_user.date_of_birth = user_data.date_of_birth
            except Exception:
                pass
        if user_data.gender is not None:
            current_user.gender = user_data.gender
        if user_data.activity_level is not None:
            current_user.activity_level = user_data.activity_level
        if user_data.health_goals is not None:
            current_user.health_goals = user_data.health_goals
        if user_data.dietary_preferences is not None:
            current_user.dietary_preferences = user_data.dietary_preferences
        # Update preferences when explicitly provided (including None to clear)
        if 'preferences' in user_data.model_fields_set:
            current_user.preferences = user_data.preferences
        
        db.commit()
        db.refresh(current_user)
        
        return UserProfileResponse.model_validate(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )


@router.post("/me/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Change current user's password.

    Args:
        password_data: Password change data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict with success message
    """
    try:
        # Verify current password
        if not AuthService.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Change password
        AuthService.change_password(db, current_user, password_data.new_password)

        return {
            "message": "Password changed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )


@router.post("/me/health-goals", response_model=UserProfileResponse)
async def update_health_goals(
    health_goals: HealthGoalsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update current user's health goals.

    This endpoint allows users to save their selected health goals (8 pillars).
    The goals are stored in the user's preferences under the 'health_goals' key.

    Args:
        health_goals: Health goals update data with selectedGoals array
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserProfileResponse: Updated user profile with new health goals

    Raises:
        HTTPException: If update fails
    """
    try:
        # Get current preferences or initialize empty dict
        preferences = current_user.preferences or {}

        # Update health_goals in preferences
        preferences["health_goals"] = health_goals.selectedGoals

        # Save updated preferences (create new dict to trigger SQLAlchemy update detection)
        current_user.preferences = dict(preferences)

        # Mark the field as modified to ensure SQLAlchemy detects the change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        # Commit changes
        db.commit()
        db.refresh(current_user)

        return UserProfileResponse.model_validate(current_user)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating health goals: {str(e)}"
        )


@router.post("/me/survey", response_model=UserProfileResponse)
async def submit_user_survey(
    survey_data: UserSurveyData,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Submit complete user survey data from onboarding flow.

    This endpoint processes the user's onboarding survey, translates health pillar names
    to IDs for backward compatibility, and stores both the translated IDs and complete
    survey data in user preferences.

    Args:
        survey_data: Complete survey data including health pillars, dietary restrictions, etc.
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserProfileResponse: Updated user profile with survey data

    Raises:
        HTTPException: If survey submission fails or pillar names are invalid
    """
    try:
        # Create reverse mapping: pillar_name -> pillar_id
        pillar_name_to_id = {
            pillar_data["name"]: pillar_id
            for pillar_id, pillar_data in HEALTH_PILLARS.items()
        }

        # Translate health pillar names to IDs
        pillar_ids = []
        for pillar_name in survey_data.healthPillars:
            pillar_id = pillar_name_to_id.get(pillar_name)
            if pillar_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid health pillar name: {pillar_name}"
                )
            pillar_ids.append(pillar_id)

        # Get current preferences or initialize empty dict
        # Parse JSON string if needed
        if isinstance(current_user.preferences, str):
            import json
            preferences = json.loads(current_user.preferences) if current_user.preferences else {}
        else:
            preferences = current_user.preferences or {}

        # Store translated pillar IDs for backward compatibility
        preferences["health_goals"] = pillar_ids

        # Store complete survey data for LLM meal plan generation
        preferences["survey_data"] = survey_data.model_dump()

        # Save updated preferences as JSON string
        import json
        current_user.preferences = json.dumps(preferences)

        # Mark the field as modified to ensure SQLAlchemy detects the change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        # Commit changes
        db.commit()
        db.refresh(current_user)

        return UserProfileResponse.model_validate(current_user)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting survey: {str(e)}"
        )


@router.post("/me/llm-meal-plan", response_model=LLMMealPlanResponse)
async def generate_llm_meal_plan_endpoint(
    include_recipes: bool = False,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered personalized meal plan using Claude Haiku LLM.

    This endpoint creates a 1-day meal plan based on the user's survey data,
    using the Claude Haiku model for cost-effective, high-quality meal planning.

    Args:
        include_recipes: Whether to include detailed recipe information (ingredients, instructions, etc.)
        current_user: Current authenticated user
        db: Database session

    Returns:
        LLMMealPlanResponse: Generated meal plan with health goal summary

    Raises:
        HTTPException 503: If meal plan generation fails
        HTTPException 400: If user has no survey data
    """
    try:
        # Import the LLM service
        from ..services import llm_service

        # Generate meal plan using LLM (1 day)
        daily_plans = await llm_service.generate_llm_meal_plan(
            user=current_user,
            num_days=1,
            include_recipes=include_recipes,
            db=db
        )

        # Save generated meals to database as templates
        from ..models.meal import Meal, MealSource
        saved_meal_ids = []

        for daily_plan in daily_plans:
            for meal_data in daily_plan.meals:
                # Create Meal record
                new_meal = Meal(
                    user_id=current_user.id,
                    name=meal_data.name,
                    meal_type=meal_data.type,
                    source=MealSource.GENERATED,
                    calories=meal_data.calories,
                    protein_g=meal_data.nutrition.get('protein_g') if hasattr(meal_data, 'nutrition') and meal_data.nutrition else None,
                    carbs_g=meal_data.nutrition.get('carbs_g') if hasattr(meal_data, 'nutrition') and meal_data.nutrition else None,
                    fat_g=meal_data.nutrition.get('fat_g') if hasattr(meal_data, 'nutrition') and meal_data.nutrition else None,
                    description=meal_data.description,
                    servings=meal_data.servings if hasattr(meal_data, 'servings') else None,
                    prep_time_minutes=meal_data.prep_time_minutes if hasattr(meal_data, 'prep_time_minutes') else None,
                    cook_time_minutes=meal_data.cook_time_minutes if hasattr(meal_data, 'cook_time_minutes') else None,
                    ingredients=meal_data.ingredients if hasattr(meal_data, 'ingredients') else None,
                    instructions=meal_data.instructions if hasattr(meal_data, 'instructions') else None,
                    nutrition_info=meal_data.nutrition if hasattr(meal_data, 'nutrition') else None,
                    date_logged=None  # Not logged yet, just a template
                )
                db.add(new_meal)
                db.flush()  # Get the ID
                saved_meal_ids.append(new_meal.id)

        db.commit()
        logger.info(f"Saved {len(saved_meal_ids)} generated meals to database for user {current_user.id}")

        # Construct health goal summary
        health_goal_summary = None
        # Parse preferences JSON string if needed
        import json
        if isinstance(current_user.preferences, str):
            preferences = json.loads(current_user.preferences) if current_user.preferences else {}
        else:
            preferences = current_user.preferences or {}

        if preferences and "health_goals" in preferences:
            health_goal_ids = preferences["health_goals"]
            health_goal_names = [
                get_pillar_name(goal_id) for goal_id in health_goal_ids
            ]
            health_goal_summary = (
                f"This meal plan is designed to support your health goals: "
                f"{', '.join(health_goal_names)}. "
                f"Meals are tailored to your dietary preferences and restrictions."
            )

        return LLMMealPlanResponse(
            plan=daily_plans,
            health_goal_summary=health_goal_summary
        )

    except llm_service.LLMResponseError as e:
        logger.error(f"LLM meal plan generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate meal plan at this time."
        )
    except ValueError as e:
        logger.error(f"User survey data missing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete the user survey before generating a meal plan."
        )
    except Exception as e:
        logger.error(f"Unexpected error generating LLM meal plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate meal plan at this time."
        )


@router.post("/me/meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: Optional[MealPlanRequest] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized meal plan for the current user.

    This endpoint creates a multi-day meal plan based on the user's preferences,
    health goals, and nutritional targets. Ingredients are prioritized based on
    the user's selected health pillars. For MVP, it returns a mock meal plan.
    In production, this will integrate with LLM-based meal planning algorithms.

    Args:
        request: Optional meal plan generation parameters
        current_user: Currently authenticated user
        db: Database session

    Returns:
        MealPlanResponse: Generated meal plan with daily meals and health goal summary

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Get user preferences for ingredient prioritization
        preferences = current_user.preferences or {}
        user_health_goals = preferences.get("health_goals", [])
        calorie_target = preferences.get("calorie_goal", 2000)

        # Determine number of days (default to 7)
        num_days = 7
        if request and request.num_days:
            num_days = request.num_days

        # Prioritized ingredient selection based on user health goals
        preferred_ingredients = []
        health_goal_summary = None

        if user_health_goals:
            # Fetch ingredients that align with user's health goals
            try:
                for pillar_id in user_health_goals:
                    # Get ingredients for each health pillar
                    pillar_ingredients = IngredientEntity.get_ingredients_by_pillar(
                        db, pillar_id, skip=0, limit=10
                    )
                    preferred_ingredients.extend(pillar_ingredients)

                # Remove duplicates while preserving order
                seen = set()
                preferred_ingredients = [
                    ing for ing in preferred_ingredients
                    if not (ing.id in seen or seen.add(ing.id))
                ]
            except Exception as e:
                # If ingredient fetching fails, continue with generic plan
                print(f"Warning: Could not fetch preferred ingredients: {e}")
                preferred_ingredients = []

            # Generate health goal summary
            pillar_names = [get_pillar_name(pid) for pid in user_health_goals if get_pillar_name(pid)]
            if pillar_names:
                if len(pillar_names) == 1:
                    health_goal_summary = f"This meal plan prioritizes ingredients for {pillar_names[0]}."
                elif len(pillar_names) == 2:
                    health_goal_summary = f"This meal plan prioritizes ingredients for {pillar_names[0]} and {pillar_names[1]}."
                else:
                    last_goal = pillar_names[-1]
                    other_goals = ", ".join(pillar_names[:-1])
                    health_goal_summary = f"This meal plan prioritizes ingredients for {other_goals}, and {last_goal}."
        else:
            health_goal_summary = "This meal plan is generated without specific health goals."

        # Generate mock meal plan with ingredient-aware descriptions
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Mock ingredient names based on preferred ingredients (MVP approach)
        ingredient_names = []
        if preferred_ingredients:
            ingredient_names = [ing.name for ing in preferred_ingredients[:15]]

        # Fallback generic ingredients if no preferred ingredients
        if not ingredient_names:
            ingredient_names = [
                "Greek yogurt", "berries", "granola", "salmon", "quinoa",
                "chicken breast", "spinach", "broccoli", "sweet potato",
                "almonds", "avocado", "eggs", "oats", "apples", "carrots"
            ]

        meal_plan = []
        total_calories = 0

        for day_index in range(num_days):
            day_name = days_of_week[day_index % 7]

            # Generate ingredient-aware mock meals
            # In production, these would be generated by LLM using preferred_ingredients
            daily_meals = [
                MealItem(
                    type="breakfast",
                    name="Healthy Breakfast Bowl",
                    calories=400,
                    description=f"{ingredient_names[0] if len(ingredient_names) > 0 else 'Yogurt'} with {ingredient_names[2] if len(ingredient_names) > 2 else 'granola'}, fresh berries, and honey"
                ),
                MealItem(
                    type="snack",
                    name="Morning Snack",
                    calories=150,
                    description=f"{ingredient_names[13] if len(ingredient_names) > 13 else 'Apple'} slices with {ingredient_names[9] if len(ingredient_names) > 9 else 'almond'} butter"
                ),
                MealItem(
                    type="lunch",
                    name="Grilled Protein Salad",
                    calories=550,
                    description=f"Mixed greens with grilled {ingredient_names[5] if len(ingredient_names) > 5 else 'chicken'}, {ingredient_names[6] if len(ingredient_names) > 6 else 'vegetables'}, and balsamic vinaigrette"
                ),
                MealItem(
                    type="snack",
                    name="Afternoon Snack",
                    calories=200,
                    description=f"Hummus with {ingredient_names[14] if len(ingredient_names) > 14 else 'carrot'} and cucumber sticks"
                ),
                MealItem(
                    type="dinner",
                    name="Baked Protein with Grains",
                    calories=650,
                    description=f"Baked {ingredient_names[3] if len(ingredient_names) > 3 else 'salmon'} with {ingredient_names[4] if len(ingredient_names) > 4 else 'quinoa'} and roasted vegetables"
                ),
            ]

            daily_plan = DailyMealPlan(day=day_name, meals=daily_meals)
            meal_plan.append(daily_plan)

            # Calculate total calories for this day
            day_calories = sum(meal.calories for meal in daily_meals)
            total_calories += day_calories

        # Calculate average calories per day
        avg_calories = total_calories // num_days

        return MealPlanResponse(
            plan=meal_plan,
            total_days=num_days,
            average_calories_per_day=avg_calories,
            health_goal_summary=health_goal_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal plan: {str(e)}"
        )


@router.post("/me/deactivate")
async def deactivate_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Deactivate current user's account.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with success message
    """
    try:
        AuthService.deactivate_user(db, current_user)
        
        return {
            "message": "Account deactivated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating account: {str(e)}"
        )


@router.delete("/me")
async def delete_my_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Soft delete (deactivate) the current user's account.
    Sets is_active=False to preserve data while disabling access.
    """
    try:
        AuthService.deactivate_user(db, current_user)
        return {"message": "Account deactivated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating account: {str(e)}"
        )

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Initiate password reset. For MVP, generate a reset token and log the link.
    """
    try:
        token = AuthService.generate_password_reset_token(payload.email)
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        import logging
        logger = logging.getLogger(__name__)
        # Try to send email; always log the link for dev
        sent = AuthService.send_email(
            subject="FlavorLab Password Reset",
            to_email=payload.email,
            html_body=f"<p>Click the link to reset your password:</p><p><a href=\"{reset_link}\">Reset Password</a></p>",
            text_body=f"Reset your password: {reset_link}"
        )
        logger.info("Password reset link for %s: %s (email sent=%s)", payload.email, reset_link, sent)
        return {"message": "If the email exists, a reset link has been sent."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating password reset: {str(e)}"
        )


@router.post("/reset-password")
async def reset_password(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using a token.
    """
    try:
        email = AuthService.validate_password_reset_token(payload.token)
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        user = AuthService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        AuthService.change_password(db, user, payload.new_password)
        return {"message": "Password has been reset successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )


@router.put("/me/avatar", response_model=UserProfileResponse)
async def update_user_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Upload and update the current user's avatar image.
    Stores files under ./static/avatars and returns updated user profile.
    """
    try:
        # Ensure directories exist
        os.makedirs("static/avatars", exist_ok=True)

        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")

        unique_name = f"{uuid4()}{ext}"
        fs_path = os.path.join("static", "avatars", unique_name)

        with open(fs_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save URL path
        current_user.avatar_url = f"/static/avatars/{unique_name}"
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return UserProfileResponse.model_validate(current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading avatar: {str(e)}")
@router.get("/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_verified_user),
):
    """
    Get user statistics (requires verified user).
    
    Args:
        db: Database session
        current_user: Current verified user
        
    Returns:
        UserStatsResponse: User statistics
    """
    try:
        from sqlalchemy import func
        from datetime import timedelta
        
        # Total users
        total_users = db.query(models.User).count()
        
        # Active users
        active_users = db.query(models.User).filter(models.User.is_active == True).count()
        
        # Verified users
        verified_users = db.query(models.User).filter(models.User.is_verified == True).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.datetime.now(datetime.UTC) - timedelta(days=30)
        recent_registrations = db.query(models.User).filter(
            models.User.created_at >= thirty_days_ago
        ).count()
        
        # Last updated
        last_updated = db.query(func.max(models.User.updated_at)).scalar()
        
        return UserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            recent_registrations=recent_registrations,
            last_updated=last_updated
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user statistics: {str(e)}"
        )


# Admin endpoints (require verified user)
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_verified_user)
):
    """
    Get user by ID (requires verified user).
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current verified user
        
    Returns:
        UserResponse: User information
    """
    try:
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.put("/{user_id}/activate")
async def activate_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_verified_user)
):
    """
    Activate a user account (requires verified user).
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current verified user
        
    Returns:
        Dict with success message
    """
    try:
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )
        
        AuthService.activate_user(db, user)
        
        return {
            "message": f"User account '{user_id}' activated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating user account: {str(e)}"
        )


@router.put("/{user_id}/verify")
async def verify_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_verified_user)
):
    """
    Verify a user account (requires verified user).
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current verified user
        
    Returns:
        Dict with success message
    """
    try:
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )
        
        user.is_verified = True
        db.commit()
        
        return {
            "message": f"User account '{user_id}' verified successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying user account: {str(e)}"
        )


@router.put("/me/nutrition-goal", response_model=DailyCaloriesSummaryResponse)
async def set_nutrition_goal(
    request: SetCalorieGoalRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Set or update the user's daily calorie goal and return updated dashboard summary.

    This endpoint:
    1. Creates or updates the user's daily calorie goal
    2. Calculates total calories consumed today
    3. Returns complete dashboard summary
    """
    from ..models.calorie_tracking import DailyCalorieGoal
    from ..models.meal import Meal
    from datetime import date

    # Get today's date
    today = date.today()

    # Find or create calorie goal
    calorie_goal = db.query(DailyCalorieGoal).filter(
        DailyCalorieGoal.user_id == current_user.id
    ).first()

    if calorie_goal:
        # Update existing goal
        calorie_goal.goal_calories = request.goal_calories
    else:
        # Create new goal
        calorie_goal = DailyCalorieGoal(
            user_id=current_user.id,
            goal_calories=request.goal_calories
        )
        db.add(calorie_goal)

    db.commit()
    db.refresh(calorie_goal)

    # Calculate total consumed today from logged meals
    todays_meals = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.date_logged == today
    ).all()

    total_consumed = sum(m.calories or 0 for m in todays_meals)
    remaining = request.goal_calories - total_consumed

    # Build logged meals summary
    from ..schemas.meals import LoggedMealSummary
    from datetime import datetime

    logged_meals = [
        LoggedMealSummary(
            log_id=m.id,
            name=m.name,
            calories=int(m.calories or 0),
            meal_type=m.meal_type or "Unknown",
            logged_at=m.updated_at.isoformat() if m.updated_at else datetime.now().isoformat()
        )
        for m in todays_meals
    ]

    return DailyCaloriesSummaryResponse(
        daily_goal=request.goal_calories,
        total_consumed=int(total_consumed),
        remaining=remaining,
        logged_meals_today=logged_meals
    )


@router.get("/me/daily-summary", response_model=DailyCaloriesSummaryResponse)
async def get_daily_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> DailyCaloriesSummaryResponse:
    """
    Get the current day's nutrition summary for dashboard hydration.

    Returns:
        Complete dashboard state with daily_goal, total_consumed,
        remaining, and logged_meals_today
    """
    from ..services.daily_summary_service import create_daily_summary

    # Get authoritative dashboard state
    summary = create_daily_summary(current_user.id, db)

    return DailyCaloriesSummaryResponse(**summary)

