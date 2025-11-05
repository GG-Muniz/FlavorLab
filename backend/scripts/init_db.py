#!/usr/bin/env python3
"""
FlavorLab Database Initialization Script

This script creates the SQLite database and populates it with data from JSON files.
It handles the migration from the existing JSON data structure to the SQLAlchemy models.

Usage:
    python scripts/init_db.py [--drop-existing] [--entities-file path] [--relationships-file path]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
import re

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import create_tables, drop_tables, SessionLocal, engine
from app.models import (
    Entity,
    IngredientEntity,
    NutrientEntity,
    CompoundEntity,
    RelationshipEntity,
)
from app.config import get_settings


def _slugify(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value).strip('-')
    return value or None


def _extract_attribute_value(attributes: Optional[Dict[str, Any]], key: str, default=None):
    if not isinstance(attributes, dict):
        return default
    value = attributes.get(key, default)
    if isinstance(value, dict) and "value" in value:
        return value.get("value", default)
    return value if value is not None else default


def _parse_datetime(value: Optional[str]):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:
        return None


class DataMigrator:
    """
    Handles migration of JSON data to SQLite database.
    """
    
    def __init__(self, entities_file: str | object, relationships_file: str | object = None, json_path: str | None = None):
        """
        Initialize the data migrator.
        
        Args:
            entities_file: Path to entities JSON file OR db_session when using validation mode
            relationships_file: Path to relationships JSON file
            json_path: Optional directory path containing JSON files for validation mode
        """
        # Support two modes:
        # 1) File mode: entities_file and relationships_file are file paths
        # 2) Validation mode (used in tests): entities_file is a Session and json_path is provided
        self.session = None
        self.settings = get_settings()
        self.validation_mode = False

        if json_path is not None and relationships_file is None:
            # Validation mode
            from sqlalchemy.orm import Session as SASession
            if not isinstance(entities_file, SASession):
                raise TypeError("In validation mode, first argument must be a SQLAlchemy Session")
            self.session = entities_file
            base_path = Path(json_path)
            self.entities_file = str(base_path / self.settings.entities_file)
            self.relationships_file = str(base_path / self.settings.relationships_file)
            self.validation_mode = True
        else:
            # File mode
            self.entities_file = str(entities_file)
            self.relationships_file = str(relationships_file)

        
    def __enter__(self):
        """Context manager entry."""
        self.session = SessionLocal()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            self.session.close()
    
    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load JSON data from file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict containing the JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        print(f"Loading data from: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data.get('entities', data.get('relationships', [])))} items")
        return data
    
    def migrate_entities(self, entities_data: List[Dict[str, Any]]) -> int:
        """
        Migrate entities from JSON to database.
        
        Args:
            entities_data: List of entity dictionaries from JSON
            
        Returns:
            Number of entities migrated
        """
        print(f"Migrating {len(entities_data)} entities...")
        
        migrated_count = 0
        batch_size = self.settings.batch_size

        # Track existing IDs to avoid duplicates within and across batches
        try:
            existing_ids = [row[0] for row in self.session.query(Entity.id).all()]
        except Exception:
            existing_ids = []
        seen_ids = set(existing_ids)
        
        for i in range(0, len(entities_data), batch_size):
            batch = entities_data[i:i + batch_size]

            batch_added = 0
            for entity_data in batch:
                try:
                    # Skip if required fields are missing
                    if not entity_data.get('id') or not entity_data.get('name') or not entity_data.get('primary_classification'):
                        continue

                    entity_id = str(entity_data['id'])

                    # Skip duplicates (already present or already staged in this run)
                    if entity_id in seen_ids:
                        continue

                    raw_attributes = entity_data.get('attributes') or {}

                    slug = entity_data.get('slug')
                    if not slug:
                        slug = _slugify(entity_data.get('name'))

                    entity_kwargs: Dict[str, Any] = {
                        'id': entity_id,
                        'name': entity_data['name'],
                        'primary_classification': entity_data['primary_classification'],
                        'classifications': list(entity_data.get('classifications') or []),
                        'attributes': dict(raw_attributes),
                        'aliases': entity_data.get('aliases') or entity_data.get('synonyms') or [],
                        'display_name': entity_data.get('display_name') or entity_data.get('name'),
                        'slug': slug,
                        'image_url': entity_data.get('image_url'),
                        'image_attribution': entity_data.get('image_attribution'),
                        'is_active': entity_data.get('is_active', True),
                    }

                    created_at = _parse_datetime(entity_data.get('created_at'))
                    if created_at:
                        entity_kwargs['created_at'] = created_at
                    updated_at = _parse_datetime(entity_data.get('updated_at'))
                    if updated_at:
                        entity_kwargs['updated_at'] = updated_at

                    classification = (entity_data.get('primary_classification') or '').lower()

                    if classification == 'ingredient':
                        entity = IngredientEntity(**entity_kwargs)

                        foodb_priority = _extract_attribute_value(raw_attributes, 'foodb_priority')
                        if foodb_priority:
                            entity.foodb_priority = foodb_priority

                        health_outcomes = _extract_attribute_value(raw_attributes, 'health_outcomes') or []
                        if isinstance(health_outcomes, list):
                            entity.health_outcomes = []
                            for outcome in health_outcomes:
                                if isinstance(outcome, str):
                                    try:
                                        entity.add_health_outcome(outcome)
                                    except Exception:
                                        continue

                        key_compounds = _extract_attribute_value(raw_attributes, 'key_compounds') or []
                        if isinstance(key_compounds, list):
                            entity.compounds = []
                            for compound in key_compounds:
                                if isinstance(compound, str):
                                    try:
                                        entity.add_compound(compound)
                                    except Exception:
                                        continue

                    elif classification == 'nutrient':
                        entity = NutrientEntity(**entity_kwargs)

                        nutrient_type = _extract_attribute_value(raw_attributes, 'nutrient_type')
                        if nutrient_type:
                            entity.nutrient_type = nutrient_type

                        function = _extract_attribute_value(raw_attributes, 'function')
                        if function:
                            entity.function = function

                        source = _extract_attribute_value(raw_attributes, 'source')
                        if source:
                            entity.source = source

                    elif classification == 'compound':
                        entity = CompoundEntity(**entity_kwargs)

                        molecular_formula = _extract_attribute_value(raw_attributes, 'molecular_formula')
                        if molecular_formula:
                            entity.molecular_formula = molecular_formula

                        molecular_weight = _extract_attribute_value(raw_attributes, 'molecular_weight')
                        if molecular_weight:
                            entity.molecular_weight = molecular_weight

                        cas_number = _extract_attribute_value(raw_attributes, 'cas_number')
                        if cas_number:
                            entity.cas_number = cas_number

                    else:
                        entity = Entity(**entity_kwargs)

                    # Add to session
                    self.session.add(entity)
                    seen_ids.add(entity_id)
                    batch_added += 1

                except Exception as e:
                    print(f"Error migrating entity {entity_data.get('id', 'unknown')}: {e}")
                    continue

            # Commit batch
            try:
                self.session.commit()
                print(f"Migrated batch {i//batch_size + 1}: {len(batch)} entities")
                migrated_count += batch_added
            except Exception as e:
                print(f"Error committing batch: {e}")
                self.session.rollback()
                # Roll back seen IDs added in this batch since commit failed
                # (conservative; ensures no false positives in counters)
                # Note: for simplicity, we rebuild seen_ids from DB after rollback
                try:
                    existing_ids = [row[0] for row in self.session.query(Entity.id).all()]
                    seen_ids = set(existing_ids)
                except Exception:
                    pass
                continue
        
        print(f"Successfully migrated {migrated_count} entities")
        return migrated_count
    
    def migrate_relationships(self, relationships_data: List[Dict[str, Any]]) -> int:
        """
        Migrate relationships from JSON to database.
        
        Args:
            relationships_data: List of relationship dictionaries from JSON
            
        Returns:
            Number of relationships migrated
        """
        print(f"Migrating {len(relationships_data)} relationships...")
        
        migrated_count = 0
        batch_size = self.settings.batch_size
        
        for i in range(0, len(relationships_data), batch_size):
            batch = relationships_data[i:i + batch_size]
            
            for rel_data in batch:
                try:
                    # Create RelationshipEntity instance
                    relationship = RelationshipEntity(
                        source_id=str(rel_data['source_id']),
                        target_id=str(rel_data['target_id']),
                        relationship_type=rel_data['relationship_type'],
                        quantity=rel_data.get('quantity'),
                        unit=rel_data.get('unit'),
                        context=rel_data.get('context', {}),
                        uncertainty=rel_data.get('uncertainty', {}),
                        source_reference=rel_data.get('source_reference'),
                        confidence_score=rel_data.get('confidence_score', 3)
                    )
                    
                    # Add to session
                    self.session.add(relationship)
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Error migrating relationship {rel_data.get('source_id', 'unknown')} -> {rel_data.get('target_id', 'unknown')}: {e}")
                    continue
            
            # Commit batch
            try:
                self.session.commit()
                print(f"Migrated batch {i//batch_size + 1}: {len(batch)} relationships")
            except Exception as e:
                print(f"Error committing batch: {e}")
                self.session.rollback()
                continue
        
        print(f"Successfully migrated {migrated_count} relationships")
        return migrated_count
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate the migration by counting records in the database.
        
        Returns:
            Dict with counts of entities and relationships
        """
        print("Validating migration...")
        
        entity_count = self.session.query(Entity).count()
        relationship_count = self.session.query(RelationshipEntity).count()
        
        print(f"Database contains:")
        print(f"  - {entity_count} entities")
        print(f"  - {relationship_count} relationships")
        
        # Build a richer report expected by tests
        return {
            "entities": {
                "source_count": self._count_source_entities(),
                "db_count": entity_count,
                "match": self._count_source_entities() == entity_count,
            },
            "relationships": {
                "source_count": self._count_source_relationships(),
                "db_count": relationship_count,
                "match": self._count_source_relationships() == relationship_count,
            },
        }

    def _count_source_entities(self) -> int:
        try:
            data = self.load_json_data(self.entities_file)
            # support both flat list and grouped format used in tests
            if isinstance(data.get("entities"), list):
                return len(data.get("entities", []))
            groups = data.get("entities", {})
            return sum(len(v or []) for v in groups.values())
        except Exception:
            return 0

    def _count_source_relationships(self) -> int:
        try:
            data = self.load_json_data(self.relationships_file)
            return len(data.get("relationships", []))
        except Exception:
            return 0
    
    def run_migration(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            True if migration was successful, False otherwise
        """
        try:
            print("Starting FlavorLab database migration...")
            print(f"Database: {self.settings.database_name}")
            print(f"Entities file: {self.entities_file}")
            print(f"Relationships file: {self.relationships_file}")
            print("-" * 50)
            
            # Load entities data
            entities_data = self.load_json_data(self.entities_file)
            entities_list = entities_data.get('entities', [])
            
            # Load relationships data
            relationships_data = self.load_json_data(self.relationships_file)
            relationships_list = relationships_data.get('relationships', [])
            
            # Migrate entities
            entity_count = self.migrate_entities(entities_list)
            
            # Migrate relationships
            relationship_count = self.migrate_relationships(relationships_list)
            
            # Validate migration
            validation = self.validate_migration()
            
            print("-" * 50)
            print("Migration completed successfully!")
            print(f"Migrated {entity_count} entities and {relationship_count} relationships")
            
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            if self.session:
                self.session.rollback()
            return False

    def run(self) -> bool:
        """Run migration using the configured mode.

        In validation mode (tests), we use the provided session and JSON path,
        support grouped entities structure, and do not manage the session context.
        In file mode, this delegates to run_migration().
        """
        if not self.validation_mode:
            return self.run_migration()

        try:
            # Load data
            entities_data = self.load_json_data(self.entities_file)
            relationships_data = self.load_json_data(self.relationships_file)

            # Normalize entities: support list or grouped dict
            raw_entities = entities_data.get('entities', [])
            if isinstance(raw_entities, dict):
                flattened: List[Dict[str, Any]] = []
                group_to_class = {
                    "ingredients": "ingredient",
                    "nutrients": "nutrient",
                    "compounds": "compound",
                }
                for group_name, group_list in raw_entities.items():
                    inferred_class = group_to_class.get(group_name, group_name.rstrip('s'))
                    for item in (group_list or []):
                        # Ensure primary_classification is present
                        if not item.get("primary_classification"):
                            item = {**item, "primary_classification": inferred_class}
                        flattened.append(item)
                entities_list = flattened
            else:
                entities_list = raw_entities

            # Normalize relationships
            relationships_list = relationships_data.get('relationships', [])

            # Migrate
            self.migrate_entities(entities_list)
            self.migrate_relationships(relationships_list)
            return True
        except Exception as e:
            print(f"Validation-mode run failed: {e}")
            if self.session:
                self.session.rollback()
            return False


def main():
    """Main function to run the database initialization."""
    parser = argparse.ArgumentParser(description="Initialize FlavorLab database with JSON data")
    parser.add_argument("--drop-existing", action="store_true", 
                       help="Drop existing tables before creating new ones")
    parser.add_argument("--entities-file", type=str, 
                       default="entities.json",
                       help="Path to entities JSON file")
    parser.add_argument("--relationships-file", type=str,
                       default="entity_relationships.json", 
                       help="Path to relationships JSON file")
    
    args = parser.parse_args()
    
    # Get settings
    settings = get_settings()
    
    # Resolve file paths
    entities_file = os.path.join(settings.json_data_path, args.entities_file)
    relationships_file = os.path.join(settings.json_data_path, args.relationships_file)
    
    print("FlavorLab Database Initialization")
    print("=" * 40)
    
    # Drop existing tables if requested
    if args.drop_existing:
        print("Dropping existing tables...")
        drop_tables()
    
    # Create tables
    print("Creating database tables...")
    create_tables()
    
    # Run migration
    with DataMigrator(entities_file, relationships_file) as migrator:
        success = migrator.run_migration()
    
    if success:
        print("\n✅ Database initialization completed successfully!")
        print(f"Database file: {settings.database_name}")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
