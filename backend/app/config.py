"""
Configuration settings for FlavorLab.

This module provides configuration management using environment variables
and sensible defaults for the FlavorLab application.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra fields without raising an error
    )

    # General settings
    app_name: str = Field(default="FlavorLab", json_schema_extra={"env": "APP_NAME"})
    debug: bool = Field(default=False, json_schema_extra={"env": "DEBUG"})
    version: str = Field(default="1.0.0", json_schema_extra={"env": "VERSION"})

    # Database settings
    database_name: str = Field(default="flavorlab.db", json_schema_extra={"env": "DATABASE_NAME"})
    database_url: Optional[str] = Field(default=None, json_schema_extra={"env": "DATABASE_URL"})

    # API settings
    api_prefix: str = Field(default="/api/v1", json_schema_extra={"env": "API_PREFIX"})
    cors_origins: list = Field(default=["*"], json_schema_extra={"env": "CORS_ORIGINS"})

    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production", json_schema_extra={"env": "SECRET_KEY"})
    access_token_expire_minutes: int = Field(default=30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})

    # Email/SMTP settings
    email_host: str = Field(default="localhost", json_schema_extra={"env": "EMAIL_HOST"})
    email_port: int = Field(default=25, json_schema_extra={"env": "EMAIL_PORT"})
    email_user: Optional[str] = Field(default=None, json_schema_extra={"env": "EMAIL_USER"})
    email_password: Optional[str] = Field(default=None, json_schema_extra={"env": "EMAIL_PASSWORD"})
    email_from: str = Field(default="noreply@flavorlab.local", json_schema_extra={"env": "EMAIL_FROM"})
    email_tls: bool = Field(default=False, json_schema_extra={"env": "EMAIL_TLS"})

    # Demo/testing settings
    demo_email: str = Field(default="demo@flavorlab.local", json_schema_extra={"env": "DEMO_EMAIL"})

    # Data settings
    json_data_path: str = Field(default="../", json_schema_extra={"env": "JSON_DATA_PATH"})
    entities_file: str = Field(default="entities.json", json_schema_extra={"env": "ENTITIES_FILE"})
    relationships_file: str = Field(default="entity_relationships.json", json_schema_extra={"env": "RELATIONSHIPS_FILE"})

    # Script settings
    batch_size: int = Field(default=100, json_schema_extra={"env": "BATCH_SIZE"})


# Global settings instance
_settings: Optional[Settings] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    """
    return Settings()

# Expose module-level settings for convenience in tests and simple imports
settings = get_settings()


def reload_settings() -> Settings:
    """
    Reload application settings.
    
    This function forces a reload of settings from environment variables
    and .env file. Useful for testing or when settings change at runtime.
    
    Returns:
        Settings: New settings instance
    """
    global _settings
    _settings = Settings()
    return _settings


# Convenience function to get specific settings
def get_database_name() -> str:
    """Get database name from settings."""
    return get_settings().database_name


def get_debug_mode() -> bool:
    """Get debug mode from settings."""
    return get_settings().debug


def get_api_prefix() -> str:
    """Get API prefix from settings."""
    return get_settings().api_prefix