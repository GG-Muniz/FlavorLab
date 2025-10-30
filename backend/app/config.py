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

    # Cloudinary (images)
    cloudinary_cloud_name: Optional[str] = Field(default=None, json_schema_extra={"env": "CLOUDINARY_CLOUD_NAME"})
    cloudinary_base_url: Optional[str] = Field(default=None, json_schema_extra={"env": "CLOUDINARY_BASE_URL"})
    cloudinary_folder: str = Field(default="flavorlab/ingredients", json_schema_extra={"env": "CLOUDINARY_FOLDER"})
    # If true, ingestion will generate Cloudinary fetch URLs from Unsplash Source for dev
    cloudinary_use_unsplash_fallback: bool = Field(default=True, json_schema_extra={"env": "CLOUDINARY_USE_UNSPLASH_FALLBACK"})
    # If true, use Cloudinary image/fetch as proxy for Unsplash; if false, use direct Unsplash URLs
    cloudinary_proxy_fetch: bool = Field(default=False, json_schema_extra={"env": "CLOUDINARY_PROXY_FETCH"})
    # Optional Upload API config (prefer unsigned preset for dev)
    cloudinary_upload_preset: Optional[str] = Field(default=None, json_schema_extra={"env": "CLOUDINARY_UPLOAD_PRESET"})
    cloudinary_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "CLOUDINARY_API_KEY"})
    cloudinary_api_secret: Optional[str] = Field(default=None, json_schema_extra={"env": "CLOUDINARY_API_SECRET"})
    # Unsplash API (official) for reliable image search
    unsplash_access_key: Optional[str] = Field(default=None, json_schema_extra={"env": "UNSPLASH_ACCESS_KEY"})
    # USDA FoodData Central API key (for nutrition enrichment)
    fdc_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "FDC_API_KEY"})

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

    # LLM settings
    anthropic_api_key: str = Field(..., json_schema_extra={"env": "ANTHROPIC_API_KEY"})
    openai_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "OPENAI_API_KEY"})
    llm_provider: str = Field(default="anthropic", json_schema_extra={"env": "LLM_PROVIDER"})  # "anthropic" or "openai"
    llm_model: str = Field(default="claude-3-5-haiku-20241022", json_schema_extra={"env": "LLM_MODEL"})


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