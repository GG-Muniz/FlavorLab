"""
Tests for entity API endpoints.

This module tests entity CRUD operations, search functionality,
and relationship management.
"""

import pytest
from fastapi.testclient import TestClient
from app.config import settings


class TestEntityListing:
    """Test entity listing endpoints."""
    
    def test_list_entities(self, client, multiple_entities):
        """Test listing entities with default parameters."""
        response = client.get("/api/v1/entities/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entities" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        assert data["total"] >= 3  # multiple_entities fixture creates 3 entities
        assert len(data["entities"]) >= 3
        assert data["page"] == 1
        assert data["size"] == 50
    
    def test_list_entities_with_pagination(self, client, multiple_entities):
        """Test entity listing with pagination."""
        response = client.get("/api/v1/entities/?page=1&size=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["entities"]) == 2
        assert data["has_next"] is True
        assert data["has_prev"] is False
    
    def test_list_entities_second_page(self, client, multiple_entities):
        """Test entity listing second page."""
        response = client.get("/api/v1/entities/?page=2&size=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 2
        assert data["size"] == 2
        assert len(data["entities"]) == 1  # Only 1 entity on second page
        assert data["has_next"] is False
        assert data["has_prev"] is True
    
    def test_list_entities_with_classification_filter(self, client, multiple_entities):
        """Test entity listing with classification filter."""
        response = client.get("/api/v1/entities/?classification=ingredient")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return ingredients
        for entity in data["entities"]:
            assert entity["primary_classification"] == "ingredient"
    
    def test_list_entities_with_search(self, client, multiple_entities):
        """Test entity listing with search query."""
        response = client.get("/api/v1/entities/?search=turmeric")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find turmeric entity
        assert data["total"] >= 1
        assert any(entity["name"].lower() == "turmeric" for entity in data["entities"])
    
    def test_list_entities_empty_result(self, client):
        """Test entity listing with no results."""
        response = client.get("/api/v1/entities/?search=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["entities"]) == 0
        assert data["has_next"] is False
        assert data["has_prev"] is False


class TestEntitySearch:
    """Test entity search endpoints."""
    
    def test_search_entities_basic(self, client, multiple_entities):
        """Test basic entity search."""
        search_data = {
            "query": "turmeric",
            "limit": 10
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entities" in data
        assert "total" in data
        assert "query" in data
        assert "filters_applied" in data
        assert "execution_time_ms" in data
        
        assert data["query"] == "turmeric"
        assert data["total"] >= 1
        assert len(data["entities"]) >= 1
    
    def test_search_entities_by_classification(self, client, multiple_entities):
        """Test entity search by classification."""
        search_data = {
            "primary_classification": "ingredient",
            "limit": 10
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # All results should be ingredients
        for entity in data["entities"]:
            assert entity["primary_classification"] == "ingredient"
    
    def test_search_entities_by_health_outcomes(self, client, multiple_entities):
        """Test entity search by health outcomes."""
        search_data = {
            "health_outcomes": ["Anti-inflammatory"],
            "limit": 10
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 1
        assert "Anti-inflammatory" in data["filters_applied"]["health_outcomes"]
    
    def test_search_entities_with_multiple_filters(self, client, multiple_entities):
        """Test entity search with multiple filters."""
        search_data = {
            "query": "turmeric",
            "primary_classification": "ingredient",
            "health_outcomes": ["Anti-inflammatory"],
            "limit": 10
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find turmeric with all filters applied
        assert data["total"] >= 1
        assert data["query"] == "turmeric"
        assert "ingredient" in data["filters_applied"]["primary_classification"]
        assert "Anti-inflammatory" in data["filters_applied"]["health_outcomes"]
    
    def test_search_entities_with_pagination(self, client, multiple_entities):
        """Test entity search with pagination."""
        search_data = {
            "limit": 2,
            "offset": 1
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entities"]) <= 2
        assert data["total"] >= 3  # Should have more than 2 total entities
    
    def test_search_entities_no_results(self, client):
        """Test entity search with no results."""
        search_data = {
            "query": "nonexistent_entity",
            "limit": 10
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["entities"]) == 0


class TestEntityDetails:
    """Test entity detail endpoints."""
    
    def test_get_entity_by_id(self, client, sample_entity):
        """Test getting entity by ID."""
        response = client.get(f"/api/v1/entities/{sample_entity.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == sample_entity.id
        assert data["name"] == sample_entity.name
        assert data["primary_classification"] == sample_entity.primary_classification
        assert data["classifications"] == sample_entity.classifications
        assert data["attributes"] == sample_entity.attributes
    
    def test_get_entity_not_found(self, client):
        """Test getting non-existent entity."""
        response = client.get("/api/v1/entities/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "Entity with ID 'nonexistent' not found" in data["detail"]
    
    def test_get_entity_connections(self, client, sample_entity, sample_relationship):
        """Test getting entity connections."""
        response = client.get(f"/api/v1/entities/{sample_entity.id}/connections")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["entity_id"] == sample_entity.id
        assert data["entity_name"] == sample_entity.name
        assert "incoming_relationships" in data
        assert "outgoing_relationships" in data
        assert "total_connections" in data
        assert "relationship_types" in data
        
        assert data["total_connections"] >= 1
    
    def test_get_entity_connections_not_found(self, client: TestClient):
        """Test getting connections for a non-existent entity."""
        response = client.get(f"{settings.api_prefix}/entities/nonexistent/connections")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_relationship_path(self, client, sample_entity, sample_relationship):
        """Test getting relationship path between entities."""
        response = client.get(f"/api/v1/entities/{sample_entity.id}/path/test_entity_2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["source_id"] == sample_entity.id
        assert data["target_id"] == "test_entity_2"
        assert "path" in data
        assert "path_length" in data
        assert "found" in data
    
    def test_get_relationship_path_not_found(self, client, sample_entity):
        """Test getting relationship path with no path found."""
        response = client.get(f"/api/v1/entities/{sample_entity.id}/path/nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["found"] is False
        assert data["path_length"] == 0
        assert len(data["path"]) == 0


class TestEntityStatistics:
    """Test entity statistics endpoints."""
    
    def test_get_entity_statistics(self, client, multiple_entities):
        """Test getting entity statistics."""
        response = client.get("/api/v1/entities/stats/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_entities" in data
        assert "by_classification" in data
        assert "by_primary_classification" in data
        assert "recent_additions" in data
        assert "last_updated" in data
        
        assert data["total_entities"] >= 3
        assert "ingredient" in data["by_classification"]
        assert "nutrient" in data["by_classification"]
    
    def test_get_entity_suggestions(self, client, multiple_entities):
        """Test getting entity suggestions."""
        response = client.get("/api/v1/entities/suggestions/search?query=tur")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "suggestions" in data
        assert "query" in data
        assert "total_suggestions" in data
        
        assert data["query"] == "tur"
        assert data["total_suggestions"] >= 1
        
        # Should find turmeric
        suggestion_names = [s["name"] for s in data["suggestions"]]
        assert any("turmeric" in name.lower() for name in suggestion_names)
    
    def test_get_entity_suggestions_with_type_filter(self, client, multiple_entities):
        """Test getting entity suggestions with type filter."""
        response = client.get("/api/v1/entities/suggestions/search?query=vit&entity_type=nutrient")
        
        assert response.status_code == 200
        data = response.json()
        
        # All suggestions should be nutrients
        for suggestion in data["suggestions"]:
            assert suggestion["type"] == "nutrient"


class TestEntityCRUD:
    """Test entity CRUD operations (authenticated)."""
    
    def test_create_entity(self, authenticated_client, test_user):
        """Test creating a new entity."""
        entity_data = {
            "id": "new_entity",
            "name": "New Entity",
            "primary_classification": "ingredient",
            "classifications": ["test", "new"],
            "attributes": {
                "description": {
                    "value": "A new test entity",
                    "source": "test",
                    "confidence": 5
                }
            }
        }
        
        response = authenticated_client.post("/api/v1/entities/", json=entity_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "new_entity"
        assert data["name"] == "New Entity"
        assert data["primary_classification"] == "ingredient"
        assert data["classifications"] == ["test", "new"]
        assert data["attributes"]["description"]["value"] == "A new test entity"
    
    def test_create_entity_duplicate_id(self, authenticated_client, test_user, sample_entity):
        """Test creating entity with duplicate ID."""
        entity_data = {
            "id": "test_entity_1",  # Same as sample_entity
            "name": "Duplicate Entity",
            "primary_classification": "ingredient"
        }
        
        response = authenticated_client.post("/api/v1/entities/", json=entity_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Entity with ID 'test_entity_1' already exists" in data["detail"]
    
    def test_create_entity_unauthenticated(self, client):
        """Test creating entity without authentication."""
        entity_data = {
            "id": "unauthorized_entity",
            "name": "Unauthorized Entity",
            "primary_classification": "ingredient"
        }
        
        response = client.post("/api/v1/entities/", json=entity_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_update_entity(self, authenticated_client, test_user, sample_entity):
        """Test updating an entity."""
        update_data = {
            "name": "Updated Entity Name",
            "classifications": ["updated", "modified"]
        }
        
        response = authenticated_client.put(f"/api/v1/entities/{sample_entity.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == sample_entity.id
        assert data["name"] == "Updated Entity Name"
        assert data["classifications"] == ["updated", "modified"]
        assert data["primary_classification"] == sample_entity.primary_classification  # Should not change
    
    def test_update_entity_not_found(self, authenticated_client, test_user):
        """Test updating non-existent entity."""
        update_data = {
            "name": "Updated Name"
        }
        
        response = authenticated_client.put("/api/v1/entities/nonexistent", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "Entity with ID 'nonexistent' not found" in data["detail"]
    
    def test_update_entity_unauthenticated(self, client, sample_entity):
        """Test updating entity without authentication."""
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put(f"/api/v1/entities/{sample_entity.id}", json=update_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_delete_entity(self, authenticated_client, test_user, db_session):
        """Test deleting an entity."""
        # Create entity to delete
        from app.models import Entity
        entity = Entity(
            id="to_delete",
            name="Entity to Delete",
            primary_classification="ingredient"
        )
        db_session.add(entity)
        db_session.commit()
        
        response = authenticated_client.delete("/api/v1/entities/to_delete")
        
        assert response.status_code == 200
        data = response.json()
        assert "Entity 'to_delete' deleted successfully" in data["message"]
        
        # Verify entity is deleted
        deleted_entity = db_session.query(Entity).filter(Entity.id == "to_delete").first()
        assert deleted_entity is None
    
    def test_delete_entity_not_found(self, authenticated_client, test_user):
        """Test deleting non-existent entity."""
        response = authenticated_client.delete("/api/v1/entities/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "Entity with ID 'nonexistent' not found" in data["detail"]
    
    def test_delete_entity_unauthenticated(self, client, sample_entity):
        """Test deleting entity without authentication."""
        response = client.delete(f"/api/v1/entities/{sample_entity.id}")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]


class TestEntityValidation:
    """Test entity validation and error handling."""
    
    def test_create_entity_invalid_data(self, authenticated_client, test_user):
        """Test creating entity with invalid data."""
        entity_data = {
            "id": "invalid_entity",
            "name": "",  # Empty name should be invalid
            "primary_classification": "ingredient"
        }
        
        response = authenticated_client.post("/api/v1/entities/", json=entity_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_update_entity_invalid_data(self, authenticated_client, test_user, sample_entity):
        """Test updating entity with invalid data."""
        update_data = {
            "name": "",  # Empty name should be invalid
            "primary_classification": ""  # Empty classification should be invalid
        }
        
        response = authenticated_client.put(f"/api/v1/entities/{sample_entity.id}", json=update_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_search_entities_invalid_pagination(self, client):
        """Test entity search with invalid pagination."""
        search_data = {
            "limit": -1,  # Invalid limit
            "offset": -1  # Invalid offset
        }
        
        response = client.post("/api/v1/entities/search", json=search_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_list_entities_invalid_pagination(self, client):
        """Test entity listing with invalid pagination."""
        response = client.get("/api/v1/entities/?page=0&size=0")
        
        assert response.status_code == 422  # Validation error
