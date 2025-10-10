"""
Tests for user API endpoints.

This module tests user profile management, password changes,
and user administration endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserProfile:
    """Test user profile endpoints."""
    
    def test_get_current_user_profile(self, authenticated_client, test_user):
        """Test getting current user profile."""
        response = authenticated_client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["is_active"] is True
        assert data["is_verified"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data
    
    def test_get_current_user_profile_unauthenticated(self, client):
        """Test getting user profile without authentication."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_update_user_profile(self, authenticated_client, test_user):
        """Test updating user profile."""
        update_data = {
            "username": "updated_user",
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "updated_user"
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["email"] == "test@example.com"  # Email should not change
    
    def test_update_user_profile_partial(self, authenticated_client, test_user):
        """Test partial profile update."""
        update_data = {
            "first_name": "Partial"
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["first_name"] == "Partial"
        assert data["last_name"] == "User"  # Should remain unchanged
        assert data["username"] == "testuser"  # Should remain unchanged
    
    def test_update_user_profile_duplicate_username(self, authenticated_client, test_user, db_session):
        """Test updating profile with duplicate username."""
        # Create another user
        from app.services.auth import AuthService
        other_user = AuthService.create_user(
            db=db_session,
            email="other@example.com",
            password="OtherPass123",
            username="other_user"
        )
        db_session.commit()
        
        # Try to update current user with other user's username
        update_data = {
            "username": "other_user"
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Username already taken" in data["detail"]
    
    def test_update_user_profile_same_username(self, authenticated_client, test_user):
        """Test updating profile with same username (should succeed)."""
        update_data = {
            "username": "testuser"  # Same as current username
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_update_user_profile_invalid_data(self, authenticated_client, test_user):
        """Test updating profile with invalid data."""
        update_data = {
            "username": "ab"  # Too short
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_update_user_profile_unauthenticated(self, client):
        """Test updating profile without authentication."""
        update_data = {
            "first_name": "Unauthorized"
        }
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]


class TestPasswordChange:
    """Test password change functionality."""
    
    def test_change_password_success(self, authenticated_client, test_user):
        """Test successful password change."""
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NewPassword123"
        }
        
        response = authenticated_client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "Password changed successfully" in data["message"]
    
    def test_change_password_wrong_current(self, authenticated_client, test_user):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "WrongPassword123",
            "new_password": "NewPassword123"
        }
        
        response = authenticated_client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Current password is incorrect" in data["detail"]
    
    def test_change_password_weak_new_password(self, authenticated_client, test_user):
        """Test password change with weak new password."""
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "weak"  # Too weak
        }
        
        response = authenticated_client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "String should have at least 8 characters" in str(data)
    
    def test_change_password_missing_fields(self, authenticated_client, test_user):
        """Test password change with missing fields."""
        password_data = {
            "current_password": "TestPassword123"
            # Missing new_password
        }
        
        response = authenticated_client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_change_password_unauthenticated(self, client):
        """Test password change without authentication."""
        password_data = {
            "current_password": "SomePassword123",
            "new_password": "NewPassword123"
        }
        
        response = client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]


class TestAccountDeactivation:
    """Test account deactivation functionality."""
    
    def test_deactivate_account(self, authenticated_client, test_user):
        """Test account deactivation."""
        response = authenticated_client.post("/api/v1/users/me/deactivate")
        
        assert response.status_code == 200
        data = response.json()
        assert "Account deactivated successfully" in data["message"]
    
    def test_deactivate_account_unauthenticated(self, client):
        """Test account deactivation without authentication."""
        response = client.post("/api/v1/users/me/deactivate")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]


