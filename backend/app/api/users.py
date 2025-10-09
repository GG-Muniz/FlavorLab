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
from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    ChangePasswordRequest,
    Token,
    TokenData,
    UserStatsResponse,
    UserLogin,
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

