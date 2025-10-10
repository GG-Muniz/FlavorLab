"""
Pydantic schemas for FlavorLab query operations.

This module defines schemas for complex search queries and filtering operations.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class FilterCondition(BaseModel):
    """Schema for individual filter conditions."""
    field: str = Field(..., description="Field to filter on")
    operator: str = Field(..., description="Filter operator (eq, ne, gt, gte, lt, lte, in, contains, starts_with, ends_with)")
    value: Any = Field(..., description="Filter value")
    
    @field_validator('operator')
    def validate_operator(cls, v):
        """Validate filter operator."""
        valid_operators = ['eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'contains', 'starts_with', 'ends_with']
        if v not in valid_operators:
            raise ValueError(f'Operator must be one of: {", ".join(valid_operators)}')
        return v


class SortCondition(BaseModel):
    """Schema for sort conditions."""
    field: str = Field(..., description="Field to sort by")
    order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(50, ge=1, le=1000, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and size."""
        return (self.page - 1) * self.size


class BaseQueryRequest(BaseModel):
    """Base schema for query requests."""
    filters: List[FilterCondition] = Field(default_factory=list)
    sort: List[SortCondition] = Field(default_factory=list)
    pagination: PaginationParams = Field(default_factory=PaginationParams)
    include_total: bool = Field(True, description="Include total count in response")


class EntityQueryRequest(BaseQueryRequest):
    """Schema for entity query requests."""
    search_text: Optional[str] = Field(None, description="Full-text search query")
    primary_classification: Optional[str] = Field(None, description="Filter by primary classification")
    classifications: Optional[List[str]] = Field(None, description="Filter by classifications")
    health_outcomes: Optional[List[str]] = Field(None, description="Filter by health outcomes")
    compound_ids: Optional[List[str]] = Field(None, description="Filter by compound IDs")
    attribute_filters: Optional[Dict[str, Any]] = Field(None, description="Filter by attribute values")


class RelationshipQueryRequest(BaseQueryRequest):
    """Schema for relationship query requests."""
    source_id: Optional[str] = Field(None, description="Filter by source entity ID")
    target_id: Optional[str] = Field(None, description="Filter by target entity ID")
    relationship_type: Optional[str] = Field(None, description="Filter by relationship type")
    relationship_types: Optional[List[str]] = Field(None, description="Filter by multiple relationship types")
    min_confidence: Optional[int] = Field(None, ge=1, le=5, description="Minimum confidence score")
    max_confidence: Optional[int] = Field(None, ge=1, le=5, description="Maximum confidence score")
    has_quantity: Optional[bool] = Field(None, description="Filter by presence of quantity data")
    context_filters: Optional[Dict[str, Any]] = Field(None, description="Filter by context values")


class HealthOutcomeQueryRequest(BaseQueryRequest):
    """Schema for health outcome query requests."""
    search_text: Optional[str] = Field(None, description="Search in health outcome names")
    categories: Optional[List[str]] = Field(None, description="Filter by health outcome categories")
    severity_levels: Optional[List[str]] = Field(None, description="Filter by severity levels")
    evidence_strength: Optional[List[str]] = Field(None, description="Filter by evidence strength")


class FlavorQueryRequest(BaseQueryRequest):
    """Schema for flavor query requests."""
    search_text: Optional[str] = Field(None, description="Search in flavor names")
    flavor_categories: Optional[List[str]] = Field(None, description="Filter by flavor categories")
    intensity_levels: Optional[List[str]] = Field(None, description="Filter by intensity levels")
    complementary_flavors: Optional[List[str]] = Field(None, description="Filter by complementary flavors")


class RecommendationRequest(BaseModel):
    """Schema for recommendation requests."""
    user_id: Optional[int] = Field(None, description="User ID for personalized recommendations")
    health_goals: Optional[List[str]] = Field(None, description="Health goals to consider")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    flavor_preferences: Optional[Dict[str, Any]] = Field(None, description="Flavor preferences")
    ingredient_preferences: Optional[List[str]] = Field(None, description="Preferred ingredients")
    max_recommendations: int = Field(10, ge=1, le=50, description="Maximum number of recommendations")
    min_confidence: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")


class SearchSuggestionRequest(BaseModel):
    """Schema for search suggestion requests."""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    entity_type: Optional[str] = Field(None, description="Limit suggestions to specific entity type")
    max_suggestions: int = Field(10, ge=1, le=20, description="Maximum number of suggestions")


class QueryResponse(BaseModel):
    """Base schema for query responses."""
    results: List[Dict[str, Any]]
    total: Optional[int] = None
    page: int
    size: int
    has_next: bool
    has_prev: bool
    execution_time_ms: float
    query_info: Dict[str, Any] = Field(default_factory=dict)


class EntityQueryResponse(QueryResponse):
    """Schema for entity query responses."""
    results: List[Dict[str, Any]]  # Will be EntityResponse objects
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class RelationshipQueryResponse(QueryResponse):
    """Schema for relationship query responses."""
    results: List[Dict[str, Any]]  # Will be RelationshipResponse objects
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class SearchSuggestionResponse(BaseModel):
    """Schema for search suggestion responses."""
    suggestions: List[Dict[str, Any]]
    query: str
    total_suggestions: int


class RecommendationResponse(BaseModel):
    """Schema for recommendation responses."""
    recommendations: List[Dict[str, Any]]
    user_id: Optional[int] = None
    criteria_used: Dict[str, Any] = Field(default_factory=dict)
    confidence_scores: List[float] = Field(default_factory=list)
    total_recommendations: int


class QueryStatsResponse(BaseModel):
    """Schema for query statistics."""
    total_queries: int
    avg_execution_time_ms: float
    most_common_filters: Dict[str, int]
    query_types: Dict[str, int]
    last_updated: Optional[datetime] = None


# Utility functions for query processing
def build_filter_conditions(filters: List[FilterCondition]) -> Dict[str, Any]:
    """Convert filter conditions to database query format."""
    conditions = {}
    for filter_cond in filters:
        field = filter_cond.field
        operator = filter_cond.operator
        value = filter_cond.value
        
        if operator == 'eq':
            conditions[field] = value
        elif operator == 'ne':
            conditions[f"{field}__ne"] = value
        elif operator == 'gt':
            conditions[f"{field}__gt"] = value
        elif operator == 'gte':
            conditions[f"{field}__gte"] = value
        elif operator == 'lt':
            conditions[f"{field}__lt"] = value
        elif operator == 'lte':
            conditions[f"{field}__lte"] = value
        elif operator == 'in':
            conditions[f"{field}__in"] = value
        elif operator == 'contains':
            conditions[f"{field}__contains"] = value
        elif operator == 'starts_with':
            conditions[f"{field}__startswith"] = value
        elif operator == 'ends_with':
            conditions[f"{field}__endswith"] = value
    
    return conditions


def validate_query_params(query_request: BaseQueryRequest) -> bool:
    """Validate query parameters."""
    # Check for conflicting filters
    if query_request.pagination.size > 1000:
        raise ValueError("Page size cannot exceed 1000")
    
    # Validate sort fields
    valid_sort_fields = ['name', 'created_at', 'updated_at', 'id']
    for sort_cond in query_request.sort:
        if sort_cond.field not in valid_sort_fields:
            raise ValueError(f"Invalid sort field: {sort_cond.field}")
    
    return True

