"""
Pytest configuration and fixtures for FlavorLab tests.

This module provides shared fixtures for database setup, test clients,
and authentication for all test modules.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, Entity, RelationshipEntity
from app.services.auth import AuthService, create_token_for_user


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    
    This fixture creates a new in-memory SQLite database for each test,
    ensuring complete isolation between tests.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client with database dependency override.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Sample user data for testing.
    
    Returns:
        dict: User registration data
    """
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """
    Create a test user in the database.
    
    Args:
        db_session: Database session
        test_user_data: User data fixture
        
    Returns:
        User: Created user object
    """
    user = AuthService.create_user(
        db=db_session,
        email=test_user_data["email"],
        password=test_user_data["password"],
        username=test_user_data["username"],
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"]
    )
    
    # Mark as verified for testing
    user.is_verified = True
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_user_token(test_user):
    """
    Create a JWT token for the test user.
    
    Args:
        test_user: Test user fixture
        
    Returns:
        str: JWT access token
    """
    return create_token_for_user(test_user)


@pytest.fixture
def authenticated_client(client, test_user_token):
    """
    Create a test client with authentication headers.
    
    Args:
        client: Test client fixture
        test_user_token: JWT token fixture
        
    Returns:
        TestClient: Authenticated test client
    """
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


@pytest.fixture
def admin_user_data():
    """
    Sample admin user data for testing.
    
    Returns:
        dict: Admin user registration data
    """
    return {
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User"
    }


@pytest.fixture
def admin_user(db_session, admin_user_data):
    """
    Create an admin test user in the database.
    
    Args:
        db_session: Database session
        admin_user_data: Admin user data fixture
        
    Returns:
        User: Created admin user object
    """
    user = AuthService.create_user(
        db=db_session,
        email=admin_user_data["email"],
        password=admin_user_data["password"],
        username=admin_user_data["username"],
        first_name=admin_user_data["first_name"],
        last_name=admin_user_data["last_name"]
    )
    
    # Mark as verified and active for testing
    user.is_verified = True
    user.is_active = True
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def admin_token(admin_user):
    """
    Create a JWT token for the admin user.
    
    Args:
        admin_user: Admin user fixture
        
    Returns:
        str: JWT access token
    """
    return create_token_for_user(admin_user)


@pytest.fixture
def admin_client(client, admin_token):
    """
    Create a test client with admin authentication headers.
    
    Args:
        client: Test client fixture
        admin_token: Admin JWT token fixture
        
    Returns:
        TestClient: Admin authenticated test client
    """
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


@pytest.fixture
def sample_entity_data():
    """
    Sample entity data for testing.
    
    Returns:
        dict: Entity creation data
    """
    return {
        "id": "test_entity_1",
        "name": "Test Ingredient",
        "primary_classification": "ingredient",
        "classifications": ["test_category", "sample_ingredient"],
        "attributes": {
            "description": {
                "value": "A test ingredient for unit testing",
                "source": "test",
                "confidence": 5
            },
            "health_outcomes": {
                "value": ["Energy", "Anti-inflammatory"],
                "source": "test",
                "confidence": 4
            }
        }
    }


@pytest.fixture
def sample_entity(db_session, sample_entity_data):
    """
    Create a sample entity in the database.
    
    Args:
        db_session: Database session
        sample_entity_data: Entity data fixture
        
    Returns:
        Entity: Created entity object
    """
    entity = Entity(
        id=sample_entity_data["id"],
        name=sample_entity_data["name"],
        primary_classification=sample_entity_data["primary_classification"],
        classifications=sample_entity_data["classifications"],
        attributes=sample_entity_data["attributes"]
    )
    
    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)
    
    return entity


@pytest.fixture
def sample_relationship_data():
    """
    Sample relationship data for testing.
    
    Returns:
        dict: Relationship creation data
    """
    return {
        "source_id": "test_entity_1",
        "target_id": "test_entity_2",
        "relationship_type": "contains",
        "quantity": "1.5",
        "unit": "g/100g",
        "context": {
            "state": "raw",
            "mechanisms": ["absorption"],
            "params": {"temperature": "room"}
        },
        "uncertainty": {
            "mean": 1.5,
            "sd": 0.2,
            "min": 1.0,
            "max": 2.0
        },
        "source_reference": "test_data",
        "confidence_score": 4
    }


