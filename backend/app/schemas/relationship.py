"""
Pydantic schemas for FlavorLab relationships.

This module defines the request/response schemas for relationship-related API endpoints.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class RelationshipBase(BaseModel):
    """Base schema for relationship operations."""
    source_id: str = Field(..., min_length=1, max_length=255)
    target_id: str = Field(..., min_length=1, max_length=255)
    relationship_type: str = Field(..., min_length=1, max_length=100)
    quantity: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    context: Dict[str, Any] = Field(default_factory=dict)
    uncertainty: Dict[str, Any] = Field(default_factory=dict)
    source_reference: Optional[str] = None
    confidence_score: int = Field(3, ge=1, le=5)


class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship."""
    pass


class RelationshipUpdate(BaseModel):
    """Schema for updating an existing relationship."""
    relationship_type: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    context: Optional[Dict[str, Any]] = None
    uncertainty: Optional[Dict[str, Any]] = None
    source_reference: Optional[str] = None
    confidence_score: Optional[int] = Field(None, ge=1, le=5)


class RelationshipResponse(RelationshipBase):
    """Schema for relationship responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RelationshipWithEntities(RelationshipResponse):
    """Schema for relationship responses with entity details."""
    source_entity: Optional[Dict[str, Any]] = None
    target_entity: Optional[Dict[str, Any]] = None


class RelationshipListResponse(BaseModel):
    """Schema for paginated relationship list responses."""
    relationships: List[RelationshipResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class RelationshipSearchRequest(BaseModel):
    """Schema for relationship search requests."""
    source_id: Optional[str] = Field(None, description="Filter by source entity ID")
    target_id: Optional[str] = Field(None, description="Filter by target entity ID")
    relationship_type: Optional[str] = Field(None, description="Filter by relationship type")
    relationship_types: Optional[List[str]] = Field(None, description="Filter by multiple relationship types")
    min_confidence: Optional[int] = Field(None, ge=1, le=5, description="Minimum confidence score")
    max_confidence: Optional[int] = Field(None, ge=1, le=5, description="Maximum confidence score")
    has_quantity: Optional[bool] = Field(None, description="Filter by presence of quantity data")
    context_filters: Optional[Dict[str, Any]] = Field(None, description="Filter by context values")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("confidence_score", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class RelationshipSearchResponse(BaseModel):
    """Schema for relationship search responses."""
    relationships: List[RelationshipResponse]
    total: int
    query: Optional[str] = None
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float


class RelationshipStatsResponse(BaseModel):
    """Schema for relationship statistics."""
    total_relationships: int
    by_type: Dict[str, int]
    by_confidence: Dict[str, int]
    avg_confidence: float
    last_updated: Optional[datetime] = None


class EntityConnectionsResponse(BaseModel):
    """Schema for entity connection analysis."""
    entity_id: str
    entity_name: str
    incoming_relationships: List[RelationshipResponse]
    outgoing_relationships: List[RelationshipResponse]
    total_connections: int
    relationship_types: List[str]


class RelationshipPathResponse(BaseModel):
    """Schema for relationship path analysis."""
    source_id: str
    target_id: str
    path: List[RelationshipResponse]
    path_length: int
    total_confidence: float
    avg_confidence: float


class ContextInfo(BaseModel):
    """Schema for relationship context information."""
    state: Optional[str] = None
    mechanisms: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)


class UncertaintyInfo(BaseModel):
    """Schema for relationship uncertainty information."""
    mean: Optional[float] = None
    sd: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None


# Utility functions for schema conversion
def relationship_to_response(relationship) -> RelationshipResponse:
    """Convert SQLAlchemy relationship to Pydantic response."""
    return RelationshipResponse(
        id=relationship.id,
        source_id=relationship.source_id,
        target_id=relationship.target_id,
        relationship_type=relationship.relationship_type,
        quantity=relationship.quantity,
        unit=relationship.unit,
        context=relationship.context or {},
        uncertainty=relationship.uncertainty or {},
        source_reference=relationship.source_reference,
        confidence_score=relationship.confidence_score,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at
    )


def create_relationship_from_schema(relationship_data: RelationshipCreate):
    """Create SQLAlchemy relationship from Pydantic schema."""
    from ..models import RelationshipEntity
    
    relationship = RelationshipEntity(
        source_id=relationship_data.source_id,
        target_id=relationship_data.target_id,
        relationship_type=relationship_data.relationship_type,
        quantity=relationship_data.quantity,
        unit=relationship_data.unit,
        context=relationship_data.context,
        uncertainty=relationship_data.uncertainty,
        source_reference=relationship_data.source_reference,
        confidence_score=relationship_data.confidence_score
    )
    return relationship
