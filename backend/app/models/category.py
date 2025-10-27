"""
Category and association models for ingredient taxonomy.

Provides hierarchical categories and a many-to-many link between
ingredients and categories.
"""

from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..database import Base


# Association table linking ingredients to categories
IngredientCategory = Table(
    "ingredient_categories",
    Base.metadata,
    Column(
        "ingredient_id",
        String(255),
        ForeignKey("ingredient_entities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("ingredient_id", "category_id", name="uq_ingredient_category"),
)


class Category(Base):
    """Hierarchical category for classifying ingredients."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(120), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Self-referential parent/children
    parent = relationship("Category", remote_side=[id], backref="children")

    # Many-to-many to IngredientEntity (defined in entity.py)
    ingredients = relationship(
        "IngredientEntity",
        secondary=IngredientCategory,
        backref="categories",
    )

    __table_args__ = (
        UniqueConstraint("slug", name="uq_category_slug"),
        UniqueConstraint("name", "parent_id", name="uq_category_name_parent"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"


