"""
Search and filtering service for FlavorLab.

This module provides search functionality for entities, relationships,
and other data types with complex filtering capabilities.
"""

import time
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, case, cast, String
from sqlalchemy.sql import text

from ..models import Entity, RelationshipEntity
from ..schemas import (
    EntitySearchRequest, RelationshipSearchRequest,
    FilterCondition, SortCondition, PaginationParams
)


class SearchService:
    """Search service class for complex queries."""

    def __init__(self, db: Session):
        """Optional instance API to support simple usage in tests.

        Storing the provided database session enables calling instance-level
        convenience methods without changing the static/class API used elsewhere.
        """
        self.db = db
        # Provide an instance-level shortcut that shadows the class attribute
        # when accessed from an instance, preserving static API on the class.
        self.search_entities = self._search_entities_instance

    def _search_entities_instance(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Instance wrapper for simple entity search returning a dict.

        This complies with tests expecting `SearchService(db).search_entities("q")`
        to return a mapping with total/data/execution_time.
        """
        from ..schemas import EntitySearchRequest

        request = EntitySearchRequest(query=query, limit=limit, offset=offset)
        entities, total_count, execution_time = SearchService.search_entities(self.db, request)
        return {
            "data": entities,
            "total": total_count,
            "execution_time": execution_time,
        }

    @staticmethod
    def search_entities(
        db: Session,
        search_request: EntitySearchRequest
    ) -> Tuple[List[Entity], int, float]:
        """
        Search entities with complex filtering.
        
        Args:
            db: Database session
            search_request: Search parameters
            
        Returns:
            Tuple of (entities, total_count, execution_time_ms)
        """
        start_time = time.time()
        
        # Build base query
        query = db.query(Entity)
        
        # Apply text search
        if search_request.query:
            query = query.filter(
                or_(
                    Entity.name.ilike(f"%{search_request.query}%"),
                    Entity.id.ilike(f"%{search_request.query}%")
                )
            )
        
        # Apply primary classification filter
        if search_request.primary_classification:
            query = query.filter(Entity.primary_classification == search_request.primary_classification)
        
        # Apply classifications filter
        if search_request.classifications:
            for classification in search_request.classifications:
                query = query.filter(cast(Entity.classifications, String).like(f'%"{classification}"%'))

        # Apply health outcomes filter
        if search_request.health_outcomes:
            for outcome in search_request.health_outcomes:
                query = query.filter(cast(Entity.attributes, String).like(f'%health_outcomes%"{outcome}"%'))

        # Apply compound IDs filter
        if search_request.compound_ids:
            for compound_id in search_request.compound_ids:
                query = query.filter(
                    cast(Entity.attributes, String).like(f'%compounds%"{compound_id}"%')
                )

        # Apply attribute filters
        if search_request.attributes:
            for key, value in search_request.attributes.items():
                query = query.filter(
                    Entity.attributes.contains({
                        key: {
                            "value": value
                        }
                    })
                )
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if search_request.sort_by == "name":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(Entity.name))
            else:
                query = query.order_by(asc(Entity.name))
        elif search_request.sort_by == "created_at":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(Entity.created_at))
            else:
                query = query.order_by(asc(Entity.created_at))
        elif search_request.sort_by == "updated_at":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(Entity.updated_at))
            else:
                query = query.order_by(asc(Entity.updated_at))
        
        # Apply pagination
        query = query.offset(search_request.offset).limit(search_request.limit)
        
        # Execute query
        entities = query.all()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return entities, total_count, execution_time
    
    @staticmethod
    def search_relationships(
        db: Session,
        search_request: RelationshipSearchRequest
    ) -> Tuple[List[RelationshipEntity], int, float]:
        """
        Search relationships with complex filtering.
        
        Args:
            db: Database session
            search_request: Search parameters
            
        Returns:
            Tuple of (relationships, total_count, execution_time_ms)
        """
        start_time = time.time()
        
        # Build base query
        query = db.query(RelationshipEntity)
        
        # Apply source ID filter
        if search_request.source_id:
            query = query.filter(RelationshipEntity.source_id == search_request.source_id)
        
        # Apply target ID filter
        if search_request.target_id:
            query = query.filter(RelationshipEntity.target_id == search_request.target_id)
        
        # Apply relationship type filter
        if search_request.relationship_type:
            query = query.filter(RelationshipEntity.relationship_type == search_request.relationship_type)
        
        # Apply multiple relationship types filter
        if search_request.relationship_types:
            query = query.filter(RelationshipEntity.relationship_type.in_(search_request.relationship_types))
        
        # Apply confidence filters
        if search_request.min_confidence:
            query = query.filter(RelationshipEntity.confidence_score >= search_request.min_confidence)
        
        if search_request.max_confidence:
            query = query.filter(RelationshipEntity.confidence_score <= search_request.max_confidence)
        
        # Apply quantity filter
        if search_request.has_quantity is not None:
            if search_request.has_quantity:
                query = query.filter(RelationshipEntity.quantity.isnot(None))
            else:
                query = query.filter(RelationshipEntity.quantity.is_(None))
        
        # Apply context filters
        if search_request.context_filters:
            for key, value in search_request.context_filters.items():
                query = query.filter(
                    RelationshipEntity.context.contains({key: value})
                )
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if search_request.sort_by == "confidence_score":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(RelationshipEntity.confidence_score))
            else:
                query = query.order_by(asc(RelationshipEntity.confidence_score))
        elif search_request.sort_by == "created_at":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(RelationshipEntity.created_at))
            else:
                query = query.order_by(asc(RelationshipEntity.created_at))
        elif search_request.sort_by == "relationship_type":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(RelationshipEntity.relationship_type))
            else:
                query = query.order_by(asc(RelationshipEntity.relationship_type))
        
        # Apply pagination
        query = query.offset(search_request.offset).limit(search_request.limit)
        
        # Execute query
        relationships = query.all()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return relationships, total_count, execution_time
    
    @staticmethod
    def get_entity_connections(
        db: Session,
        entity_id: str,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get entity connections and relationship paths.
        
        Args:
            db: Database session
            entity_id: Entity ID to analyze
            relationship_types: Filter by relationship types
            max_depth: Maximum relationship depth
            
        Returns:
            Dict with connection information
        """
        # Get entity
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return {"error": "Entity not found"}
        
        # Build relationship query
        rel_query = db.query(RelationshipEntity)
        
        if relationship_types:
            rel_query = rel_query.filter(RelationshipEntity.relationship_type.in_(relationship_types))
        
        # Get incoming relationships
        incoming = rel_query.filter(RelationshipEntity.target_id == entity_id).all()
        
        # Get outgoing relationships
        outgoing = rel_query.filter(RelationshipEntity.source_id == entity_id).all()
        
        # Get unique relationship types
        all_relationships = incoming + outgoing
        relationship_types_found = list(set([rel.relationship_type for rel in all_relationships]))
        
        return {
            "entity_id": entity_id,
            "entity_name": entity.name,
            "incoming_relationships": incoming,
            "outgoing_relationships": outgoing,
            "total_connections": len(all_relationships),
            "relationship_types": relationship_types_found
        }
    
    @staticmethod
    def find_relationship_path(
        db: Session,
        source_id: str,
        target_id: str,
        max_depth: int = 3
    ) -> Optional[List[RelationshipEntity]]:
        """
        Find a relationship path between two entities.
        
        Args:
            db: Database session
            source_id: Source entity ID
            target_id: Target entity ID
            max_depth: Maximum path depth
            
        Returns:
            List of relationships forming the path, or None if no path found
        """
        # Simple BFS implementation for relationship paths
        from collections import deque
        
        queue = deque([(source_id, [])])
        visited = {source_id}
        
        while queue and len(queue[0][1]) < max_depth:
            current_id, path = queue.popleft()
            
            # Get all outgoing relationships from current entity
            relationships = db.query(RelationshipEntity).filter(
                RelationshipEntity.source_id == current_id
            ).all()
            
            for rel in relationships:
                if rel.target_id == target_id:
                    # Found target, return complete path
                    return path + [rel]
                
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append((rel.target_id, path + [rel]))
        
        return None
    
    @staticmethod
    def get_entity_statistics(db: Session) -> Dict[str, Any]:
        """
        Get entity statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict with entity statistics
        """
        # Total entities
        total_entities = db.query(Entity).count()
        
        # Entities by primary classification
        classification_stats = db.query(
            Entity.primary_classification,
            func.count(Entity.id).label('count')
        ).group_by(Entity.primary_classification).all()
        
        by_classification = {stat.primary_classification: stat.count for stat in classification_stats}
        
        # Recent additions (last 30 days)
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        recent_additions = db.query(Entity).filter(
            Entity.created_at >= thirty_days_ago
        ).count()
        
        # Last updated
        last_updated = db.query(func.max(Entity.updated_at)).scalar()
        
        return {
            "total_entities": total_entities,
            "by_classification": by_classification,
            "recent_additions": recent_additions,
            "last_updated": last_updated
        }
    
    @staticmethod
    def get_relationship_statistics(db: Session) -> Dict[str, Any]:
        """
        Get relationship statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict with relationship statistics
        """
        # Total relationships
        total_relationships = db.query(RelationshipEntity).count()
        
        # Relationships by type
        type_stats = db.query(
            RelationshipEntity.relationship_type,
            func.count(RelationshipEntity.id).label('count')
        ).group_by(RelationshipEntity.relationship_type).all()
        
        by_type = {stat.relationship_type: stat.count for stat in type_stats}
        
        # Average confidence
        avg_confidence = db.query(func.avg(RelationshipEntity.confidence_score)).scalar()
        
        # Confidence distribution
        confidence_stats = db.query(
            RelationshipEntity.confidence_score,
            func.count(RelationshipEntity.id).label('count')
        ).group_by(RelationshipEntity.confidence_score).all()
        
        by_confidence = {str(stat.confidence_score): stat.count for stat in confidence_stats}
        
        # Last updated
        last_updated = db.query(func.max(RelationshipEntity.updated_at)).scalar()
        
        return {
            "total_relationships": total_relationships,
            "by_type": by_type,
            "by_confidence": by_confidence,
            "avg_confidence": float(avg_confidence) if avg_confidence else 0.0,
            "last_updated": last_updated
        }
    
    @staticmethod
    def suggest_entities(
        db: Session,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get entity suggestions based on query.
        
        Args:
            db: Database session
            query: Search query
            entity_type: Filter by entity type
            limit: Maximum number of suggestions
            
        Returns:
            List of entity suggestions
        """
        search_query = db.query(Entity)
        
        # Apply entity type filter
        if entity_type:
            search_query = search_query.filter(Entity.primary_classification == entity_type)
        
        # Apply text search
        search_query = search_query.filter(
            or_(
                Entity.name.ilike(f"%{query}%"),
                Entity.id.ilike(f"%{query}%")
            )
        )
        
        # Order by relevance (name matches first)
        search_query = search_query.order_by(
            case(
                (Entity.name.ilike(f"{query}%"), 1),
                (Entity.name.ilike(f"%{query}%"), 2),
                else_=3
            ),
            Entity.name
        )
        
        # Limit results
        entities = search_query.limit(limit).all()
        
        # Format suggestions
        suggestions = []
        for entity in entities:
            suggestions.append({
                "id": entity.id,
                "name": entity.name,
                "type": entity.primary_classification,
                "classifications": entity.classifications or []
            })
        
        return suggestions

