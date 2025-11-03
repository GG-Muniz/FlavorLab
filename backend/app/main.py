"""
FlavorLab FastAPI Application

This is the main entry point for the FlavorLab backend API.
"""

import logging
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import health, users, entities, relationships, flavor, calorie_tracker, nutrition, tips, meals, water_tracker, journal
from .database import engine, Base, SessionLocal, ensure_user_columns, ensure_entity_columns, ensure_calorie_goal_columns
from .config import get_settings


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    """
    logger.info("Application startup...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Ensure new columns exist (SQLite lightweight migration)
    ensure_user_columns()
    ensure_entity_columns()
    ensure_calorie_goal_columns()
    # Ensure static directories exist for avatar uploads
    os.makedirs("static/avatars", exist_ok=True)
    logger.info("Database tables created.")
    yield
    logger.info("Application shutdown...")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="FlavorLab API - An intelligent cooking platform.",
    lifespan=lifespan
)

# CORS Middleware (settings-driven origins; add common dev IPs)
_origins = settings.cors_origins or []
if isinstance(_origins, str):
    _origins = [_origins]
additional_dev_origins = [
    "http://192.168.9.86:5173",  # merge: dev LAN IP from incoming branch
]
for origin in additional_dev_origins:
    if origin not in _origins:
        _origins.append(origin)

if "*" in _origins or not _origins:
    _origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.9.213:5173",
        "http://192.168.9.86:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for avatars and other assets (allow start even if dir absent)
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")

# API Routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
app.include_router(users.router, prefix=settings.api_prefix, tags=["Users", "Authentication"])
app.include_router(nutrition.router, prefix=settings.api_prefix, tags=["Nutrition"])
app.include_router(entities.router, prefix=settings.api_prefix, tags=["Entities"])
app.include_router(tips.router, prefix=settings.api_prefix, tags=["Tips"])
app.include_router(relationships.router, prefix=settings.api_prefix, tags=["Relationships"])
app.include_router(flavor.router, prefix=settings.api_prefix, tags=["Flavor"])
app.include_router(calorie_tracker.router, prefix=settings.api_prefix, tags=["Calorie Tracking"])
app.include_router(water_tracker.router, prefix=settings.api_prefix, tags=["Water Tracking"])
app.include_router(meals.router, prefix=settings.api_prefix, tags=["Meals"])
app.include_router(journal.router, prefix=settings.api_prefix, tags=["Journal"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