class TestUserStatistics:
    """Test user statistics endpoint."""
    
    def test_get_user_statistics(self, admin_client, test_user, admin_user):
        """Test getting user statistics."""
        response = admin_client.get("/api/v1/users/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_users" in data
        assert "active_users" in data
        assert "verified_users" in data
        assert "recent_registrations" in data
        assert "last_updated" in data
        
        # Should have at least 2 users (test_user + admin_user)
        assert data["total_users"] >= 2
        assert data["active_users"] >= 2
        assert data["verified_users"] >= 2
    
    def test_get_user_statistics_unauthenticated(self, client):
        """Test getting user statistics without authentication."""
        response = client.get("/api/v1/users/stats")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_get_user_statistics_unverified_user(self, authenticated_client, test_user):
        """Test getting user statistics with unverified user."""
        # Make user unverified
        from app.database import get_db
        db = next(get_db())
        test_user.is_verified = False
        db.commit()
        
        response = authenticated_client.get("/api/v1/users/stats")
        
        assert response.status_code == 400
        data = response.json()
        assert "User not verified" in data["detail"]


class TestUserManagement:
    """Test user management endpoints (admin only)."""
    
    def test_get_user_by_id(self, admin_client, test_user):
        """Test getting user by ID."""
        response = admin_client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
    
    def test_get_user_by_id_not_found(self, admin_client):
        """Test getting non-existent user by ID."""
        response = admin_client.get("/api/v1/users/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "User with ID '99999' not found" in data["detail"]
    
    def test_get_user_by_id_unauthenticated(self, client, test_user):
        """Test getting user by ID without authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_get_user_by_id_unverified_user(self, authenticated_client, test_user):
        """Test getting user by ID with unverified user."""
        # Make user unverified
        from app.database import get_db
        db = next(get_db())
        test_user.is_verified = False
        db.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 400
        data = response.json()
        assert "User not verified" in data["detail"]
    
    def test_activate_user_account(self, admin_client, test_user, db_session):
        """Test activating user account."""
        # Deactivate user first
        test_user.is_active = False
        db_session.commit()
        
        response = admin_client.put(f"/api/v1/users/{test_user.id}/activate")
        
        assert response.status_code == 200
        data = response.json()
        assert f"User account '{test_user.id}' activated successfully" in data["message"]
        
        # Verify user is now active
        db_session.refresh(test_user)
        assert test_user.is_active is True
    
    def test_verify_user_account(self, admin_client, test_user, db_session):
        """Test verifying user account."""
        # Make user unverified first
        test_user.is_verified = False
        db_session.commit()
        
        response = admin_client.put(f"/api/v1/users/{test_user.id}/verify")
        
        assert response.status_code == 200
        data = response.json()
        assert f"User account '{test_user.id}' verified successfully" in data["message"]
        
        # Verify user is now verified
        db_session.refresh(test_user)
        assert test_user.is_verified is True
    
    def test_activate_nonexistent_user(self, admin_client):
        """Test activating non-existent user."""
        response = admin_client.put("/api/v1/users/99999/activate")
        
        assert response.status_code == 404
        data = response.json()
        assert "User with ID '99999' not found" in data["detail"]
    
    def test_verify_nonexistent_user(self, admin_client):
        """Test verifying non-existent user."""
        response = admin_client.put("/api/v1/users/99999/verify")
        
        assert response.status_code == 404
        data = response.json()
        assert "User with ID '99999' not found" in data["detail"]


class TestUserPreferences:
    """Test user preferences functionality."""
    
    def test_update_user_preferences(self, authenticated_client, test_user):
        """Test updating user preferences."""
        preferences = {
            "dietary_restrictions": ["vegetarian"],
            "health_goals": ["weight_loss", "energy"],
            "flavor_preferences": {
                "spicy": "moderate",
                "sweet": "low"
            },
            "notification_settings": {
                "email": True,
                "push": False
            }
        }
        
        update_data = {
            "preferences": preferences
        }
        
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Preferences should be updated
        assert data["preferences"] == preferences
    
    def test_update_user_preferences_partial(self, authenticated_client, test_user):
        """Test partial preferences update."""
        initial_preferences = {
            "dietary_restrictions": ["vegetarian"],
            "health_goals": ["weight_loss"]
        }
        
        # Set initial preferences
        update_data = {"preferences": initial_preferences}
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 200
        
        # Update only one preference
        updated_preferences = {
            "dietary_restrictions": ["vegetarian", "gluten-free"],
            "health_goals": ["weight_loss"]  # Keep existing
        }
        
        update_data = {"preferences": updated_preferences}
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["preferences"] == updated_preferences
    
    def test_clear_user_preferences(self, authenticated_client, test_user):
        """Test clearing user preferences."""
        # Set some preferences first
        preferences = {"theme": "dark"}
        update_data = {"preferences": preferences}
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 200
        
        # Clear preferences
        update_data = {"preferences": None}
        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["preferences"] is None
