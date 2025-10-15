"""
Health API endpoints for FlavorLab.

This module provides REST API endpoints for health-related data including
health pillars information for the frontend Health Pillar selection interface.
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..models.health_pillars import get_all_pillars

# Create router
router = APIRouter(prefix="/health", tags=["health"])


class PillarResponse(BaseModel):
    """
    Schema for health pillar response.

    Represents a single health pillar with its ID, name, and description.
    Used in the frontend for displaying health goal options to users.
    """
    id: int = Field(..., description="Unique pillar ID (1-8)", ge=1, le=8)
    name: str = Field(..., description="Display name of the health pillar")
    description: str = Field(..., description="Detailed description of the pillar's benefits")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Increased Energy",
                "description": "Supports sustained energy levels and reduces fatigue"
            }
        }


@router.get("/pillars", response_model=List[PillarResponse])
async def list_health_pillars():
    """
    List all available health pillars.

    This endpoint returns all 8 health pillars that users can select as their
    health goals. This data is used by the frontend to populate the health goal
    selection interface.

    **No authentication required** - this is public reference data.

    Returns:
        List[PillarResponse]: List of all 8 health pillars with their details

    Example response:
        ```json
        [
            {
                "id": 1,
                "name": "Increased Energy",
                "description": "Supports sustained energy levels and reduces fatigue"
            },
            {
                "id": 2,
                "name": "Improved Digestion",
                "description": "Promotes healthy digestive function and gut health"
            },
            ...
        ]
        ```
    """
    # Get all pillars from the health_pillars module
    pillars = get_all_pillars()

    # Convert to response model format
    return [
        PillarResponse(
            id=pillar["id"],
            name=pillar["name"],
            description=pillar["description"]
        )
        for pillar in pillars
    ]
