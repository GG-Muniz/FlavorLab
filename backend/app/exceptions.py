"""
Custom exceptions for FlavorLab.

This module defines custom exception classes for consistent error handling
across the FlavorLab application.
"""

from typing import Any, Dict, Optional


class FlavorLabException(Exception):
    """Base exception class for FlavorLab."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(FlavorLabException):
    """Raised when an entity is not found."""
    
    def __init__(self, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Entity with ID '{entity_id}' not found"
        super().__init__(message, details)


class RelationshipNotFoundError(FlavorLabException):
    """Raised when a relationship is not found."""
    
    def __init__(self, relationship_id: int, details: Optional[Dict[str, Any]] = None):
        message = f"Relationship with ID '{relationship_id}' not found"
        super().__init__(message, details)


class UserNotFoundError(FlavorLabException):
    """Raised when a user is not found."""
    
    def __init__(self, user_id: int, details: Optional[Dict[str, Any]] = None):
        message = f"User with ID '{user_id}' not found"
        super().__init__(message, details)


class AuthenticationError(FlavorLabException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class AuthorizationError(FlavorLabException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ValidationError(FlavorLabException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if field:
            message = f"Validation error in field '{field}': {message}"
        super().__init__(message, details)


class DuplicateEntityError(FlavorLabException):
    """Raised when trying to create a duplicate entity."""
    
    def __init__(self, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Entity with ID '{entity_id}' already exists"
        super().__init__(message, details)


class DuplicateUserError(FlavorLabException):
    """Raised when trying to create a duplicate user."""
    
    def __init__(self, email: str, details: Optional[Dict[str, Any]] = None):
        message = f"User with email '{email}' already exists"
        super().__init__(message, details)


class SearchError(FlavorLabException):
    """Raised when search operations fail."""
    
    def __init__(self, message: str = "Search operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class DatabaseError(FlavorLabException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

