"""
Database configuration and setup for FlavorLab.

This module provides SQLAlchemy database configuration, engine setup,
and session management for the FlavorLab application.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
from .config import get_settings

# Get settings
settings = get_settings()

# Create SQLAlchemy engine
# SQLite database file will be created in the backend directory
DATABASE_URL = f"sqlite:///./{settings.database_name}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.debug,  # Set to True for SQL query logging
    pool_pre_ping=True,   # Verify connections before use
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    This function provides a database session for FastAPI dependency injection.
    It ensures the session is properly closed after use.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables.
    
    This function creates all tables defined in the models.
    Should be called during application startup or database initialization.
    """
    # Import all models to ensure they are registered with Base
    from .models import Entity, IngredientEntity, NutrientEntity, CompoundEntity, RelationshipEntity, User
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data in the database!
    Use with caution, typically only for development/testing.
    """
    # Import all models to ensure they are registered with Base
    from .models import Entity, IngredientEntity, NutrientEntity, CompoundEntity, RelationshipEntity, User
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


def get_database_url() -> str:
    """
    Get the database URL.
    
    Returns:
        str: Database connection URL
    """
    return DATABASE_URL


def check_database_connection() -> bool:
    """
    Check if the database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database information.
    
    Returns:
        dict: Database information including URL, tables, etc.
    """
    info = {
        "database_url": DATABASE_URL,
        "database_name": settings.database_name,
        "connection_working": check_database_connection()
    }
    
    try:
        with engine.connect() as connection:
            # Get list of tables
            result = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result.fetchall()]
            info["tables"] = tables
            info["table_count"] = len(tables)
    except Exception as e:
        info["error"] = str(e)
    
    return info
