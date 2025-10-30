"""
SQLAlchemy models for FlavorLab relationships.

This module defines the RelationshipEntity model for managing
connections between entities in the FlavorLab database.
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone as UTC
from typing import Dict, Any, Optional
from .entity import Base


class RelationshipEntity(Base):
    """
    Model representing relationships between entities.
    
    This model stores connections between entities such as:
    - "contains" (ingredient contains compound)
    - "found_in" (compound found in ingredient)
    - "related_to" (general relationships)
    """
    __tablename__ = "relationships"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relationship endpoints
    source_id = Column(String(255), ForeignKey("entities.id"), nullable=False, index=True)
    target_id = Column(String(255), ForeignKey("entities.id"), nullable=False, index=True)
    
    # Relationship type (contains, found_in, related_to, etc.)
    relationship_type = Column(String(100), nullable=False, index=True)
    
    # Quantitative data
    quantity = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    
    # Context and uncertainty information
    context = Column(JSON, default=dict)
    uncertainty = Column(JSON, default=dict)
    
    # Source and confidence
    source_reference = Column(Text, nullable=True)
    confidence_score = Column(Integer, default=3)  # 1-5 scale
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    source_entity = relationship(
        "Entity", 
        foreign_keys=[source_id],
        back_populates="source_relationships"
    )
    target_entity = relationship(
        "Entity", 
        foreign_keys=[target_id],
        back_populates="target_relationships"
    )
    
    def __repr__(self):
        return f"<Relationship({self.source_id} --{self.relationship_type}--> {self.target_id})>"
    
    def set_context(self, state: Optional[str] = None, mechanisms: Optional[list] = None, params: Optional[dict] = None) -> None:
        """
        Set context information for the relationship.
        
        Args:
            state: State of the entities (e.g., "raw", "cooked")
            mechanisms: List of mechanisms involved
            params: Additional parameters
        """
        self.context = {
            "state": state,
            "mechanisms": mechanisms or [],
            "params": params or {}
        }
    
    def set_uncertainty(self, mean: Optional[float] = None, sd: Optional[float] = None, 
                       min_val: Optional[float] = None, max_val: Optional[float] = None) -> None:
        """
        Set uncertainty information for the relationship.
        
        Args:
            mean: Mean value
            sd: Standard deviation
            min_val: Minimum value
            max_val: Maximum value
        """
        self.uncertainty = {
            "mean": mean,
            "sd": sd,
            "min": min_val,
            "max": max_val
        }
    
    def is_contains_relationship(self) -> bool:
        """Check if this is a 'contains' relationship."""
        return self.relationship_type == "contains"
    
    def is_found_in_relationship(self) -> bool:
        """Check if this is a 'found_in' relationship."""
        return self.relationship_type == "found_in"
    
    def get_quantity_with_unit(self) -> str:
        """Get formatted quantity with unit."""
        if self.quantity and self.unit:
            return f"{self.quantity} {self.unit}"
        elif self.quantity:
            return self.quantity
        else:
            return "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "quantity": self.quantity,
            "unit": self.unit,
            "context": self.context,
            "uncertainty": self.uncertainty,
            "source_reference": self.source_reference,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
