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
    PasswordReset,
    PasswordResetConfirm,
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

