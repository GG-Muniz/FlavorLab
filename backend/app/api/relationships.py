"""
Relationship API endpoints for FlavorLab.

This module provides REST API endpoints for relationship operations including
listing, searching, and retrieving relationship information.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import RelationshipEntity, Entity
from ..schemas import (
    RelationshipResponse, RelationshipListResponse, RelationshipSearchRequest,
    RelationshipSearchResponse, RelationshipStatsResponse, RelationshipCreate,
    RelationshipUpdate, EntityConnectionsResponse
)
from ..services.search import SearchService
from ..services.auth import get_current_user, get_current_active_user
from ..models import User

# Create router
router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("/", response_model=RelationshipListResponse)
async def list_relationships(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    source_id: Optional[str] = Query(None, description="Filter by source entity ID"),
    target_id: Optional[str] = Query(None, description="Filter by target entity ID"),
    min_confidence: Optional[int] = Query(None, ge=1, le=5, description="Minimum confidence score"),
    db: Session = Depends(get_db)
):
    """
    List relationships with optional filtering and pagination.
    
    Args:
        page: Page number (1-based)
        size: Page size
        relationship_type: Filter by relationship type
        source_id: Filter by source entity ID
        target_id: Filter by target entity ID
        min_confidence: Minimum confidence score
        db: Database session
        
    Returns:
        RelationshipListResponse: Paginated list of relationships
    """
    try:
        # Build query
        query = db.query(RelationshipEntity)
        
        # Apply filters
        if relationship_type:
            query = query.filter(RelationshipEntity.relationship_type == relationship_type)
        
        if source_id:
            query = query.filter(RelationshipEntity.source_id == source_id)
        
        if target_id:
            query = query.filter(RelationshipEntity.target_id == target_id)
        
        if min_confidence:
            query = query.filter(RelationshipEntity.confidence_score >= min_confidence)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        relationships = query.offset(offset).limit(size).all()
        
        # Convert to response format
        relationship_responses = [RelationshipResponse.from_orm(rel) for rel in relationships]
        
        return RelationshipListResponse(
            relationships=relationship_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing relationships: {str(e)}"
        )


@router.post("/search", response_model=RelationshipSearchResponse)
async def search_relationships(
    search_request: RelationshipSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search relationships with complex filtering criteria.
    
    Args:
        search_request: Search parameters
        db: Database session
        
    Returns:
        RelationshipSearchResponse: Search results with metadata
    """
    try:
        # Use search service
        relationships, total_count, execution_time = SearchService.search_relationships(
            db, search_request
        )
        
        # Convert to response format
        relationship_responses = [RelationshipResponse.from_orm(rel) for rel in relationships]
        
        # Build filters applied dict
        filters_applied = {}
        if search_request.source_id:
            filters_applied["source_id"] = search_request.source_id
        if search_request.target_id:
            filters_applied["target_id"] = search_request.target_id
        if search_request.relationship_type:
            filters_applied["relationship_type"] = search_request.relationship_type
        if search_request.relationship_types:
            filters_applied["relationship_types"] = search_request.relationship_types
        if search_request.min_confidence:
            filters_applied["min_confidence"] = search_request.min_confidence
        if search_request.max_confidence:
            filters_applied["max_confidence"] = search_request.max_confidence
        if search_request.has_quantity is not None:
            filters_applied["has_quantity"] = search_request.has_quantity
        if search_request.context_filters:
            filters_applied["context_filters"] = search_request.context_filters
        
        return RelationshipSearchResponse(
            relationships=relationship_responses,
            total=total_count,
            query=None,  # Relationships don't have text search yet
            filters_applied=filters_applied,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching relationships: {str(e)}"
        )


