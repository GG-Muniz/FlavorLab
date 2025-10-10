"""
Tests for the SearchService.

This module tests the search and filtering functionality
for entities and relationships.
"""

import pytest
from app.services.search import SearchService
from app.schemas import EntitySearchRequest, RelationshipSearchRequest
from sqlalchemy.orm import Session


class TestEntitySearch:
    """Test entity search functionality."""
    
    def test_search_entities_basic(self, db_session, multiple_entities):
        """Test basic entity search."""
        search_request = EntitySearchRequest(
            query="turmeric",
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(entities) >= 1
        assert execution_time > 0
        
        # Should find turmeric
        entity_names = [entity.name.lower() for entity in entities]
        assert any("turmeric" in name for name in entity_names)
    
    def test_search_entities_by_classification(self, db_session, multiple_entities):
        """Test entity search by primary classification."""
        search_request = EntitySearchRequest(
            primary_classification="ingredient",
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 2  # Should find turmeric and ginger
        assert len(entities) >= 2
        
        # All results should be ingredients
        for entity in entities:
            assert entity.primary_classification == "ingredient"
    
    def test_search_entities_by_classifications(self, db_session, multiple_entities):
        """Test entity search by specific classifications."""
        search_request = EntitySearchRequest(
            classifications=["spice"],
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 2  # Should find turmeric and ginger
        assert len(entities) >= 2
        
        # All results should have "spice" classification
        for entity in entities:
            assert "spice" in entity.classifications
    
    def test_search_entities_by_health_outcomes(self, db_session, multiple_entities):
        """Test entity search by health outcomes."""
        search_request = EntitySearchRequest(
            health_outcomes=["Anti-inflammatory"],
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 2  # Should find turmeric and ginger
        assert len(entities) >= 2
    
    def test_search_entities_with_pagination(self, db_session, multiple_entities):
        """Test entity search with pagination."""
        search_request = EntitySearchRequest(
            limit=2,
            offset=1
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 3  # Total should be more than limit
        assert len(entities) <= 2  # Should respect limit
        assert execution_time > 0
    
    def test_search_entities_with_sorting(self, db_session, multiple_entities):
        """Test entity search with sorting."""
        search_request = EntitySearchRequest(
            sort_by="name",
            sort_order="asc",
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 3
        assert len(entities) >= 3
        
        # Should be sorted by name ascending
        names = [entity.name for entity in entities]
        assert names == sorted(names)
    
    def test_search_entities_no_results(self, db_session: Session):
        """Test searching for entities with no matching results."""
        service = SearchService(db_session)
        result = service.search_entities("nonexistent")
        assert result["total"] == 0
        assert len(result["data"]) == 0
        assert result["execution_time"] >= 0
    
    def test_search_entities_combined_filters(self, db_session, multiple_entities):
        """Test entity search with multiple filters."""
        search_request = EntitySearchRequest(
            query="turmeric",
            primary_classification="ingredient",
            classifications=["spice"],
            health_outcomes=["Anti-inflammatory"],
            limit=10
        )
        
        entities, total_count, execution_time = SearchService.search_entities(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(entities) >= 1
        
        # Should find turmeric with all filters
        for entity in entities:
            assert entity.primary_classification == "ingredient"
            assert "spice" in entity.classifications


class TestRelationshipSearch:
    """Test relationship search functionality."""
    
    def test_search_relationships_basic(self, db_session, sample_relationship):
        """Test basic relationship search."""
        search_request = RelationshipSearchRequest(
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        assert execution_time > 0
    
    def test_search_relationships_by_type(self, db_session, sample_relationship):
        """Test relationship search by type."""
        search_request = RelationshipSearchRequest(
            relationship_type="contains",
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # All results should be "contains" relationships
        for rel in relationships:
            assert rel.relationship_type == "contains"
    
    def test_search_relationships_by_source_id(self, db_session, sample_relationship):
        """Test relationship search by source ID."""
        search_request = RelationshipSearchRequest(
            source_id="test_entity_1",
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # All results should have the specified source ID
        for rel in relationships:
            assert rel.source_id == "test_entity_1"
    
    def test_search_relationships_by_target_id(self, db_session, sample_relationship):
        """Test relationship search by target ID."""
        search_request = RelationshipSearchRequest(
            target_id="test_entity_2",
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # All results should have the specified target ID
        for rel in relationships:
            assert rel.target_id == "test_entity_2"
    
    def test_search_relationships_by_confidence(self, db_session, sample_relationship):
        """Test relationship search by confidence score."""
        search_request = RelationshipSearchRequest(
            min_confidence=4,
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # All results should have confidence >= 4
        for rel in relationships:
            assert rel.confidence_score >= 4
    
    def test_search_relationships_by_quantity(self, db_session, sample_relationship):
        """Test relationship search by quantity presence."""
        search_request = RelationshipSearchRequest(
            has_quantity=True,
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # All results should have quantity data
        for rel in relationships:
            assert rel.quantity is not None
    
    def test_search_relationships_with_pagination(self, db_session, sample_relationship):
        """Test relationship search with pagination."""
        search_request = RelationshipSearchRequest(
            limit=1,
            offset=0
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) <= 1
        assert execution_time >= 0
    
    def test_search_relationships_with_sorting(self, db_session, sample_relationship):
        """Test relationship search with sorting."""
        search_request = RelationshipSearchRequest(
            sort_by="confidence_score",
            sort_order="desc",
            limit=10
        )
        
        relationships, total_count, execution_time = SearchService.search_relationships(
            db_session, search_request
        )
        
        assert total_count >= 1
        assert len(relationships) >= 1
        
        # Should be sorted by confidence score descending
        scores = [rel.confidence_score for rel in relationships]
        assert scores == sorted(scores, reverse=True)


class TestEntityConnections:
    """Test entity connection functionality."""
    
    def test_get_entity_connections(self, db_session, sample_entity, sample_relationship):
        """Test getting entity connections."""
        connections = SearchService.get_entity_connections(
            db_session, sample_entity.id
        )
        
        assert "entity_id" in connections
        assert "entity_name" in connections
        assert "incoming_relationships" in connections
        assert "outgoing_relationships" in connections
        assert "total_connections" in connections
        assert "relationship_types" in connections
        
        assert connections["entity_id"] == sample_entity.id
        assert connections["entity_name"] == sample_entity.name
        assert connections["total_connections"] >= 1
    
    def test_get_entity_connections_with_type_filter(self, db_session, sample_entity, sample_relationship):
        """Test getting entity connections with type filter."""
        connections = SearchService.get_entity_connections(
            db_session, sample_entity.id, relationship_types=["contains"]
        )
        
        assert connections["total_connections"] >= 1
        
        # All relationships should be "contains" type
        all_relationships = connections["incoming_relationships"] + connections["outgoing_relationships"]
        for rel in all_relationships:
            assert rel.relationship_type == "contains"
    
    def test_get_entity_connections_not_found(self, db_session):
        """Test getting connections for non-existent entity."""
        connections = SearchService.get_entity_connections(
            db_session, "nonexistent_entity"
        )
        
        assert "error" in connections
        assert connections["error"] == "Entity not found"
    
    def test_get_entity_connections_with_depth_limit(self, db_session, sample_entity, sample_relationship):
        """Test getting entity connections with depth limit."""
        connections = SearchService.get_entity_connections(
            db_session, sample_entity.id, max_depth=1
        )
        
        assert "total_connections" in connections
        assert connections["total_connections"] >= 0


class TestRelationshipPathFinding:
    """Test relationship path finding functionality."""
    
    def test_find_relationship_path_direct(self, db_session, sample_entity, sample_relationship):
        """Test finding direct relationship path."""
        path = SearchService.find_relationship_path(
            db_session, "test_entity_1", "test_entity_2"
        )
        
        assert path is not None
        assert len(path) == 1
        assert path[0].source_id == "test_entity_1"
        assert path[0].target_id == "test_entity_2"
    
    def test_find_relationship_path_nonexistent(self, db_session):
        """Test finding path between non-existent entities."""
        path = SearchService.find_relationship_path(
            db_session, "nonexistent_source", "nonexistent_target"
        )
        
        assert path is None
    
    def test_find_relationship_path_no_path(self, db_session, sample_entity):
        """Test finding path when no path exists."""
        # Create isolated entity
        from app.models import Entity
        isolated_entity = Entity(
            id="isolated_entity",
            name="Isolated Entity",
            primary_classification="ingredient"
        )
        db_session.add(isolated_entity)
        db_session.commit()
        
        path = SearchService.find_relationship_path(
            db_session, sample_entity.id, "isolated_entity"
        )
        
        assert path is None
    
    def test_find_relationship_path_with_depth_limit(self, db_session, sample_entity, sample_relationship):
        """Test finding path with depth limit."""
        path = SearchService.find_relationship_path(
            db_session, "test_entity_1", "test_entity_2", max_depth=1
        )
        
        assert path is not None
        assert len(path) <= 1


class TestStatistics:
    """Test statistics functionality."""
    
    def test_get_entity_statistics(self, db_session, multiple_entities):
        """Test getting entity statistics."""
        stats = SearchService.get_entity_statistics(db_session)
        
        assert "total_entities" in stats
        assert "by_classification" in stats
        assert "recent_additions" in stats
        assert "last_updated" in stats
        
        assert stats["total_entities"] >= 3
        assert "ingredient" in stats["by_classification"]
        assert "nutrient" in stats["by_classification"]
    
    def test_get_relationship_statistics(self, db_session, sample_relationship):
        """Test getting relationship statistics."""
        stats = SearchService.get_relationship_statistics(db_session)
        
        assert "total_relationships" in stats
        assert "by_type" in stats
        assert "by_confidence" in stats
        assert "avg_confidence" in stats
        assert "last_updated" in stats
        
        assert stats["total_relationships"] >= 1
        assert "contains" in stats["by_type"]
        assert stats["avg_confidence"] > 0
    
    def test_get_entity_statistics_empty_database(self, db_session):
        """Test getting entity statistics with empty database."""
        stats = SearchService.get_entity_statistics(db_session)
        
        assert stats["total_entities"] == 0
        assert stats["by_classification"] == {}
        assert stats["recent_additions"] == 0
    
    def test_get_relationship_statistics_empty_database(self, db_session):
        """Test getting relationship statistics with empty database."""
        stats = SearchService.get_relationship_statistics(db_session)
        
        assert stats["total_relationships"] == 0
        assert stats["by_type"] == {}
        assert stats["by_confidence"] == {}
        assert stats["avg_confidence"] == 0.0


class TestEntitySuggestions:
    """Test entity suggestion functionality."""
    
    def test_suggest_entities(self, db_session, multiple_entities):
        """Test getting entity suggestions."""
        suggestions = SearchService.suggest_entities(
            db_session, "tur", limit=5
        )
        
        assert len(suggestions) >= 1
        assert len(suggestions) <= 5
        
        # Should find turmeric
        suggestion_names = [s["name"] for s in suggestions]
        assert any("turmeric" in name.lower() for name in suggestion_names)
    
    def test_suggest_entities_with_type_filter(self, db_session, multiple_entities):
        """Test getting entity suggestions with type filter."""
        suggestions = SearchService.suggest_entities(
            db_session, "vit", entity_type="nutrient", limit=5
        )
        
        # All suggestions should be nutrients
        for suggestion in suggestions:
            assert suggestion["type"] == "nutrient"
    
    def test_suggest_entities_no_results(self, db_session):
        """Test getting entity suggestions with no results."""
        suggestions = SearchService.suggest_entities(
            db_session, "nonexistent", limit=5
        )
        
        assert len(suggestions) == 0
    
    def test_suggest_entities_limit(self, db_session, multiple_entities):
        """Test entity suggestions with limit."""
        suggestions = SearchService.suggest_entities(
            db_session, "test", limit=2
        )
        
        assert len(suggestions) <= 2
    
    def test_suggest_entities_relevance_ordering(self, db_session, multiple_entities):
        """Test that entity suggestions are ordered by relevance."""
        suggestions = SearchService.suggest_entities(
            db_session, "turmeric", limit=5
        )
        
        # First suggestion should be exact match
        if suggestions:
            assert "turmeric" in suggestions[0]["name"].lower()
