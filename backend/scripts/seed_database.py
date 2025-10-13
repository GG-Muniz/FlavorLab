#!/usr/bin/env python3
"""
Database Seeding Script for FlavorLab

This script populates the database with enriched ingredient data from
health_pillar_ingredients_enriched.json. It's designed for development
and testing purposes.

⚠️  WARNING: This script is DESTRUCTIVE - it will delete all existing
    ingredient data before seeding new data. Only use for development/testing.

Usage:
    cd /home/holberton/FlavorLab/backend
    python scripts/seed_database.py

Requirements:
    - health_pillar_ingredients_enriched.json must exist
    - Database must be initialized (tables created)
    - Virtual environment should be activated
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add the backend directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

# Import application components
from app.database import SessionLocal, engine, Base
from app.models.entity import Entity, IngredientEntity
from app.models import User  # Import to ensure all tables are registered

# File paths
ENRICHED_DATA_FILE = os.path.join(backend_dir, "health_pillar_ingredients_enriched.json")


def ensure_tables_exist():
    """
    Ensure all database tables exist.
    This creates tables if they don't exist yet.
    """
    print("Checking database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables ready")
    except Exception as e:
        print(f"ERROR: Failed to create database tables: {e}")
        sys.exit(1)


def load_enriched_data() -> Dict[str, Any]:
    """
    Load the enriched ingredient data from JSON file.

    Returns:
        Dictionary containing metadata and entities list

    Raises:
        SystemExit: If file cannot be loaded
    """
    if not os.path.exists(ENRICHED_DATA_FILE):
        print(f"ERROR: Enriched data file not found: {ENRICHED_DATA_FILE}")
        print("Please run generate_enriched_ingredients_data.py first.")
        sys.exit(1)

    print(f"Loading enriched data from: {ENRICHED_DATA_FILE}")
    try:
        with open(ENRICHED_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded data with {len(data.get('entities', []))} entities")
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read file: {e}")
        sys.exit(1)


def clear_existing_data(db: SessionLocal) -> int:
    """
    Clear all existing ingredient and entity data from the database.

    Args:
        db: Database session

    Returns:
        Number of records deleted
    """
    print("\n⚠️  Clearing existing data...")
    print("   - Deleting ingredient entities...")

    try:
        # Delete ingredient entities first (due to foreign key constraints)
        ingredient_count = db.query(IngredientEntity).count()
        db.query(IngredientEntity).delete()
        print(f"   ✓ Deleted {ingredient_count} ingredient records")

        # Delete base entities
        entity_count = db.query(Entity).count()
        db.query(Entity).delete()
        print(f"   ✓ Deleted {entity_count} entity records")

        db.commit()
        print("✓ Database cleared successfully")

        return ingredient_count + entity_count

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to clear existing data: {e}")
        raise


def create_entity_from_json(entity_data: Dict[str, Any]) -> Entity:
    """
    Create an Entity object from JSON data.

    Args:
        entity_data: Dictionary containing entity information

    Returns:
        Entity instance
    """
    # Map JSON fields to Entity model fields
    entity = Entity(
        id=str(entity_data.get('id')),
        name=entity_data.get('name', 'Unknown'),
        primary_classification=entity_data.get('primary_classification', 'unknown'),
        classifications=entity_data.get('classifications', []),
        attributes=entity_data.get('attributes', {}),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    return entity


def create_ingredient_from_json(entity_data: Dict[str, Any]) -> IngredientEntity:
    """
    Create an IngredientEntity object from JSON data.

    Args:
        entity_data: Dictionary containing ingredient information

    Returns:
        IngredientEntity instance
    """
    # Create the ingredient entity with inherited fields
    ingredient = IngredientEntity(
        id=str(entity_data.get('id')),
        name=entity_data.get('name', 'Unknown'),
        primary_classification=entity_data.get('primary_classification', 'ingredient'),
        classifications=entity_data.get('classifications', []),
        attributes=entity_data.get('attributes', {}),
        health_outcomes=entity_data.get('health_outcomes', []),
        compounds=entity_data.get('compounds', []),
        foodb_priority=entity_data.get('foodb_priority'),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    return ingredient


def seed_data():
    """
    Main seeding function that orchestrates the database population process.
    """
    print("=" * 70)
    print("FlavorLab Database Seeding Script")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will DELETE all existing ingredient data!")
    print()

    # Ensure tables exist
    ensure_tables_exist()

    # Load enriched data
    enriched_data = load_enriched_data()
    entities = enriched_data.get('entities', [])
    metadata = enriched_data.get('metadata', {})

    if not entities:
        print("ERROR: No entities found in enriched data file.")
        sys.exit(1)

    print()
    print(f"Preparing to seed {len(entities)} entities")
    print(f"Source file metadata: {metadata.get('enrichment_timestamp', 'N/A')}")
    print()

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data
        deleted_count = clear_existing_data(db)

        # Statistics counters
        stats = {
            "ingredients_created": 0,
            "entities_created": 0,
            "ingredients_with_health_data": 0,
            "total_health_outcomes": 0,
            "errors": 0
        }

        # Seed entities
        print("\nSeeding database...")
        print("-" * 70)

        for idx, entity_data in enumerate(entities, 1):
            entity_id = entity_data.get('id')
            entity_name = entity_data.get('name', 'Unknown')
            classification = entity_data.get('primary_classification', 'unknown')

            try:
                # Progress indicator
                if idx % 20 == 0 or idx == len(entities):
                    print(f"  Processing: {idx}/{len(entities)} - {entity_name}")

                # Create appropriate entity type based on classification
                if classification == 'ingredient':
                    # Create as IngredientEntity for ingredients
                    entity = create_ingredient_from_json(entity_data)
                    stats["ingredients_created"] += 1

                    # Track health outcomes statistics
                    health_outcomes = entity_data.get('health_outcomes', [])
                    if health_outcomes:
                        stats["ingredients_with_health_data"] += 1
                        stats["total_health_outcomes"] += len(health_outcomes)

                else:
                    # Create as base Entity for nutrients, compounds, etc.
                    entity = create_entity_from_json(entity_data)
                    stats["entities_created"] += 1

                # Add to session
                db.add(entity)

            except Exception as e:
                print(f"\n  ⚠️  Error processing {entity_name} (ID: {entity_id}): {e}")
                stats["errors"] += 1
                continue

        # Commit all changes
        print("\nCommitting changes to database...")
        db.commit()
        print("✓ Successfully committed all changes")

        # Print summary
        print()
        print("=" * 70)
        print("SEEDING COMPLETE")
        print("=" * 70)
        print(f"Total entities processed:              {len(entities)}")
        print(f"  - Ingredients created:               {stats['ingredients_created']}")
        print(f"  - Other entities created:            {stats['entities_created']}")
        print(f"  - Ingredients with health data:      {stats['ingredients_with_health_data']}")
        print(f"  - Total health outcomes added:       {stats['total_health_outcomes']}")
        print(f"  - Errors encountered:                {stats['errors']}")
        print()

        if stats['errors'] > 0:
            print(f"⚠️  {stats['errors']} errors occurred during seeding")
        else:
            print("✅ All entities seeded successfully!")

        print()
        print("Database is ready for use!")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print()
        print("=" * 70)
        print("ERROR: Database seeding failed!")
        print("=" * 70)
        print(f"Error: {e}")
        print("\nChanges have been rolled back.")
        sys.exit(1)

    finally:
        db.close()
        print("\nDatabase session closed.")


def main():
    """
    Entry point for the script.
    """
    try:
        seed_data()
    except KeyboardInterrupt:
        print("\n\nSeeding interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
