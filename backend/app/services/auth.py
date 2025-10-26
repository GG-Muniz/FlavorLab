"""
Authentication service for FlavorLab.

This module provides authentication utilities including JWT token management,
password hashing, and user authentication.
"""

import os
import json
import bcrypt
import datetime
import time
from datetime import timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from .. import models
from ..schemas.user import TokenData, UserResponse
from ..config import get_settings
from ..database import get_db
import smtplib
from email.message import EmailMessage

# Get settings
settings = get_settings()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/users/login")

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class AuthService:
    """Authentication service class."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        """
        Create a new access token with exp as POSIX timestamp.
        Always enforce exp > current time by at least 60 seconds.
        """
        # Current UTC timestamp (aware)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_ts = int(now_utc.timestamp())
        # Local timezone offset in seconds (aware, no deprecations)
        local_offset = now_utc.astimezone().utcoffset()
        offset_sec = int(local_offset.total_seconds()) if local_offset else 0

        # Determine desired delta seconds
        if expires_delta and expires_delta.total_seconds() > 0:
            delta_seconds = int(expires_delta.total_seconds())
        else:
            minutes = ACCESS_TOKEN_EXPIRE_MINUTES if isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, (int, float)) else 15
            if not minutes or minutes <= 0:
                minutes = 15
            delta_seconds = int(minutes * 60)

        # Enforce minimum 60s to avoid clock drift issues
        if delta_seconds < 60:
            delta_seconds = 60
        # Add absolute local offset so exp beats naive utcnow().timestamp() regardless of sign
        if offset_sec != 0:
            delta_seconds += abs(offset_sec)
        expire_ts = now_ts + delta_seconds
        to_encode = {**data, "exp": expire_ts}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            TokenData: Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_claim = payload.get("user_id") or payload.get("sub")
            email: str = payload.get("email")

            if user_id_claim is None or email is None:
                return None

            try:
                user_id_int = int(user_id_claim)
            except (TypeError, ValueError):
                return None

            return TokenData(user_id=user_id_int, email=email)
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User: Authenticated user or None if authentication fails
        """
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User: User object or None if not found
        """
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User: User object or None if not found
        """
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, email: str, password: str, **kwargs) -> models.User:
        """
        Create a new user.
        
        Args:
            db: Database session
            email: User email
            password: User password
            **kwargs: Additional user fields
            
        Returns:
            User: Created user object
        """
        hashed_password = AuthService.get_password_hash(password)
        
        user = models.User(
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user_last_login(db: Session, user: models.User) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            db: Database session
            user: User object to update
        """
        user.update_last_login()
        db.commit()
    
    @staticmethod
    def change_password(db: Session, user: models.User, new_password: str) -> None:
        """
        Change user's password.
        
        Args:
            db: Database session
            user: User object
            new_password: New password
        """
        user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()
    
    @staticmethod
    def deactivate_user(db: Session, user: models.User) -> None:
        """
        Deactivate a user account.
        
        Args:
            db: Database session
            user: User object
        """
        user.is_active = False
        db.commit()
    
    @staticmethod
    def activate_user(db: Session, user: models.User) -> None:
        """
        Activate a user account.
        
        Args:
            db: Database session
            user: User object
        """
        user.is_active = True
        db.commit()

    @staticmethod
    def delete_user_by_email(db: Session, email: str) -> bool:
        """
        Delete a user by email (case-insensitive). Returns True if deleted.
        Intended for development/demo flows to reset a special account.
        """
        user = db.query(models.User).filter(models.User.email.ilike(email)).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    # --- Password reset helpers ---
    @staticmethod
    def generate_password_reset_token(email: str, expires_minutes: int = 30) -> str:
        """
        Generate a short‑lived JWT token for password reset.
        Encodes the email as subject and a purpose claim.
        """
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        exp_dt = now_utc + datetime.timedelta(minutes=max(1, int(expires_minutes)))
        exp_ts = int(exp_dt.timestamp())
        payload = {"sub": email, "prp": "password_reset", "exp": exp_ts}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def validate_password_reset_token(token: str) -> Optional[str]:
        """
        Validate a password reset token and return the email if valid.
        Returns None if invalid or expired.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("prp") != "password_reset":
                return None
            email = payload.get("sub")
            if not isinstance(email, str) or not email:
                return None
            return email
        except JWTError:
            return None

    # --- Email helpers (SMTP) ---
    @staticmethod
    def send_email(subject: str, to_email: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """Send an email using configured SMTP. Returns True if sent, else False."""
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = settings.email_from
        msg['To'] = to_email
        if text_body:
            msg.set_content(text_body)
        msg.add_alternative(html_body, subtype='html')

        try:
            if settings.email_tls:
                server = smtplib.SMTP(settings.email_host, settings.email_port, timeout=5)
                server.starttls()
            else:
                server = smtplib.SMTP(settings.email_host, settings.email_port, timeout=5)
            if settings.email_user and settings.email_password:
                server.login(settings.email_user, settings.email_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception:
            return False


# Dependency functions for FastAPI
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Get the current authenticated user.
    
    Args:
        token: JWT token from request
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = AuthService.verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = AuthService.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    """
    Get the current verified user.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not verified"
        )
    return current_user


# Utility functions
def create_token_for_user(user: models.User) -> str:
    """
    Create an access token for a user.
    
    Args:
        user: User object
        
    Returns:
        str: JWT access token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    return access_token


def get_token_expiration_time() -> datetime:
    """
    Get the token expiration time.
    
    Returns:
        datetime: Token expiration time
    """
    return datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

