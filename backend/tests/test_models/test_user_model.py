"""
Tests for the User model.

This module tests the SQLAlchemy User model functionality including
user creation, authentication, and profile management.
"""

import pytest
import json
from datetime import datetime

from app.models import User


class TestUserModel:
    """Test the User model."""
    
    def test_user_creation(self, db_session):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            first_name="Test",
            last_name="User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.last_login is None
    
    def test_user_creation_minimal(self, db_session):
        """Test user creation with minimal required fields."""
        user = User(
            email="minimal@example.com",
            hashed_password="hashed_password_123"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.email == "minimal@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_user_with_preferences(self, db_session):
        """Test user creation with preferences."""
        preferences = {
            "dietary_restrictions": ["vegetarian"],
            "health_goals": ["weight_loss", "energy"],
            "flavor_preferences": {
                "spicy": "moderate",
                "sweet": "low"
            }
        }
        
        user = User(
            email="prefs@example.com",
            hashed_password="hashed_password_123",
            preferences=json.dumps(preferences)
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.preferences == json.dumps(preferences)
    
    def test_get_full_name(self, db_session):
        """Test getting user's full name."""
        # User with both first and last name
        user1 = User(
            email="full@example.com",
            hashed_password="hashed_password_123",
            first_name="John",
            last_name="Doe"
        )
        assert user1.get_full_name() == "John Doe"
        
        # User with only first name
        user2 = User(
            email="first@example.com",
            hashed_password="hashed_password_123",
            first_name="Jane"
        )
        assert user2.get_full_name() == "Jane"
        
        # User with only last name
        user3 = User(
            email="last@example.com",
            hashed_password="hashed_password_123",
            last_name="Smith"
        )
        assert user3.get_full_name() == "Smith"
        
        # User with username only
        user4 = User(
            email="username@example.com",
            hashed_password="hashed_password_123",
            username="johndoe"
        )
        assert user4.get_full_name() == "johndoe"
        
        # User with email only
        user5 = User(
            email="emailonly@example.com",
            hashed_password="hashed_password_123"
        )
        assert user5.get_full_name() == "emailonly"
    
    def test_is_authenticated(self, db_session):
        """Test user authentication status."""
        # Active and verified user
        user1 = User(
            email="active@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            is_verified=True
        )
        assert user1.is_authenticated() is True
        
        # Active but not verified user
        user2 = User(
            email="unverified@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            is_verified=False
        )
        assert user2.is_authenticated() is False
        
        # Verified but inactive user
        user3 = User(
            email="inactive@example.com",
            hashed_password="hashed_password_123",
            is_active=False,
            is_verified=True
        )
        assert user3.is_authenticated() is False
        
        # Neither active nor verified user
        user4 = User(
            email="neither@example.com",
            hashed_password="hashed_password_123",
            is_active=False,
            is_verified=False
        )
        assert user4.is_authenticated() is False
    
    def test_update_last_login(self, db_session):
        """Test updating last login timestamp."""
        user = User(
            email="login@example.com",
            hashed_password="hashed_password_123"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        initial_login = user.last_login
        assert initial_login is None
        
        # Update last login
        user.update_last_login()
        db_session.commit()
        db_session.refresh(user)
        
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
    
    def test_to_dict_basic(self, db_session):
        """Test converting user to dictionary (basic info)."""
        user = User(
            email="dict@example.com",
            username="dictuser",
            hashed_password="hashed_password_123",
            first_name="Dict",
            last_name="User",
            is_active=True,
            is_verified=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        user_dict = user.to_dict(include_sensitive=False)
        
        assert user_dict["email"] == "dict@example.com"
        assert user_dict["username"] == "dictuser"
        assert user_dict["first_name"] == "Dict"
        assert user_dict["last_name"] == "User"
        assert user_dict["is_active"] is True
        assert user_dict["is_verified"] is True
        assert "hashed_password" not in user_dict
        assert "preferences" not in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
    
    def test_to_dict_sensitive(self, db_session):
        """Test converting user to dictionary (including sensitive info)."""
        preferences = {"theme": "dark"}
        user = User(
            email="sensitive@example.com",
            hashed_password="hashed_password_123",
            preferences=json.dumps(preferences)
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        user_dict = user.to_dict(include_sensitive=True)
        
        assert user_dict["email"] == "sensitive@example.com"
        assert user_dict["hashed_password"] == "hashed_password_123"
        assert user_dict["preferences"] == json.dumps(preferences)
    
    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            email="repr@example.com",
            username="repruser",
            hashed_password="hashed_password_123"
        )
        
        repr_str = repr(user)
        assert "repr@example.com" in repr_str
        assert "repruser" in repr_str


class TestUserValidation:
    """Test user validation and constraints."""
    
    def test_email_uniqueness(self, db_session):
        """Test email uniqueness constraint."""
        user1 = User(
            email="unique@example.com",
            hashed_password="hashed_password_123"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password="another_password"
        )
        db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db_session.commit()
    
    def test_username_uniqueness(self, db_session):
        """Test username uniqueness constraint."""
        user1 = User(
            email="user1@example.com",
            username="unique_username",
            hashed_password="hashed_password_123"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same username
        user2 = User(
            email="user2@example.com",
            username="unique_username",
            hashed_password="another_password"
        )
        db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db_session.commit()
    
    def test_username_can_be_null(self, db_session):
        """Test that username can be null for multiple users."""
        user1 = User(
            email="user1@example.com",
            hashed_password="hashed_password_123"
        )
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed_password_123"
        )
        
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Both users should be created successfully
        users = db_session.query(User).all()
        assert len(users) == 2
        assert users[0].username is None
        assert users[1].username is None


class TestUserQueries:
    """Test user querying functionality."""
    
    def test_query_by_email(self, db_session):
        """Test querying users by email."""
        users_data = [
            ("user1@example.com", "user1"),
            ("user2@example.com", "user2"),
            ("user3@example.com", "user3")
        ]
        
        for email, username in users_data:
            user = User(
                email=email,
                username=username,
                hashed_password="hashed_password_123"
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query by email
        user = db_session.query(User).filter(User.email == "user2@example.com").first()
        assert user is not None
        assert user.username == "user2"
    
    def test_query_by_username(self, db_session):
        """Test querying users by username."""
        users_data = [
            ("user1@example.com", "alice"),
            ("user2@example.com", "bob"),
            ("user3@example.com", "charlie")
        ]
        
        for email, username in users_data:
            user = User(
                email=email,
                username=username,
                hashed_password="hashed_password_123"
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query by username
        user = db_session.query(User).filter(User.username == "bob").first()
        assert user is not None
        assert user.email == "user2@example.com"
    
    def test_query_active_users(self, db_session):
        """Test querying active users."""
        users_data = [
            ("active1@example.com", True),
            ("inactive@example.com", False),
            ("active2@example.com", True)
        ]
        
        for email, is_active in users_data:
            user = User(
                email=email,
                hashed_password="hashed_password_123",
                is_active=is_active
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query active users
        active_users = db_session.query(User).filter(User.is_active == True).all()
        assert len(active_users) == 2
        
        # Query inactive users
        inactive_users = db_session.query(User).filter(User.is_active == False).all()
        assert len(inactive_users) == 1
    
    def test_query_verified_users(self, db_session):
        """Test querying verified users."""
        users_data = [
            ("verified1@example.com", True),
            ("unverified@example.com", False),
            ("verified2@example.com", True)
        ]
        
        for email, is_verified in users_data:
            user = User(
                email=email,
                hashed_password="hashed_password_123",
                is_verified=is_verified
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query verified users
        verified_users = db_session.query(User).filter(User.is_verified == True).all()
        assert len(verified_users) == 2
        
        # Query unverified users
        unverified_users = db_session.query(User).filter(User.is_verified == False).all()
        assert len(unverified_users) == 1


class TestUserPreferences:
    """Test user preferences functionality."""
    
    def test_preferences_json_serialization(self, db_session):
        """Test JSON serialization of preferences."""
        preferences = {
            "dietary_restrictions": ["vegetarian", "gluten-free"],
            "health_goals": ["weight_loss", "energy", "sleep"],
            "flavor_preferences": {
                "spicy": "moderate",
                "sweet": "low",
                "sour": "high"
            },
            "notification_settings": {
                "email": True,
                "push": False
            }
        }
        
        user = User(
            email="prefs@example.com",
            hashed_password="hashed_password_123",
            preferences=json.dumps(preferences)
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify preferences are stored as JSON string
        assert isinstance(user.preferences, str)
        
        # Parse and verify content
        parsed_prefs = json.loads(user.preferences)
        assert parsed_prefs == preferences
        assert parsed_prefs["dietary_restrictions"] == ["vegetarian", "gluten-free"]
        assert parsed_prefs["flavor_preferences"]["spicy"] == "moderate"
    
    def test_preferences_update(self, db_session):
        """Test updating user preferences."""
        initial_prefs = {"theme": "light"}
        user = User(
            email="update@example.com",
            hashed_password="hashed_password_123",
            preferences=json.dumps(initial_prefs)
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Update preferences
        updated_prefs = {"theme": "dark", "language": "en"}
        user.preferences = json.dumps(updated_prefs)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify update
        parsed_prefs = json.loads(user.preferences)
        assert parsed_prefs == updated_prefs
        assert parsed_prefs["theme"] == "dark"
        assert parsed_prefs["language"] == "en"
