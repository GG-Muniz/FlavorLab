"""
Pydantic schemas for FlavorLab entities.

This module defines the request/response schemas for entity-related API endpoints.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AttributeValue(BaseModel):
    """Schema for attribute values with source and confidence."""
    value: Any
    source: Optional[str] = None
    confidence: Optional[int] = Field(None, ge=1, le=5)


class EntityBase(BaseModel):
    """Base schema for entity operations."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    primary_classification: str = Field(..., min_length=1, max_length=100)
    classifications: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    # Allow flexible attribute shapes (flattened numbers, arrays, etc.)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    image_url: Optional[str] = Field(None, max_length=512)
    image_attribution: Optional[str] = Field(None, max_length=512)
    is_active: bool = True


class EntityCreate(EntityBase):
    """Schema for creating a new entity."""
    id: str = Field(..., min_length=1, max_length=255)


class EntityUpdate(BaseModel):
    """Schema for updating an existing entity."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    primary_classification: Optional[str] = Field(None, min_length=1, max_length=100)
    classifications: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = Field(None, max_length=512)
    image_attribution: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None


class EntityResponse(EntityBase):
    """Schema for entity responses."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique identifier for the entity")
    created_at: Any = Field(..., description="Timestamp of when the entity was created")
    updated_at: Any = Field(..., description="Timestamp of when the entity was last updated")


class EntityListResponse(BaseModel):
    """Schema for paginated entity list responses."""
    entities: List[EntityResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class HealthOutcomeSchema(BaseModel):
    """Schema for health outcome information with health pillar mappings."""
    outcome: str
    confidence: int = Field(ge=1, le=5)
    added_at: datetime
    updated_at: Optional[datetime] = None
    pillars: List[int] = Field(default_factory=list, description="Health pillar IDs (1-8) associated with this outcome")


class CompoundInfo(BaseModel):
    """Schema for compound information."""
    compound_id: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    added_at: datetime
    updated_at: Optional[datetime] = None


class IngredientEntityResponse(EntityResponse):
    """Schema for ingredient entity responses with structured health outcomes."""
    foodb_priority: Optional[str] = None
    health_outcomes: List[HealthOutcomeSchema] = Field(
        default_factory=list,
        description="Health outcomes with pillar mappings"
    )
    compounds: List[CompoundInfo] = Field(
        default_factory=list,
        description="Compound information"
    )


class NutrientEntityResponse(EntityResponse):
    """Schema for nutrient entity responses."""
    nutrient_type: Optional[str] = None
    function: Optional[str] = None
    source: Optional[str] = None


class CompoundEntityResponse(EntityResponse):
    """Schema for compound entity responses."""
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[str] = None
    cas_number: Optional[str] = None


class EntitySearchRequest(BaseModel):
    """Schema for entity search requests."""
    query: Optional[str] = Field(None, description="Text search query")
    primary_classification: Optional[str] = Field(None, description="Filter by primary classification")
    classifications: Optional[List[str]] = Field(None, description="Filter by specific classifications")
    health_outcomes: Optional[List[str]] = Field(None, description="Filter by health outcomes")
    compound_ids: Optional[List[str]] = Field(None, description="Filter by compound IDs")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Filter by attribute values")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("name", description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class EntitySearchResponse(BaseModel):
    """Schema for entity search responses."""
    entities: List[EntityResponse]
    total: int
    query: Optional[str] = None
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float


class IngredientGroup(BaseModel):
    """Schema for a group of ingredients within a category."""
    category_id: int
    category_name: str
    category_slug: str
    total: int
    page: int
    size: int
    items: List[IngredientEntityResponse]


class IngredientGroupsResponse(BaseModel):
    """Response schema for grouped ingredients endpoint."""
    groups: List[IngredientGroup]


class EntityStatsResponse(BaseModel):
    """Schema for entity statistics."""
    total_entities: int
    by_classification: Dict[str, int]
    by_primary_classification: Dict[str, int]
    recent_additions: int
    last_updated: Optional[datetime] = None


# Legacy alias for backward compatibility
class HealthOutcomeInfo(HealthOutcomeSchema):
    """Legacy schema name for health outcome information."""
    pass


# Utility functions for schema conversion
def entity_to_response(entity) -> EntityResponse:
    """Convert SQLAlchemy entity to Pydantic response."""
    return EntityResponse(
        id=entity.id,
        name=entity.name,
        primary_classification=entity.primary_classification,
        classifications=entity.classifications or [],
        attributes=entity.attributes or {},
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )


def create_entity_from_schema(entity_data: EntityCreate):
    """Create SQLAlchemy entity from Pydantic schema."""
    from ..models import Entity
    
    # Convert AttributeValue models to plain dicts for JSON storage
    raw_attrs = entity_data.attributes or {}
    attributes_dumped = {
        key: (value.model_dump() if hasattr(value, "model_dump") else value)
        for key, value in raw_attrs.items()
    }
    
    entity = Entity(
        id=entity_data.id,
        name=entity_data.name,
        primary_classification=entity_data.primary_classification,
        classifications=entity_data.classifications,
        attributes=attributes_dumped
    )
    return entity

