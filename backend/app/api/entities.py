"""
Entity API endpoints for FlavorLab.

This module provides REST API endpoints for entity operations including
listing, searching, and retrieving entity information.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Entity
from ..models.entity import IngredientEntity
from ..schemas import (
    EntityResponse, EntityListResponse, EntitySearchRequest, EntitySearchResponse,
    EntityStatsResponse, EntityCreate, EntityUpdate, IngredientEntityResponse
)
from ..services.search import SearchService
from ..services.auth import get_current_user, get_current_active_user
from ..models import User

# Create router
router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/", response_model=EntityListResponse)
async def list_entities(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    classification: Optional[str] = Query(None, description="Filter by primary classification"),
    search: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    List entities with optional filtering and pagination.
    
    Args:
        page: Page number (1-based)
        size: Page size
        classification: Filter by primary classification
        search: Search query
        db: Database session
        
    Returns:
        EntityListResponse: Paginated list of entities
    """
    try:
        # Build query
        query = db.query(Entity)
        
        # Apply classification filter
        if classification:
            query = query.filter(Entity.primary_classification == classification)
        
        # Apply search filter
        if search:
            query = query.filter(
                Entity.name.ilike(f"%{search}%")
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        # Convert to response format
        entity_responses = [EntityResponse.model_validate(entity) for entity in entities]
        
        return EntityListResponse(
            entities=entity_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing entities: {str(e)}"
        )


@router.get("/ingredients", response_model=List[IngredientEntityResponse])
async def list_ingredients(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    health_pillars: Optional[str] = Query(
        None,
        description="Comma-separated list of health pillar IDs to filter by (e.g., '1,3,8')"
    ),
    db: Session = Depends(get_db)
):
    """
    List ingredients with optional filtering by health pillars and pagination.

    Args:
        page: Page number (1-based)
        size: Page size
        search: Search query for ingredient names
        health_pillars: Comma-separated health pillar IDs (1-8) to filter by
        db: Database session

    Returns:
        List[IngredientEntityResponse]: List of ingredients with health outcomes

    Example:
        GET /entities/ingredients?health_pillars=1,3,8
        Returns ingredients supporting Energy, Immunity, and Inflammation Reduction
    """
    try:
        # Start with base query for ingredients
        query = db.query(IngredientEntity)

        # Apply search filter
        if search:
            query = query.filter(IngredientEntity.name.ilike(f"%{search}%"))

        # Parse and apply health pillar filter
        pillar_ids: Optional[List[int]] = None
        if health_pillars:
            try:
                # Parse comma-separated string into list of integers
                pillar_ids = [int(pid.strip()) for pid in health_pillars.split(",") if pid.strip()]

                # Validate pillar IDs are in range 1-8
                invalid_ids = [pid for pid in pillar_ids if pid < 1 or pid > 8]
                if invalid_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid health pillar IDs: {invalid_ids}. Must be between 1-8."
                    )

                # Apply pillar filter using the model's class method
                query = IngredientEntity.filter_ingredients_by_pillars(query, pillar_ids)

            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid health_pillars format. Expected comma-separated integers (e.g., '1,3,8'): {str(e)}"
                )

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * size
        ingredients = query.offset(offset).limit(size).all()

        # Additional filtering in Python for SQLite (checking pillar membership)
        # This is needed because SQLite JSON querying is limited
        if pillar_ids:
            filtered_ingredients = []
            for ingredient in ingredients:
                if isinstance(ingredient.health_outcomes, list):
                    # Check if any outcome has a matching pillar
                    for outcome in ingredient.health_outcomes:
                        if isinstance(outcome, dict) and "pillars" in outcome:
                            if any(pid in outcome["pillars"] for pid in pillar_ids):
                                filtered_ingredients.append(ingredient)
                                break
            ingredients = filtered_ingredients

        # Convert to response format
        ingredient_responses = [
            IngredientEntityResponse.model_validate(ingredient)
            for ingredient in ingredients
        ]

        return ingredient_responses

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing ingredients: {str(e)}"
        )


