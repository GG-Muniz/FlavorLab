"""
Tests for the Entity model.

This module tests the SQLAlchemy Entity model functionality including
model creation, attribute management, and relationship handling.
"""

import pytest
from sqlalchemy.orm import Session
from app.models import Entity, IngredientEntity, NutrientEntity, CompoundEntity, RelationshipEntity
from datetime import datetime


class TestEntityModel:
    """Test the base Entity model."""
    
    def test_entity_creation(self, db_session):
        """Test basic entity creation."""
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient"
        )
        
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)
        
        assert entity.id == "test_entity"
        assert entity.name == "Test Entity"
        assert entity.primary_classification == "ingredient"
        assert entity.classifications == []
        assert entity.attributes == {}
        assert entity.created_at is not None
        assert entity.updated_at is not None
    
    def test_entity_with_classifications(self, db_session):
        """Test entity creation with classifications."""
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient",
            classifications=["spice", "anti-inflammatory"]
        )
        
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)
        
        assert entity.classifications == ["spice", "anti-inflammatory"]
    
    def test_entity_with_attributes(self, db_session):
        """Test entity creation with attributes."""
        attributes = {
            "description": {
                "value": "A test ingredient",
                "source": "test",
                "confidence": 5
            },
            "health_outcomes": {
                "value": ["Energy", "Anti-inflammatory"],
                "source": "research",
                "confidence": 4
            }
        }
        
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient",
            attributes=attributes
        )
        
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)
        
        assert entity.attributes == attributes
        assert entity.get_attribute("description") == "A test ingredient"
        assert entity.get_attribute("health_outcomes") == ["Energy", "Anti-inflammatory"]
        assert entity.get_attribute("nonexistent") is None
    
    def test_add_classification(self, db_session):
        """Test adding classifications to entity."""
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient"
        )
        
        entity.add_classification("spice")
        entity.add_classification("anti-inflammatory")
        entity.add_classification("spice")  # Duplicate should not be added
        
        assert entity.classifications == ["spice", "anti-inflammatory"]
    
    def test_add_attribute(self, db_session):
        """Test adding attributes to entity."""
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient"
        )
        
        entity.add_attribute("description", "A test ingredient", source="test", confidence=5)
        entity.add_attribute("health_outcomes", ["Energy"], source="research", confidence=4)
        
        expected_attributes = {
            "description": {
                "value": "A test ingredient",
                "source": "test",
                "confidence": 5
            },
            "health_outcomes": {
                "value": ["Energy"],
                "source": "research",
                "confidence": 4
            }
        }
        
        assert entity.attributes == expected_attributes
    
    def test_entity_type_checking(self, db_session):
        """Test entity type checking methods."""
        ingredient = Entity(
            id="ingredient_1",
            name="Test Ingredient",
            primary_classification="ingredient"
        )
        
        nutrient = Entity(
            id="nutrient_1",
            name="Test Nutrient",
            primary_classification="nutrient"
        )
        
        compound = Entity(
            id="compound_1",
            name="Test Compound",
            primary_classification="compound"
        )
        
        assert ingredient.is_ingredient() is True
        assert ingredient.is_nutrient() is False
        assert ingredient.is_compound() is False
        
        assert nutrient.is_ingredient() is False
        assert nutrient.is_nutrient() is True
        assert nutrient.is_compound() is False
        
        assert compound.is_ingredient() is False
        assert compound.is_nutrient() is False
        assert compound.is_compound() is True
    
    def test_entity_repr(self, db_session):
        """Test entity string representation."""
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient"
        )
        
        repr_str = repr(entity)
        assert "test_entity" in repr_str
        assert "Test Entity" in repr_str
        assert "ingredient" in repr_str


class TestIngredientEntityModel:
    """Test the IngredientEntity model."""
    
    def test_ingredient_entity_creation(self, db_session):
        """Test ingredient entity creation."""
        ingredient = IngredientEntity(
            id="turmeric",
            name="Turmeric",
            primary_classification="ingredient",
            foodb_priority="Critical"
        )
        
        db_session.add(ingredient)
        db_session.commit()
        db_session.refresh(ingredient)
        
        assert ingredient.id == "turmeric"
        assert ingredient.name == "Turmeric"
        assert ingredient.foodb_priority == "Critical"
        assert ingredient.health_outcomes == []
        assert ingredient.compounds == []
    
    def test_add_health_outcome(self, db_session):
        """Test adding health outcomes to ingredient."""
        ingredient = IngredientEntity(
            id="turmeric",
            name="Turmeric",
            primary_classification="ingredient"
        )
        
        ingredient.add_health_outcome("Anti-inflammatory", confidence=5)
        ingredient.add_health_outcome("Antioxidant", confidence=4)
        ingredient.add_health_outcome("Anti-inflammatory", confidence=3)  # Update existing
        
        assert len(ingredient.health_outcomes) == 2
        
        # Check first outcome
        first_outcome = ingredient.health_outcomes[0]
        assert first_outcome["outcome"] == "Anti-inflammatory"
        assert first_outcome["confidence"] == 3  # Updated confidence
        assert "added_at" in first_outcome
        assert "updated_at" in first_outcome
        
        # Check second outcome
        second_outcome = ingredient.health_outcomes[1]
        assert second_outcome["outcome"] == "Antioxidant"
        assert second_outcome["confidence"] == 4
        assert "added_at" in second_outcome
    
    def test_add_compound(self, db_session):
        """Test adding compounds to ingredient."""
        ingredient = IngredientEntity(
            id="turmeric",
            name="Turmeric",
            primary_classification="ingredient"
        )
        
        ingredient.add_compound("curcumin", quantity="3.0", unit="g/100g")
        ingredient.add_compound("demethoxycurcumin", quantity="0.5", unit="g/100g")
        ingredient.add_compound("curcumin", quantity="3.5", unit="g/100g")  # Update existing
        
        assert len(ingredient.compounds) == 2
        
        # Check first compound
        first_compound = ingredient.compounds[0]
        assert first_compound["compound_id"] == "curcumin"
        assert first_compound["quantity"] == "3.5"  # Updated quantity
        assert first_compound["unit"] == "g/100g"
        assert "added_at" in first_compound
        assert "updated_at" in first_compound
        
        # Check second compound
        second_compound = ingredient.compounds[1]
        assert second_compound["compound_id"] == "demethoxycurcumin"
        assert second_compound["quantity"] == "0.5"
        assert second_compound["unit"] == "g/100g"
        assert "added_at" in second_compound


