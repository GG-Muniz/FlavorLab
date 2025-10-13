"""
FlavorLab FastAPI Application

This is the main entry point for the FlavorLab backend API.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .api import health, users, entities, relationships, flavor, calorie_tracker
from .database import engine, Base, SessionLocal
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
app.include_router(users.router, prefix=settings.api_prefix, tags=["Users", "Authentication"])
app.include_router(entities.router, prefix=settings.api_prefix, tags=["Entities"])
app.include_router(relationships.router, prefix=settings.api_prefix, tags=["Relationships"])
app.include_router(flavor.router, prefix=settings.api_prefix, tags=["Flavor"])
app.include_router(calorie_tracker.router, prefix=settings.api_prefix, tags=["Calorie Tracking"])

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
