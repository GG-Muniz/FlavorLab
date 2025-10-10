"""
SQLAlchemy models for FlavorLab entities.

This module defines the core Entity model and specialized entity types
for ingredients, nutrients, and compounds.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from ..database import Base


class Entity(Base):
    """
    Base entity model representing any item in the FlavorLab database.
    
    This is the core model that can represent ingredients, nutrients, compounds,
    or any other entity type. It uses a flexible attribute system to store
    type-specific data.
    """
    __tablename__ = "entities"
    
    # Primary key - can be string or integer
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    primary_classification = Column(String(100), nullable=False, index=True)
    
    # Flexible classifications as JSON array
    classifications = Column(JSON, default=list)
    
    # Flexible attributes system - stores type-specific data
    attributes = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    source_relationships = relationship(
        "RelationshipEntity", 
        foreign_keys="RelationshipEntity.source_id",
        back_populates="source_entity",
        passive_deletes=True
    )
    target_relationships = relationship(
        "RelationshipEntity", 
        foreign_keys="RelationshipEntity.target_id",
        back_populates="target_entity",
        passive_deletes=True
    )
    
    def __repr__(self):
        return f"<Entity(id='{self.id}', name='{self.name}', type='{self.primary_classification}')>"
    
    def add_classification(self, classification: str) -> None:
        """Add a classification to the entity."""
        if self.classifications is None:
            self.classifications = []
        if classification not in self.classifications:
            self.classifications.append(classification)
    
    def add_attribute(self, key: str, value: Any, source: Optional[str] = None, confidence: Optional[int] = None) -> None:
        """
        Add an attribute to the entity.
        
        Args:
            key: Attribute name
            value: Attribute value
            source: Source of the attribute data
            confidence: Confidence score (1-5)
        """
        if self.attributes is None:
            self.attributes = {}
        
        self.attributes[key] = {
            "value": value,
            "source": source,
            "confidence": confidence
        }
    
    def get_attribute(self, key: str) -> Optional[Any]:
        """Get an attribute value by key."""
        if self.attributes and key in self.attributes:
            return self.attributes[key].get("value")
        return None
    
    def is_ingredient(self) -> bool:
        """Check if this entity is an ingredient."""
        return self.primary_classification == "ingredient"
    
    def is_nutrient(self) -> bool:
        """Check if this entity is a nutrient."""
        return self.primary_classification == "nutrient"
    
    def is_compound(self) -> bool:
        """Check if this entity is a compound."""
        return self.primary_classification == "compound"


class IngredientEntity(Entity):
    """
    Specialized entity for ingredients.
    
    This model inherits from Entity and adds ingredient-specific methods
    and properties.
    """
    __tablename__ = "ingredient_entities"
    
    # Primary key that references the base entity
    id = Column(String(255), ForeignKey("entities.id"), primary_key=True)
    
    # Additional ingredient-specific fields
    foodb_priority = Column(String(50), nullable=True)
    health_outcomes = Column(JSON, default=list)
    compounds = Column(JSON, default=list)
    
    def add_health_outcome(self, outcome: str, confidence: int = 3) -> None:
        """Add a health outcome to the ingredient."""
        if self.health_outcomes is None:
            self.health_outcomes = []
        
        outcome_data = {
            "outcome": outcome,
            "confidence": confidence,
            "added_at": datetime.now(UTC).isoformat()
        }
        
        # Check if outcome already exists
        existing = next((h for h in self.health_outcomes if h.get("outcome") == outcome), None)
        if existing:
            existing["confidence"] = confidence
            existing["updated_at"] = datetime.now(UTC).isoformat()
        else:
            self.health_outcomes.append(outcome_data)
    
    def add_compound(self, compound_id: str, quantity: Optional[str] = None, unit: Optional[str] = None) -> None:
        """Add a compound to the ingredient."""
        if self.compounds is None:
            self.compounds = []
        
        compound_data = {
            "compound_id": compound_id,
            "quantity": quantity,
            "unit": unit,
            "added_at": datetime.now(UTC).isoformat()
        }
        
        # Check if compound already exists
        existing = next((c for c in self.compounds if c.get("compound_id") == compound_id), None)
        if existing:
            existing.update({
                "quantity": quantity,
                "unit": unit,
                "updated_at": datetime.now(UTC).isoformat()
            })
        else:
            self.compounds.append(compound_data)


class NutrientEntity(Entity):
    """
    Specialized entity for nutrients.
    
    This model inherits from Entity and adds nutrient-specific methods
    and properties.
    """
    __tablename__ = "nutrient_entities"
    
    # Primary key that references the base entity
    id = Column(String(255), ForeignKey("entities.id"), primary_key=True)
    
    # Additional nutrient-specific fields
    nutrient_type = Column(String(100), nullable=True)
    function = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    
    def set_function(self, function: str, source: Optional[str] = None) -> None:
        """Set the function description for the nutrient."""
        self.function = function
        if source:
            self.add_attribute("function_source", source)
    
    def set_source(self, source: str) -> None:
        """Set the source of the nutrient data."""
        self.source = source
        self.add_attribute("data_source", source)


class CompoundEntity(Entity):
    """
    Specialized entity for compounds.
    
    This model inherits from Entity and adds compound-specific methods
    and properties.
    """
    __tablename__ = "compound_entities"
    
    # Primary key that references the base entity
    id = Column(String(255), ForeignKey("entities.id"), primary_key=True)
    
    # Additional compound-specific fields
    molecular_formula = Column(String(255), nullable=True)
    molecular_weight = Column(String(50), nullable=True)
    cas_number = Column(String(50), nullable=True)
    
    def set_molecular_data(self, formula: str, weight: str, cas: Optional[str] = None) -> None:
        """Set molecular data for the compound."""
        self.molecular_formula = formula
        self.molecular_weight = weight
        if cas:
            self.cas_number = cas
