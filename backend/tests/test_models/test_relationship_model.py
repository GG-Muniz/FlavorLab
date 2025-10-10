"""
Tests for the RelationshipEntity model.

This module tests the SQLAlchemy RelationshipEntity model functionality including
model creation, context management, and relationship validation.
"""

import pytest
from datetime import datetime

from app.models import RelationshipEntity, Entity


class TestRelationshipEntityModel:
    """Test the RelationshipEntity model."""
    
    def test_relationship_creation(self, db_session, sample_entity):
        """Test basic relationship creation."""
        # Create target entity
        target_entity = Entity(
            id="target_entity",
            name="Target Entity",
            primary_classification="compound"
        )
        db_session.add(target_entity)
        db_session.commit()
        
        relationship = RelationshipEntity(
            source_id="test_entity_1",
            target_id="target_entity",
            relationship_type="contains",
            quantity="1.5",
            unit="g/100g",
            confidence_score=4
        )
        
        db_session.add(relationship)
        db_session.commit()
        db_session.refresh(relationship)
        
        assert relationship.source_id == "test_entity_1"
        assert relationship.target_id == "target_entity"
        assert relationship.relationship_type == "contains"
        assert relationship.quantity == "1.5"
        assert relationship.unit == "g/100g"
        assert relationship.confidence_score == 4
        assert relationship.context == {}
        assert relationship.uncertainty == {}
        assert relationship.created_at is not None
        assert relationship.updated_at is not None
    
    def test_relationship_with_context(self, db_session):
        """Test relationship creation with context."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains",
            context={
                "state": "raw",
                "mechanisms": ["absorption", "metabolism"],
                "params": {"temperature": "room", "ph": 7.0}
            }
        )
        
        db_session.add(relationship)
        db_session.commit()
        db_session.refresh(relationship)
        
        assert relationship.context["state"] == "raw"
        assert relationship.context["mechanisms"] == ["absorption", "metabolism"]
        assert relationship.context["params"]["temperature"] == "room"
        assert relationship.context["params"]["ph"] == 7.0
    
    def test_relationship_with_uncertainty(self, db_session):
        """Test relationship creation with uncertainty data."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains",
            uncertainty={
                "mean": 1.5,
                "sd": 0.2,
                "min": 1.0,
                "max": 2.0
            }
        )
        
        db_session.add(relationship)
        db_session.commit()
        db_session.refresh(relationship)
        
        assert relationship.uncertainty["mean"] == 1.5
        assert relationship.uncertainty["sd"] == 0.2
        assert relationship.uncertainty["min"] == 1.0
        assert relationship.uncertainty["max"] == 2.0
    
    def test_set_context(self, db_session):
        """Test setting relationship context."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        
        relationship.set_context(
            state="cooked",
            mechanisms=["denaturation", "absorption"],
            params={"temperature": 100, "time": "30min"}
        )
        
        assert relationship.context["state"] == "cooked"
        assert relationship.context["mechanisms"] == ["denaturation", "absorption"]
        assert relationship.context["params"]["temperature"] == 100
        assert relationship.context["params"]["time"] == "30min"
    
    def test_set_context_partial(self, db_session):
        """Test setting partial context."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        
        relationship.set_context(state="raw")
        
        assert relationship.context["state"] == "raw"
        assert relationship.context["mechanisms"] == []
        assert relationship.context["params"] == {}
    
    def test_set_uncertainty(self, db_session):
        """Test setting relationship uncertainty."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        
        relationship.set_uncertainty(
            mean=2.0,
            sd=0.3,
            min_val=1.5,
            max_val=2.5
        )
        
        assert relationship.uncertainty["mean"] == 2.0
        assert relationship.uncertainty["sd"] == 0.3
        assert relationship.uncertainty["min"] == 1.5
        assert relationship.uncertainty["max"] == 2.5
    
    def test_set_uncertainty_partial(self, db_session):
        """Test setting partial uncertainty."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        
        relationship.set_uncertainty(mean=1.0, sd=0.1)
        
        assert relationship.uncertainty["mean"] == 1.0
        assert relationship.uncertainty["sd"] == 0.1
        assert relationship.uncertainty["min"] is None
        assert relationship.uncertainty["max"] is None
    
    def test_relationship_type_checking(self, db_session):
        """Test relationship type checking methods."""
        contains_rel = RelationshipEntity(
            source_id="source",
            target_id="target",
            relationship_type="contains"
        )
        
        found_in_rel = RelationshipEntity(
            source_id="source",
            target_id="target",
            relationship_type="found_in"
        )
        
        assert contains_rel.is_contains_relationship() is True
        assert contains_rel.is_found_in_relationship() is False
        
        assert found_in_rel.is_contains_relationship() is False
        assert found_in_rel.is_found_in_relationship() is True
    
    def test_get_quantity_with_unit(self, db_session):
        """Test getting formatted quantity with unit."""
        # With both quantity and unit
        rel1 = RelationshipEntity(
            source_id="source",
            target_id="target",
            relationship_type="contains",
            quantity="1.5",
            unit="g/100g"
        )
        assert rel1.get_quantity_with_unit() == "1.5 g/100g"
        
        # With quantity only
        rel2 = RelationshipEntity(
            source_id="source",
            target_id="target",
            relationship_type="contains",
            quantity="variable"
        )
        assert rel2.get_quantity_with_unit() == "variable"
        
        # With neither
        rel3 = RelationshipEntity(
            source_id="source",
            target_id="target",
            relationship_type="contains"
        )
        assert rel3.get_quantity_with_unit() == "unknown"
    
    def test_to_dict(self, db_session):
        """Test converting relationship to dictionary."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains",
            quantity="1.0",
            unit="g/100g",
            context={"state": "raw"},
            uncertainty={"mean": 1.0},
            source_reference="test_data",
            confidence_score=4
        )
        
        db_session.add(relationship)
        db_session.commit()
        db_session.refresh(relationship)
        
        rel_dict = relationship.to_dict()
        
        assert rel_dict["source_id"] == "source_entity"
        assert rel_dict["target_id"] == "target_entity"
        assert rel_dict["relationship_type"] == "contains"
        assert rel_dict["quantity"] == "1.0"
        assert rel_dict["unit"] == "g/100g"
        assert rel_dict["context"] == {"state": "raw"}
        assert rel_dict["uncertainty"] == {"mean": 1.0}
        assert rel_dict["source_reference"] == "test_data"
        assert rel_dict["confidence_score"] == 4
        assert "created_at" in rel_dict
        assert "updated_at" in rel_dict
    
    def test_relationship_repr(self, db_session):
        """Test relationship string representation."""
        relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        
        repr_str = repr(relationship)
        assert "source_entity" in repr_str
        assert "target_entity" in repr_str
        assert "contains" in repr_str


class TestRelationshipValidation:
    """Test relationship validation and constraints."""
    
    def test_confidence_score_range(self, db_session):
        """Test confidence score validation."""
        # Valid confidence scores
        for score in [1, 2, 3, 4, 5]:
            relationship = RelationshipEntity(
                source_id="source",
                target_id="target",
                relationship_type="contains",
                confidence_score=score
            )
            db_session.add(relationship)
        
        db_session.commit()
        
        # All should be created successfully
        relationships = db_session.query(RelationshipEntity).all()
        assert len(relationships) == 5
    
    def test_relationship_type_validation(self, db_session):
        """Test relationship type validation."""
        valid_types = ["contains", "found_in", "related_to", "inhibits", "enhances"]
        
        for rel_type in valid_types:
            relationship = RelationshipEntity(
                source_id="source",
                target_id="target",
                relationship_type=rel_type
            )
            db_session.add(relationship)
        
        db_session.commit()
        
        # All should be created successfully
        relationships = db_session.query(RelationshipEntity).all()
        assert len(relationships) == len(valid_types)
    
    def test_foreign_key_constraints(self, db_session):
        """Test foreign key constraints."""
        # Create entities
        source_entity = Entity(
            id="source_entity",
            name="Source Entity",
            primary_classification="ingredient"
        )
        target_entity = Entity(
            id="target_entity",
            name="Target Entity",
            primary_classification="compound"
        )
        db_session.add_all([source_entity, target_entity])
        db_session.commit()
        
        # Valid relationship with existing entities
        valid_relationship = RelationshipEntity(
            source_id="source_entity",
            target_id="target_entity",
            relationship_type="contains"
        )
        db_session.add(valid_relationship)
        db_session.commit()
        
        # Should be created successfully
        relationships = db_session.query(RelationshipEntity).all()
        assert len(relationships) == 1


class TestRelationshipQueries:
    """Test relationship querying functionality."""
    
    def test_query_by_relationship_type(self, db_session):
        """Test querying relationships by type."""
        # Create multiple relationships
        relationships_data = [
            ("source1", "target1", "contains"),
            ("source2", "target2", "found_in"),
            ("source3", "target3", "contains"),
            ("source4", "target4", "related_to")
        ]
        
        for source, target, rel_type in relationships_data:
            relationship = RelationshipEntity(
                source_id=source,
                target_id=target,
                relationship_type=rel_type
            )
            db_session.add(relationship)
        
        db_session.commit()
        
        # Query by type
        contains_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.relationship_type == "contains"
        ).all()
        
        assert len(contains_rels) == 2
        
        found_in_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.relationship_type == "found_in"
        ).all()
        
        assert len(found_in_rels) == 1
    
    def test_query_by_confidence_score(self, db_session):
        """Test querying relationships by confidence score."""
        # Create relationships with different confidence scores
        for score in [1, 3, 4, 5]:
            relationship = RelationshipEntity(
                source_id=f"source_{score}",
                target_id=f"target_{score}",
                relationship_type="contains",
                confidence_score=score
            )
            db_session.add(relationship)
        
        db_session.commit()
        
        # Query high confidence relationships
        high_confidence_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.confidence_score >= 4
        ).all()
        
        assert len(high_confidence_rels) == 2
        
        # Query low confidence relationships
        low_confidence_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.confidence_score <= 2
        ).all()
        
        assert len(low_confidence_rels) == 1
    
    def test_query_by_entity_id(self, db_session):
        """Test querying relationships by entity ID."""
        # Create relationships
        relationships_data = [
            ("entity_a", "entity_b", "contains"),
            ("entity_a", "entity_c", "found_in"),
            ("entity_b", "entity_d", "contains"),
            ("entity_c", "entity_e", "related_to")
        ]
        
        for source, target, rel_type in relationships_data:
            relationship = RelationshipEntity(
                source_id=source,
                target_id=target,
                relationship_type=rel_type
            )
            db_session.add(relationship)
        
        db_session.commit()
        
        # Query by source entity
        source_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.source_id == "entity_a"
        ).all()
        
        assert len(source_rels) == 2
        
        # Query by target entity
        target_rels = db_session.query(RelationshipEntity).filter(
            RelationshipEntity.target_id == "entity_b"
        ).all()
        
        assert len(target_rels) == 1