@router.get("/ingredients/{ingredient_id}", response_model=IngredientEntityResponse)
async def get_ingredient_by_id(
    ingredient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single ingredient by its ID.

    This endpoint retrieves detailed information about a specific ingredient,
    including its health outcomes with pillar mappings and compound information.

    **Authentication required** - users must be logged in to view ingredient details.

    Args:
        ingredient_id: Unique identifier for the ingredient
        db: Database session
        current_user: Currently authenticated user

    Returns:
        IngredientEntityResponse: Detailed ingredient information

    Raises:
        HTTPException 404: If ingredient with given ID is not found
        HTTPException 500: If database error occurs

    Example:
        GET /api/v1/entities/ingredients/garlic

        Response:
        ```json
        {
            "id": "garlic",
            "name": "Garlic",
            "primary_classification": "ingredient",
            "health_outcomes": [
                {
                    "outcome": "Garlic",
                    "confidence": 2,
                    "added_at": "2025-10-13T15:43:02.734596+00:00",
                    "pillars": [3, 6, 8]
                }
            ],
            ...
        }
        ```
    """
    try:
        # Query for the specific ingredient
        ingredient = db.query(IngredientEntity).filter(
            IngredientEntity.id == ingredient_id
        ).first()

        # Check if ingredient exists
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with ID '{ingredient_id}' not found"
            )

        # Validate and return the ingredient
        return IngredientEntityResponse.model_validate(ingredient)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving ingredient: {str(e)}"
        )


@router.post("/search", response_model=EntitySearchResponse)
async def search_entities(
    search_request: EntitySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search entities with complex filtering criteria.
    
    Args:
        search_request: Search parameters
        db: Database session
        
    Returns:
        EntitySearchResponse: Search results with metadata
    """
    try:
        # Use search service
        entities, total_count, execution_time = SearchService.search_entities(
            db, search_request
        )
        
        # Convert to response format
        entity_responses = [EntityResponse.model_validate(entity) for entity in entities]
        
        # Build filters applied dict
        filters_applied = {}
        if search_request.primary_classification:
            filters_applied["primary_classification"] = search_request.primary_classification
        if search_request.classifications:
            filters_applied["classifications"] = search_request.classifications
        if search_request.health_outcomes:
            filters_applied["health_outcomes"] = search_request.health_outcomes
        if search_request.compound_ids:
            filters_applied["compound_ids"] = search_request.compound_ids
        if search_request.attributes:
            filters_applied["attributes"] = search_request.attributes
        
        return EntitySearchResponse(
            entities=entity_responses,
            total=total_count,
            query=search_request.query,
            filters_applied=filters_applied,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching entities: {str(e)}"
        )


@router.post("/simple-search")
async def simple_ingredient_search(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Lightweight ingredient name search for autocomplete.

    Accepts {"name_contains": "app"} and returns [{"id":"apple","name":"Apple"}, ...].
    Case-insensitive, limited to ingredients only. Returns at most 15 results.
    """
    try:
        term = (payload or {}).get("name_contains", "")
        term = (term or "").strip()
        if not term:
            return {"results": []}

        query = (
            db.query(IngredientEntity.id, IngredientEntity.name)
            .filter(IngredientEntity.name.ilike(f"%{term}%"))
        ).limit(15)

        results = [{"id": row[0], "name": row[1]} for row in query.all()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching ingredients: {str(e)}"
        )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific entity by ID.
    
    Args:
        entity_id: Entity ID
        db: Database session
        
    Returns:
        EntityResponse: Entity information
        
    Raises:
        HTTPException: If entity not found
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity: {str(e)}"
        )


@router.get("/{entity_id}/connections")
async def get_entity_connections(
    entity_id: str,
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    max_depth: int = Query(2, ge=1, le=5, description="Maximum relationship depth"),
    db: Session = Depends(get_db)
):
    """
    Get entity connections and relationships.
    
    Args:
        entity_id: Entity ID
        relationship_types: Filter by relationship types
        max_depth: Maximum relationship depth
        db: Database session
        
    Returns:
        Dict with connection information
    """
    try:
        connections = SearchService.get_entity_connections(
            db, entity_id, relationship_types, max_depth
        )
        
        if "error" in connections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=connections["error"]
            )
        
        return connections
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity connections: {str(e)}"
        )


@router.get("/{entity_id}/path/{target_id}")
async def get_relationship_path(
    entity_id: str,
    target_id: str,
    max_depth: int = Query(3, ge=1, le=5, description="Maximum path depth"),
    db: Session = Depends(get_db)
):
    """
    Find relationship path between two entities.
    
    Args:
        entity_id: Source entity ID
        target_id: Target entity ID
        max_depth: Maximum path depth
        db: Database session
        
    Returns:
        Dict with path information
    """
    try:
        path = SearchService.find_relationship_path(db, entity_id, target_id, max_depth)
        
        if path is None:
            return {
                "source_id": entity_id,
                "target_id": target_id,
                "path": [],
                "path_length": 0,
                "found": False,
                "message": "No relationship path found"
            }
        
        return {
            "source_id": entity_id,
            "target_id": target_id,
            "path": [rel.to_dict() for rel in path],
            "path_length": len(path),
            "found": True,
            "total_confidence": sum(rel.confidence_score for rel in path),
            "avg_confidence": sum(rel.confidence_score for rel in path) / len(path)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding relationship path: {str(e)}"
        )


@router.get("/stats/overview", response_model=EntityStatsResponse)
async def get_entity_statistics(
    db: Session = Depends(get_db)
):
    """
    Get entity statistics and overview.
    
    Args:
        db: Database session
        
    Returns:
        EntityStatsResponse: Entity statistics
    """
    try:
        stats = SearchService.get_entity_statistics(db)
        
        return EntityStatsResponse(
            total_entities=stats["total_entities"],
            by_classification=stats["by_classification"],
            by_primary_classification=stats["by_classification"],  # Same data for now
            recent_additions=stats["recent_additions"],
            last_updated=stats["last_updated"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity statistics: {str(e)}"
        )


@router.get("/suggestions/search")
async def get_entity_suggestions(
    query: str = Query(..., min_length=1, description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get entity suggestions for search autocomplete.
    
    Args:
        query: Search query
        entity_type: Filter by entity type
        limit: Maximum number of suggestions
        db: Database session
        
    Returns:
        List of entity suggestions
    """
    try:
        suggestions = SearchService.suggest_entities(db, query, entity_type, limit)
        
        return {
            "suggestions": suggestions,
            "query": query,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting entity suggestions: {str(e)}"
        )


# Protected endpoints (require authentication)
@router.post("/", response_model=EntityResponse)
async def create_entity(
    entity_data: EntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new entity (requires authentication).
    
    Args:
        entity_data: Entity creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        EntityResponse: Created entity
    """
    try:
        # Check if entity already exists
        existing_entity = db.query(Entity).filter(Entity.id == entity_data.id).first()
        if existing_entity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entity with ID '{entity_data.id}' already exists"
            )
        
        # Create entity (ensure attributes are plain dicts for JSON storage)
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
        
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating entity: {str(e)}"
        )


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    entity_data: EntityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing entity (requires authentication).
    
    Args:
        entity_id: Entity ID
        entity_data: Entity update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        EntityResponse: Updated entity
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        # Update fields
        if entity_data.name is not None:
            entity.name = entity_data.name
        if entity_data.primary_classification is not None:
            entity.primary_classification = entity_data.primary_classification
        if entity_data.classifications is not None:
            entity.classifications = entity_data.classifications
        if entity_data.attributes is not None:
            raw_attrs = entity_data.attributes or {}
            entity.attributes = {
                key: (value.model_dump() if hasattr(value, "model_dump") else value)
                for key, value in raw_attrs.items()
            }
        
        db.commit()
        db.refresh(entity)
        
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating entity: {str(e)}"
        )


@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an entity (requires authentication).
    
    Args:
        entity_id: Entity ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with deletion confirmation
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        db.delete(entity)
        db.commit()
        
        return {
            "message": f"Entity '{entity_id}' deleted successfully",
            "deleted_at": "now"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting entity: {str(e)}"
        )

