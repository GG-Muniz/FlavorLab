"""
User API endpoints for FlavorLab.

This module provides REST API endpoints for user operations including
registration, authentication, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
import datetime
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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
    Token,
    TokenData,
    UserStatsResponse,
    UserLogin,
)
from ..schemas.meal_plan import (
    MealPlanResponse,
    MealPlanRequest,
    MealItem,
    DailyMealPlan,
)
from ..services.auth import AuthService, get_current_active_user, get_current_verified_user
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


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
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
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
            email=user_data.email,
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