class TestNutrientEntityModel:
    """Test the NutrientEntity model."""
    
    def test_nutrient_entity_creation(self, db_session):
        """Test nutrient entity creation."""
        nutrient = NutrientEntity(
            id="vitamin_c",
            name="Vitamin C",
            primary_classification="nutrient",
            nutrient_type="vitamin",
            function="Immune system support",
            source="USDA"
        )
        
        db_session.add(nutrient)
        db_session.commit()
        db_session.refresh(nutrient)
        
        assert nutrient.id == "vitamin_c"
        assert nutrient.name == "Vitamin C"
        assert nutrient.nutrient_type == "vitamin"
        assert nutrient.function == "Immune system support"
        assert nutrient.source == "USDA"
    
    def test_set_function(self, db_session):
        """Test setting nutrient function."""
        nutrient = NutrientEntity(
            id="vitamin_c",
            name="Vitamin C",
            primary_classification="nutrient"
        )
        
        nutrient.set_function("Immune system support and antioxidant activity", source="research")
        
        assert nutrient.function == "Immune system support and antioxidant activity"
        assert nutrient.get_attribute("function_source") == "research"
    
    def test_set_source(self, db_session):
        """Test setting nutrient source."""
        nutrient = NutrientEntity(
            id="vitamin_c",
            name="Vitamin C",
            primary_classification="nutrient"
        )
        
        nutrient.set_source("USDA Nutrient Database")
        
        assert nutrient.source == "USDA Nutrient Database"
        assert nutrient.get_attribute("data_source") == "USDA Nutrient Database"


class TestCompoundEntityModel:
    """Test the CompoundEntity model."""
    
    def test_compound_entity_creation(self, db_session):
        """Test compound entity creation."""
        compound = CompoundEntity(
            id="curcumin",
            name="Curcumin",
            primary_classification="compound",
            molecular_formula="C21H20O6",
            molecular_weight="368.38",
            cas_number="458-37-7"
        )
        
        db_session.add(compound)
        db_session.commit()
        db_session.refresh(compound)
        
        assert compound.id == "curcumin"
        assert compound.name == "Curcumin"
        assert compound.molecular_formula == "C21H20O6"
        assert compound.molecular_weight == "368.38"
        assert compound.cas_number == "458-37-7"
    
    def test_set_molecular_data(self, db_session):
        """Test setting molecular data."""
        compound = CompoundEntity(
            id="curcumin",
            name="Curcumin",
            primary_classification="compound"
        )
        
        compound.set_molecular_data(
            formula="C21H20O6",
            weight="368.38",
            cas="458-37-7"
        )
        
        assert compound.molecular_formula == "C21H20O6"
        assert compound.molecular_weight == "368.38"
        assert compound.cas_number == "458-37-7"
    
    def test_set_molecular_data_without_cas(self, db_session):
        """Test setting molecular data without CAS number."""
        compound = CompoundEntity(
            id="test_compound",
            name="Test Compound",
            primary_classification="compound"
        )
        
        compound.set_molecular_data(
            formula="C10H12O",
            weight="148.20"
        )
        
        assert compound.molecular_formula == "C10H12O"
        assert compound.molecular_weight == "148.20"
        assert compound.cas_number is None


class TestEntityRelationships:
    """Test entity relationships with other models."""
    
    def test_entity_relationships(self, db_session, sample_entity, sample_relationship):
        """Test entity relationship connections."""
        # Refresh entities to get relationships
        db_session.refresh(sample_entity)
        
        # Check source relationships
        source_relationships = sample_entity.source_relationships
        assert len(source_relationships) == 1
        assert source_relationships[0].id == sample_relationship.id
        
        # Check target relationships
        target_entity = db_session.query(Entity).filter(Entity.id == "test_entity_2").first()
        target_relationships = target_entity.target_relationships
        assert len(target_relationships) == 1
        assert target_relationships[0].id == sample_relationship.id
    
    def test_entity_cascade_behavior(self, db_session):
        """Test entity cascade behavior when deleting."""
        # Create entity with relationships
        entity = Entity(
            id="test_entity",
            name="Test Entity",
            primary_classification="ingredient"
        )
        db_session.add(entity)
        
        target_entity = Entity(
            id="target_entity",
            name="Target Entity",
            primary_classification="compound"
        )
        db_session.add(target_entity)
        db_session.commit()
        
        # Create relationship
        relationship = RelationshipEntity(
            source_id="test_entity",
            target_id="target_entity",
            relationship_type="contains",
            confidence_score=3
        )
        db_session.add(relationship)
        db_session.commit()
        
        # Delete source entity
        db_session.delete(entity)
        db_session.commit()
        
        # Relationship should still exist (no cascade delete)
        remaining_relationships = db_session.query(RelationshipEntity).all()
        assert len(remaining_relationships) == 1
        assert remaining_relationships[0].source_id == "test_entity"  # Still references deleted entity
