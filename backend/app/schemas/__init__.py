"""
FlavorLab schemas package.

This package contains all Pydantic schemas for the FlavorLab application.
"""

from .entity import (
    EntityBase, EntityCreate, EntityUpdate, EntityResponse,
    EntityListResponse, EntitySearchRequest, EntitySearchResponse,
    EntityStatsResponse, IngredientEntityResponse, NutrientEntityResponse,
    CompoundEntityResponse, HealthOutcomeInfo, CompoundInfo
)

from .relationship import (
    RelationshipBase, RelationshipCreate, RelationshipUpdate, RelationshipResponse,
    RelationshipListResponse, RelationshipSearchRequest, RelationshipSearchResponse,
    RelationshipStatsResponse, EntityConnectionsResponse, RelationshipPathResponse,
    ContextInfo, UncertaintyInfo
)

from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserProfileResponse,
    UserLogin, UserLoginResponse, Token, TokenData, ChangePasswordRequest, PasswordReset,
    PasswordResetConfirm, UserPreferences, UserStatsResponse
)

from .query import (
    FilterCondition, SortCondition, PaginationParams, BaseQueryRequest,
    EntityQueryRequest, RelationshipQueryRequest, HealthOutcomeQueryRequest,
    FlavorQueryRequest, RecommendationRequest, SearchSuggestionRequest,
    QueryResponse, EntityQueryResponse, RelationshipQueryResponse,
    SearchSuggestionResponse, RecommendationResponse, QueryStatsResponse
)

__all__ = [
    # Entity schemas
    "EntityBase", "EntityCreate", "EntityUpdate", "EntityResponse",
    "EntityListResponse", "EntitySearchRequest", "EntitySearchResponse",
    "EntityStatsResponse", "IngredientEntityResponse", "NutrientEntityResponse",
    "CompoundEntityResponse", "HealthOutcomeInfo", "CompoundInfo",
    
    # Relationship schemas
    "RelationshipBase", "RelationshipCreate", "RelationshipUpdate", "RelationshipResponse",
    "RelationshipListResponse", "RelationshipSearchRequest", "RelationshipSearchResponse",
    "RelationshipStatsResponse", "EntityConnectionsResponse", "RelationshipPathResponse",
    "ContextInfo", "UncertaintyInfo",
    
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserProfileResponse",
    "UserLogin", "UserLoginResponse", "Token", "TokenData", "ChangePasswordRequest", "PasswordReset",
    "PasswordResetConfirm", "UserPreferences", "UserStatsResponse",
    
    # Query schemas
    "FilterCondition", "SortCondition", "PaginationParams", "BaseQueryRequest",
    "EntityQueryRequest", "RelationshipQueryRequest", "HealthOutcomeQueryRequest",
    "FlavorQueryRequest", "RecommendationRequest", "SearchSuggestionRequest",
    "QueryResponse", "EntityQueryResponse", "RelationshipQueryResponse",
    "SearchSuggestionResponse", "RecommendationResponse", "QueryStatsResponse"
]

