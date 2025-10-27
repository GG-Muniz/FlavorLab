"""
SQLAlchemy models for FlavorLab entities.

This module defines the core Entity model and specialized entity types
for ingredients, nutrients, and compounds.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey, func
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import relationship, Session, Query
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from ..database import Base
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint
from .health_pillars import get_pillar_ids_for_outcome


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
    # URL-friendly identifier; not enforced unique in SQLite migration, but indexed
    slug = Column(String(255), nullable=True, index=True)
    # Optional display name separate from canonical name
    display_name = Column(String(255), nullable=True)
    primary_classification = Column(String(100), nullable=False, index=True)
    
    # Flexible classifications as JSON array
    classifications = Column(MutableList.as_mutable(JSON), default=list)
    # Search helpers and metadata
    aliases = Column(MutableList.as_mutable(JSON), default=list)
    
    # Flexible attributes system - stores type-specific data
    attributes = Column(MutableDict.as_mutable(JSON), default=dict)
    # Media
    image_url = Column(String(512), nullable=True)
    image_attribution = Column(String(512), nullable=True)
    # Lifecycle
    is_active = Column(Boolean, default=True, nullable=False)
    
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
    health_outcomes = Column(MutableList.as_mutable(JSON), default=list)
    compounds = Column(MutableList.as_mutable(JSON), default=list)
    
    def add_health_outcome(self, outcome: str, confidence: int = 3) -> None:
        """
        Add a health outcome to the ingredient with automatic pillar mapping.

        This method also handles migration from old data format {"value": [...]}
        to new format [{"outcome": "...", "confidence": ..., "pillars": [...]}].

        Args:
            outcome: Health outcome string (e.g., "Anti-inflammatory", "Supports digestion")
            confidence: Confidence score 1-5 (default: 3)
        """
        # Initialize if None
        if self.health_outcomes is None:
            self.health_outcomes = []

        # Migrate old format: {"value": ["outcome1", "outcome2"]} -> new list format
        if isinstance(self.health_outcomes, dict) and "value" in self.health_outcomes:
            old_outcomes = self.health_outcomes.get("value", [])
            migrated_outcomes = []

            for old_outcome in old_outcomes:
                if isinstance(old_outcome, str):
                    # Map pillars for each old outcome
                    pillar_ids = get_pillar_ids_for_outcome(old_outcome)
                    migrated_outcomes.append({
                        "outcome": old_outcome,
                        "confidence": 3,  # Default confidence for migrated data
                        "added_at": datetime.now(UTC).isoformat(),
                        "pillars": pillar_ids
                    })

            # Replace with migrated data
            self.health_outcomes = migrated_outcomes

        # Map outcome string to health pillar IDs
        pillar_ids = get_pillar_ids_for_outcome(outcome)

        # Create new outcome data with pillars
        outcome_data = {
            "outcome": outcome,
            "confidence": confidence,
            "added_at": datetime.now(UTC).isoformat(),
            "pillars": pillar_ids
        }

        # Check if outcome already exists (update if so)
        existing = next((h for h in self.health_outcomes if h.get("outcome") == outcome), None)
        if existing:
            existing["confidence"] = confidence
            existing["updated_at"] = datetime.now(UTC).isoformat()
            existing["pillars"] = pillar_ids  # Update pillars
        else:
            self.health_outcomes.append(outcome_data)

        # Ensure SQLAlchemy detects the change to JSON column
        flag_modified(self, "health_outcomes")
    
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

    @classmethod
    def get_ingredients_by_pillar(
        cls,
        db: Session,
        pillar_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List['IngredientEntity']:
        """
        Query ingredients that have health outcomes associated with a specific health pillar.

        This method searches for ingredients where at least one health outcome
        contains the specified pillar_id in its pillars array.

        Args:
            db: SQLAlchemy database session
            pillar_id: Health pillar ID (1-8)
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of IngredientEntity instances matching the pillar

        Example:
            # Get ingredients supporting "Inflammation Reduction" (pillar 8)
            ingredients = IngredientEntity.get_ingredients_by_pillar(db, pillar_id=8)
        """
        # SQLite JSON query: Check if any outcome in health_outcomes array
        # has the pillar_id in its pillars array
        # Using json_each to expand the health_outcomes array
        query = db.query(cls).filter(
            func.json_extract(cls.health_outcomes, '$').isnot(None)
        )

        # Get all ingredients and filter in Python (works for SQLite)
        # For production with PostgreSQL, use native JSONB operators
        all_ingredients = query.offset(skip).limit(limit).all()

        # Filter ingredients that have the pillar_id in any outcome's pillars
        matching_ingredients = []
        for ingredient in all_ingredients:
            if isinstance(ingredient.health_outcomes, list):
                for outcome in ingredient.health_outcomes:
                    if isinstance(outcome, dict) and "pillars" in outcome:
                        if pillar_id in outcome["pillars"]:
                            matching_ingredients.append(ingredient)
                            break

        return matching_ingredients

    @classmethod
    def filter_ingredients_by_pillars(
        cls,
        query: Query,
        pillar_ids: Optional[List[int]]
    ) -> Query:
        """
        Add a filter to an existing query to find ingredients with specific health pillars.

        This method modifies an existing SQLAlchemy query to filter ingredients
        whose health_outcomes contain at least one outcome whose pillars list
        intersects with the provided pillar_ids.

        Args:
            query: Existing SQLAlchemy Query object for IngredientEntity
            pillar_ids: List of health pillar IDs to filter by (1-8).
                       If None or empty, returns the query unchanged.

        Returns:
            Modified Query object with pillar filter applied

        Example:
            # Start with a base query
            query = db.query(IngredientEntity)

            # Filter by multiple pillars (Digestion=2, Immunity=3)
            query = IngredientEntity.filter_ingredients_by_pillars(query, [2, 3])

            # Execute query
            ingredients = query.all()
        """
        if not pillar_ids:
            return query

        # For SQLite: Filter using json_extract
        # This checks if health_outcomes is not null/empty
        query = query.filter(
            func.json_extract(cls.health_outcomes, '$').isnot(None)
        )

        # Note: For SQLite, we need to do additional filtering in application code
        # For PostgreSQL, we would use:
        # query = query.filter(
        #     cls.health_outcomes.op('@>')(
        #         func.cast([{"pillars": pillar_ids}], JSONB)
        #     )
        # )

        return query


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