@router.get("/{relationship_id}", response_model=RelationshipResponse)
async def get_relationship(
    relationship_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific relationship by ID.
    
    Args:
        relationship_id: Relationship ID
        db: Database session
        
    Returns:
        RelationshipResponse: Relationship information
        
    Raises:
        HTTPException: If relationship not found
    """
    try:
        relationship = db.query(RelationshipEntity).filter(
            RelationshipEntity.id == relationship_id
        ).first()
        
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relationship with ID '{relationship_id}' not found"
            )
        
        return RelationshipResponse.from_orm(relationship)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving relationship: {str(e)}"
        )


@router.get("/entity/{entity_id}/connections")
async def get_entity_relationships(
    entity_id: str,
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    direction: str = Query("both", pattern="^(incoming|outgoing|both)$", description="Relationship direction"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum relationships"),
    db: Session = Depends(get_db)
):
    """
    Get all relationships for a specific entity.
    
    Args:
        entity_id: Entity ID
        relationship_types: Filter by relationship types
        direction: Relationship direction (incoming, outgoing, both)
        limit: Maximum number of relationships
        db: Database session
        
    Returns:
        Dict with relationship information
    """
    try:
        # Check if entity exists
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        # Build query
        query = db.query(RelationshipEntity)
        
        # Apply relationship type filter
        if relationship_types:
            query = query.filter(RelationshipEntity.relationship_type.in_(relationship_types))
        
        # Apply direction filter
        if direction == "incoming":
            query = query.filter(RelationshipEntity.target_id == entity_id)
        elif direction == "outgoing":
            query = query.filter(RelationshipEntity.source_id == entity_id)
        else:  # both
            query = query.filter(
                (RelationshipEntity.source_id == entity_id) |
                (RelationshipEntity.target_id == entity_id)
            )
        
        # Apply limit
        relationships = query.limit(limit).all()
        
        # Separate incoming and outgoing
        incoming = [rel for rel in relationships if rel.target_id == entity_id]
        outgoing = [rel for rel in relationships if rel.source_id == entity_id]
        
        return {
            "entity_id": entity_id,
            "entity_name": entity.name,
            "incoming_relationships": [RelationshipResponse.from_orm(rel) for rel in incoming],
            "outgoing_relationships": [RelationshipResponse.from_orm(rel) for rel in outgoing],
            "total_connections": len(relationships),
            "relationship_types": list(set([rel.relationship_type for rel in relationships]))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity relationships: {str(e)}"
        )


@router.get("/stats/overview", response_model=RelationshipStatsResponse)
async def get_relationship_statistics(
    db: Session = Depends(get_db)
):
    """
    Get relationship statistics and overview.
    
    Args:
        db: Database session
        
    Returns:
        RelationshipStatsResponse: Relationship statistics
    """
    try:
        stats = SearchService.get_relationship_statistics(db)
        
        return RelationshipStatsResponse(
            total_relationships=stats["total_relationships"],
            by_type=stats["by_type"],
            by_confidence=stats["by_confidence"],
            avg_confidence=stats["avg_confidence"],
            last_updated=stats["last_updated"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving relationship statistics: {str(e)}"
        )


@router.get("/types/list")
async def get_relationship_types(
    db: Session = Depends(get_db)
):
    """
    Get list of all relationship types in the database.
    
    Args:
        db: Database session
        
    Returns:
        List of relationship types with counts
    """
    try:
        from sqlalchemy import func
        
        # Get relationship types with counts
        type_stats = db.query(
            RelationshipEntity.relationship_type,
            func.count(RelationshipEntity.id).label('count')
        ).group_by(RelationshipEntity.relationship_type).all()
        
        return {
            "relationship_types": [
                {"type": stat.relationship_type, "count": stat.count}
                for stat in type_stats
            ],
            "total_types": len(type_stats)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving relationship types: {str(e)}"
        )


# Protected endpoints (require authentication)
@router.post("/", response_model=RelationshipResponse)
async def create_relationship(
    relationship_data: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new relationship (requires authentication).
    
    Args:
        relationship_data: Relationship creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        RelationshipResponse: Created relationship
    """
    try:
        # Verify source and target entities exist
        source_entity = db.query(Entity).filter(Entity.id == relationship_data.source_id).first()
        if not source_entity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source entity with ID '{relationship_data.source_id}' not found"
            )
        
        target_entity = db.query(Entity).filter(Entity.id == relationship_data.target_id).first()
        if not target_entity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target entity with ID '{relationship_data.target_id}' not found"
            )
        
        # Create relationship
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
        
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        
        return RelationshipResponse.from_orm(relationship)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating relationship: {str(e)}"
        )


@router.put("/{relationship_id}", response_model=RelationshipResponse)
async def update_relationship(
    relationship_id: int,
    relationship_data: RelationshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing relationship (requires authentication).
    
    Args:
        relationship_id: Relationship ID
        relationship_data: Relationship update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        RelationshipResponse: Updated relationship
    """
    try:
        relationship = db.query(RelationshipEntity).filter(
            RelationshipEntity.id == relationship_id
        ).first()
        
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relationship with ID '{relationship_id}' not found"
            )
        
        # Update fields
        if relationship_data.relationship_type is not None:
            relationship.relationship_type = relationship_data.relationship_type
        if relationship_data.quantity is not None:
            relationship.quantity = relationship_data.quantity
        if relationship_data.unit is not None:
            relationship.unit = relationship_data.unit
        if relationship_data.context is not None:
            relationship.context = relationship_data.context
        if relationship_data.uncertainty is not None:
            relationship.uncertainty = relationship_data.uncertainty
        if relationship_data.source_reference is not None:
            relationship.source_reference = relationship_data.source_reference
        if relationship_data.confidence_score is not None:
            relationship.confidence_score = relationship_data.confidence_score
        
        db.commit()
        db.refresh(relationship)
        
        return RelationshipResponse.from_orm(relationship)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating relationship: {str(e)}"
        )


@router.delete("/{relationship_id}")
async def delete_relationship(
    relationship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a relationship (requires authentication).
    
    Args:
        relationship_id: Relationship ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with deletion confirmation
    """
    try:
        relationship = db.query(RelationshipEntity).filter(
            RelationshipEntity.id == relationship_id
        ).first()
        
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relationship with ID '{relationship_id}' not found"
            )
        
        db.delete(relationship)
        db.commit()
        
        return {
            "message": f"Relationship '{relationship_id}' deleted successfully",
            "deleted_at": "now"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting relationship: {str(e)}"
        )