@pytest.fixture
def sample_relationship(db_session, sample_entity, sample_relationship_data):
    """
    Create a sample relationship in the database.
    
    Args:
        db_session: Database session
        sample_entity: Sample entity fixture
        sample_relationship_data: Relationship data fixture
        
    Returns:
        RelationshipEntity: Created relationship object
    """
    # Create target entity
    target_entity = Entity(
        id="test_entity_2",
        name="Test Compound",
        primary_classification="compound",
        classifications=["test_compound"]
    )
    db_session.add(target_entity)
    
    # Create relationship
    relationship = RelationshipEntity(
        source_id=sample_relationship_data["source_id"],
        target_id=sample_relationship_data["target_id"],
        relationship_type=sample_relationship_data["relationship_type"],
        quantity=sample_relationship_data["quantity"],
        unit=sample_relationship_data["unit"],
        context=sample_relationship_data["context"],
        uncertainty=sample_relationship_data["uncertainty"],
        source_reference=sample_relationship_data["source_reference"],
        confidence_score=sample_relationship_data["confidence_score"]
    )
    
    db_session.add(relationship)
    db_session.commit()
    db_session.refresh(relationship)
    
    return relationship


@pytest.fixture
def multiple_entities(db_session):
    """
    Create multiple test entities for testing search and filtering.
    
    Args:
        db_session: Database session
        
    Returns:
        list: List of created entities
    """
    entities_data = [
        {
            "id": "ingredient_1",
            "name": "Turmeric",
            "primary_classification": "ingredient",
            "classifications": ["spice", "anti-inflammatory"],
            "attributes": {
                "health_outcomes": {
                    "value": ["Anti-inflammatory", "Antioxidant"],
                    "source": "research",
                    "confidence": 5
                }
            }
        },
        {
            "id": "ingredient_2",
            "name": "Ginger",
            "primary_classification": "ingredient",
            "classifications": ["spice", "digestive"],
            "attributes": {
                "health_outcomes": {
                    "value": ["Digestive Health", "Anti-inflammatory"],
                    "source": "research",
                    "confidence": 4
                }
            }
        },
        {
            "id": "nutrient_1",
            "name": "Vitamin C",
            "primary_classification": "nutrient",
            "classifications": ["vitamin", "antioxidant"],
            "attributes": {
                "function": {
                    "value": "Immune system support and antioxidant activity",
                    "source": "research",
                    "confidence": 5
                }
            }
        }
    ]
    
    entities = []
    for entity_data in entities_data:
        entity = Entity(**entity_data)
        db_session.add(entity)
        entities.append(entity)
    
    db_session.commit()
    
    for entity in entities:
        db_session.refresh(entity)
    
    return entities


@pytest.fixture
def temp_json_file():
    """
    Create a temporary directory with default-named JSON files used by scripts.
    
    Returns:
        pathlib.Path: Path to entities.json within the temp directory
    """
    import json
    import tempfile
    from pathlib import Path
    
    temp_dir = Path(tempfile.mkdtemp())
    entities_path = temp_dir / "entities.json"
    relationships_path = temp_dir / "entity_relationships.json"
    
    # Minimal entities dataset (2 entities)
    entities_data = {
        "metadata": {
            "total_entities": 2,
            "primary_classifications": {
                "ingredient": 1,
                "nutrient": 1
            }
        },
        "entities": [
            {
                "id": "test_ingredient",
                "name": "Test Ingredient",
                "primary_classification": "ingredient",
                "classifications": ["test"],
                "attributes": {}
            },
            {
                "id": "test_nutrient",
                "name": "Test Nutrient",
                "primary_classification": "nutrient",
                "classifications": ["test"],
                "attributes": {}
            }
        ]
    }
    entities_path.write_text(json.dumps(entities_data), encoding="utf-8")
    
    # Minimal relationships dataset (1 relationship)
    relationships_data = {
        "metadata": {"total_relationships": 1},
        "relationships": [
            {
                "source_id": "test_ingredient",
                "target_id": "test_nutrient",
                "relationship_type": "related_to",
                "confidence_score": 3
            }
        ]
    }
    relationships_path.write_text(json.dumps(relationships_data), encoding="utf-8")
    
    return entities_path


@pytest.fixture(autouse=True)
def cleanup_temp_files(temp_json_file):
    """
    Clean up temporary files after tests.
    
    Args:
        temp_json_file: Path to entities.json created by temp_json_file fixture
    """
    from pathlib import Path
    yield
    try:
        path = Path(temp_json_file)
        base_dir = path.parent
        # Remove files
        for name in ("entities.json", "entity_relationships.json"):
            p = base_dir / name
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
        # Remove directory if empty
        try:
            base_dir.rmdir()
        except Exception:
            pass
    except Exception:
        pass  # Ignore cleanup errors


# Test data constants
TEST_ENTITIES_COUNT = 3
TEST_RELATIONSHIPS_COUNT = 1
TEST_USERS_COUNT = 2  # test_user + admin_user

# API endpoint constants
API_PREFIX = "/api/v1"
ENTITIES_ENDPOINT = f"{API_PREFIX}/entities"
RELATIONSHIPS_ENDPOINT = f"{API_PREFIX}/relationships"
USERS_ENDPOINT = f"{API_PREFIX}/users"
HEALTH_ENDPOINT = f"{API_PREFIX}/health"
FLAVOR_ENDPOINT = f"{API_PREFIX}/flavor"
