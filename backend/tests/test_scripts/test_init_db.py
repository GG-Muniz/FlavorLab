"""
Tests for the database initialization script.

This module tests the scripts/init_db.py functionality to ensure
proper database creation and data migration from JSON files.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.database import create_tables, drop_tables, engine, SessionLocal
from app.models import Entity, RelationshipEntity, User
from scripts.init_db import DataMigrator, main
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestDataMigrator:
    """Test the DataMigrator class functionality."""
    
    def test_load_json_data_success(self, temp_json_file):
        """Test successful JSON data loading."""
        migrator = DataMigrator(temp_json_file, temp_json_file)
        
        data = migrator.load_json_data(temp_json_file)
        
        assert "metadata" in data
        assert "entities" in data
        assert data["metadata"]["total_entities"] == 2
        assert len(data["entities"]) == 2
    
    def test_load_json_data_file_not_found(self):
        """Test JSON data loading with non-existent file."""
        migrator = DataMigrator("nonexistent.json", "nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            migrator.load_json_data("nonexistent.json")
    
    def test_load_json_data_invalid_json(self):
        """Test JSON data loading with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            migrator = DataMigrator(temp_file, temp_file)
            
            with pytest.raises(json.JSONDecodeError):
                migrator.load_json_data(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_migrate_entities_success(self, db_session, temp_json_file):
        """Test successful entity migration."""
        migrator = DataMigrator(temp_json_file, temp_json_file)
        
        with migrator:
            migrator.session = db_session
            
            # Load test data
            data = migrator.load_json_data(temp_json_file)
            entities_data = data["entities"]
            
            # Migrate entities
            migrated_count = migrator.migrate_entities(entities_data)
            
            assert migrated_count == 2
            
            # Verify entities were created
            entities = db_session.query(Entity).all()
            assert len(entities) == 2
            
            # Check specific entity
            test_ingredient = db_session.query(Entity).filter(Entity.id == "test_ingredient").first()
            assert test_ingredient is not None
            assert test_ingredient.name == "Test Ingredient"
            assert test_ingredient.primary_classification == "ingredient"
    
    def test_migrate_entities_batch_processing(self, db_session):
        """Test entity migration with batch processing."""
        # Create test data with more entities than batch size
        test_data = {
            "entities": [
                {
                    "id": f"entity_{i}",
                    "name": f"Entity {i}",
                    "primary_classification": "ingredient",
                    "classifications": ["test"],
                    "attributes": {}
                }
                for i in range(5)  # More than default batch size
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            migrator = DataMigrator(temp_file, temp_file)
            
            with migrator:
                migrator.session = db_session
                
                migrated_count = migrator.migrate_entities(test_data["entities"])
                
                assert migrated_count == 5
                
                # Verify all entities were created
                entities = db_session.query(Entity).all()
                assert len(entities) == 5
        finally:
            os.unlink(temp_file)
    
    def test_migrate_entities_invalid_data(self, db_session):
        """Test entity migration with invalid data."""
        invalid_entities = [
            {
                "id": "valid_entity",
                "name": "Valid Entity",
                "primary_classification": "ingredient",
                "classifications": ["test"],
                "attributes": {}
            },
            {
                # Missing required fields
                "name": "Invalid Entity"
            }
        ]
        
        migrator = DataMigrator("dummy.json", "dummy.json")
        
        with migrator:
            migrator.session = db_session
            
            # Should handle invalid data gracefully
            migrated_count = migrator.migrate_entities(invalid_entities)
            
            # Should migrate valid entities only
            assert migrated_count == 1
            
            entities = db_session.query(Entity).all()
            assert len(entities) == 1
            assert entities[0].id == "valid_entity"
    
    def test_migrate_relationships_success(self, db_session):
        """Test successful relationship migration."""
        # Create test entities first
        entity1 = Entity(id="source_entity", name="Source", primary_classification="ingredient")
        entity2 = Entity(id="target_entity", name="Target", primary_classification="compound")
        db_session.add_all([entity1, entity2])
        db_session.commit()
        
        # Create test relationship data
        relationships_data = [
            {
                "source_id": "source_entity",
                "target_id": "target_entity",
                "relationship_type": "contains",
                "quantity": "1.0",
                "unit": "g/100g",
                "context": {"state": "raw"},
                "uncertainty": {"mean": 1.0},
                "source_reference": "test",
                "confidence_score": 4
            }
        ]
        
        migrator = DataMigrator("dummy.json", "dummy.json")
        
        with migrator:
            migrator.session = db_session
            
            migrated_count = migrator.migrate_relationships(relationships_data)
            
            assert migrated_count == 1
            
            # Verify relationship was created
            relationships = db_session.query(RelationshipEntity).all()
            assert len(relationships) == 1
            
            rel = relationships[0]
            assert rel.source_id == "source_entity"
            assert rel.target_id == "target_entity"
            assert rel.relationship_type == "contains"
            assert rel.confidence_score == 4
    
    def test_validate_migration(self, db_session: Session, temp_json_file):
        """Test the complete migration validation."""
        migrator = DataMigrator(db_session, json_path=str(temp_json_file.parent))
        migrator.run()
        
        report = migrator.validate_migration()
        
        assert report["entities"]["source_count"] == 2
        assert report["entities"]["db_count"] == 2
        assert report["entities"]["match"] is True
        
        assert report["relationships"]["source_count"] == 1
        assert report["relationships"]["db_count"] == 1
        assert report["relationships"]["match"] is True
    
    def test_run_migration_success(self, db_session):
        """Test complete migration process."""
        # Create test JSON files
        entities_data = {
            "metadata": {"total_entities": 1},
            "entities": [
                {
                    "id": "migration_test",
                    "name": "Migration Test Entity",
                    "primary_classification": "ingredient",
                    "classifications": ["test"],
                    "attributes": {}
                }
            ]
        }
        
        relationships_data = {
            "metadata": {"total_relationships": 0},
            "relationships": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as entities_file:
            json.dump(entities_data, entities_file)
            entities_path = entities_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as relationships_file:
            json.dump(relationships_data, relationships_file)
            relationships_path = relationships_file.name
        
        try:
            migrator = DataMigrator(entities_path, relationships_path)
            
            with migrator:
                migrator.session = db_session
                
                success = migrator.run_migration()
                
                assert success is True
                
                # Verify migration results
                entities = db_session.query(Entity).all()
                assert len(entities) == 1
                assert entities[0].id == "migration_test"
        finally:
            os.unlink(entities_path)
            os.unlink(relationships_path)


class TestInitDbScript:
    """Test the main init_db.py script functionality."""
    
    def test_create_tables(self, db_session):
        """Test that create_tables creates all necessary tables."""
        # Drop tables first
        drop_tables()
        
        # Verify no tables exist
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            assert len(tables) == 0
        
        # Create tables
        create_tables()
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ["entities", "relationships", "users"]
            for table in expected_tables:
                assert table in tables
    
    def test_drop_tables(self, db_session):
        """Test that drop_tables removes all tables."""
        # Create tables first
        create_tables()
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            assert len(tables) > 0
        
        # Drop tables
        drop_tables()
        
        # Verify tables were dropped
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            assert len(tables) == 0
    
    @patch('scripts.init_db.get_settings')
    @patch('scripts.init_db.create_tables')
    @patch('scripts.init_db.DataMigrator')
    def test_main_function_success(self, mock_migrator_class, mock_create_tables, mock_get_settings):
        """Test the main function with successful migration."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.database_name = "test.db"
        mock_settings.json_data_path = "."
        mock_get_settings.return_value = mock_settings
        
        # Mock migrator
        mock_migrator = MagicMock()
        mock_migrator.run_migration.return_value = True
        mock_migrator_class.return_value.__enter__.return_value = mock_migrator
        
        # Mock command line arguments
        with patch('sys.argv', ['init_db.py']):
            # This should not raise an exception
            try:
                main()
            except SystemExit as e:
                # main() calls sys.exit(0) on success
                assert e.code == 0
        
        # Verify create_tables was called
        mock_create_tables.assert_called_once()
        
        # Verify migrator was used
        mock_migrator.run_migration.assert_called_once()
    
    @patch('scripts.init_db.get_settings')
    @patch('scripts.init_db.create_tables')
    @patch('scripts.init_db.DataMigrator')
    def test_main_function_failure(self, mock_migrator_class, mock_create_tables, mock_get_settings):
        """Test the main function with failed migration."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.database_name = "test.db"
        mock_settings.json_data_path = "."
        mock_get_settings.return_value = mock_settings
        
        # Mock migrator with failure
        mock_migrator = MagicMock()
        mock_migrator.run_migration.return_value = False
        mock_migrator_class.return_value.__enter__.return_value = mock_migrator
        
        # Mock command line arguments
        with patch('sys.argv', ['init_db.py']):
            # This should exit with code 1
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestDataIntegrity:
    """Test data integrity during migration."""
    
    def test_entity_id_uniqueness(self, db_session: Session, temp_json_file):
        """Test that duplicate entity IDs are handled correctly."""
        # Create JSON with duplicate IDs
        entities = {
            "ingredients": [{"id": "ingredient1", "name": "Ingredient 1"}],
            "nutrients": [{"id": "nutrient1", "name": "Nutrient 1"}],
            "compounds": [{"id": "ingredient1", "name": "Compound with duplicate ID"}]
        }
        relationships = []
        
        with open(temp_json_file, "w") as f:
            json.dump({"entities": entities, "relationships": relationships}, f)
            
        migrator = DataMigrator(db_session, json_path=str(temp_json_file.parent))
        migrator.run()
        
        entity_count = db_session.query(Entity).count()
        assert entity_count == 2
    
    def test_relationship_entity_references(self, db_session):
        """Test that relationships reference existing entities."""
        # Create test entity
        entity = Entity(id="test_entity", name="Test", primary_classification="ingredient")
        db_session.add(entity)
        db_session.commit()
        
        relationships_data = [
            {
                "source_id": "test_entity",  # Valid reference
                "target_id": "nonexistent_entity",  # Invalid reference
                "relationship_type": "contains",
                "confidence_score": 3
            }
        ]
        
        migrator = DataMigrator("dummy.json", "dummy.json")
        
        with migrator:
            migrator.session = db_session
            
            # Should handle invalid references gracefully
            migrated_count = migrator.migrate_relationships(relationships_data)
            
            # Should still create the relationship (foreign key constraint will be enforced by DB)
            assert migrated_count == 1
    
    def test_attribute_data_types(self, db_session):
        """Test that attribute data types are preserved."""
        entities_data = [
            {
                "id": "test_entity",
                "name": "Test Entity",
                "primary_classification": "ingredient",
                "classifications": ["test"],
                "attributes": {
                    "string_attr": {"value": "string_value", "source": "test"},
                    "number_attr": {"value": 42, "source": "test"},
                    "boolean_attr": {"value": True, "source": "test"},
                    "list_attr": {"value": ["item1", "item2"], "source": "test"},
                    "dict_attr": {"value": {"key": "value"}, "source": "test"}
                }
            }
        ]
        
        migrator = DataMigrator("dummy.json", "dummy.json")
        
        with migrator:
            migrator.session = db_session
            
            migrated_count = migrator.migrate_entities(entities_data)
            
            assert migrated_count == 1
            
            entity = db_session.query(Entity).filter(Entity.id == "test_entity").first()
            assert entity is not None
            
            # Verify attribute data types
            attrs = entity.attributes
            assert attrs["string_attr"]["value"] == "string_value"
            assert attrs["number_attr"]["value"] == 42
            assert attrs["boolean_attr"]["value"] is True
            assert attrs["list_attr"]["value"] == ["item1", "item2"]
            assert attrs["dict_attr"]["value"] == {"key": "value"}
