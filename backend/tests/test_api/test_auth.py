"""
Tests for authentication API endpoints.

This module tests the user registration and login functionality,
JWT token generation, and authentication flow.
"""

import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.models.user import User
import jwt
from datetime import datetime


class TestUserRegistration:
    """Test user registration endpoints."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data
    
    def test_register_user_minimal_data(self, client):
        """Test user registration with minimal required data."""
        user_data = {
            "email": "minimal@example.com",
            "password": "MinimalPass123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "minimal@example.com"
        assert data["username"] is None
        assert data["first_name"] is None
        assert data["last_name"] is None
    
    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": "test@example.com",  # Same as test_user
            "password": "AnotherPassword123",
            "username": "different_user"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]
    
    def test_register_user_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "email": "different@example.com",
            "password": "AnotherPassword123",
            "username": "testuser"  # Same as test_user
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Username already taken" in data["detail"]
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "ValidPassword123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "email": "weak@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "String should have at least 8 characters" in str(data)
    
    def test_register_user_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        user_data = {
            "username": "incomplete"
            # Missing email and password
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoints."""
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful user login."""
        response = client.post(
            f"{settings.api_prefix}/users/login",
            data={"username": test_user.email, "password": "TestPassword123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect email or password" in data["detail"]
    
    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with an invalid password."""
        response = client.post(
            f"{settings.api_prefix}/users/login",
            data={"username": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client: TestClient, test_user_data: dict):
        """Test login for an inactive user."""
        # Create an inactive user
        response = client.post(
            f"{settings.api_prefix}/users/register",
            json={**test_user_data, "is_active": False},
        )
        assert response.status_code == 200
        
        # Attempt to log in
        response = client.post(
            f"{settings.api_prefix}/users/login",
            data={"username": test_user_data["email"], "password": test_user_data["password"]},
        )
        assert response.status_code == 401
    
    def test_login_invalid_data_format(self, client):
        """Test login with invalid data format."""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == 422  # Validation error


class TestJWTToken:
    """Test JWT token functionality."""
    
    def test_token_structure(self, client, test_user):
        """Test JWT token structure and content."""
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        data = response.json()
        
        token = data["access_token"]
        
        # Token should be a string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should have three parts (header.payload.signature)
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_token_expiration(self, client: TestClient, test_user: User):
        """Test that the JWT token expires correctly."""
        # Use existing test user created by fixture
        login_data = {"username": test_user.email, "password": "TestPassword123"}
        response = client.post(
            f"{settings.api_prefix}/users/login",
            data=login_data,
        )
        assert response.status_code == 200
        token_data = response.json()
        token = token_data.get("access_token")
        
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert "exp" in decoded_token
        assert decoded_token["exp"] > datetime.now(UTC.utc).timestamp()

    def test_token_usage(self, authenticated_client: TestClient):
        """Test using the token to access a protected endpoint."""
        response = authenticated_client.get(f"{settings.api_prefix}/users/me")
        assert response.status_code == 200
        assert "email" in response.json()
    
    def test_invalid_token(self, client):
        """Test request with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Could not validate credentials" in data["detail"]
    
    def test_malformed_token(self, client):
        """Test request with malformed token."""
        headers = {"Authorization": "Bearer not.a.valid.jwt.token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Could not validate credentials" in data["detail"]
    
    def test_missing_token(self, client):
        """Test request without token."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    def test_wrong_token_format(self, client):
        """Test request with wrong token format."""
        headers = {"Authorization": "Basic some_basic_auth"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, client):
        """Test complete registration -> login -> authenticated request flow."""
        # Step 1: Register user
        user_data = {
            "email": "flow@example.com",
            "password": "FlowPassword123",
            "username": "flowuser",
            "first_name": "Flow",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 200
        
        # Step 2: Login user
        login_data = {
            "email": "flow@example.com",
            "password": "FlowPassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        token = data["access_token"]
        
        # Step 3: Use token for authenticated request
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "flow@example.com"
        assert user_data["username"] == "flowuser"
    
    def test_token_persistence(self, client, test_user):
        """Test that token works across multiple requests."""
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        data = response.json()
        token = data["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple authenticated requests
        for _ in range(3):
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 200
    
    def test_logout_behavior(self, client, test_user):
        """Test logout behavior (token should become invalid)."""
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        data = response.json()
        token = data["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Token should work initially
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        
        # Note: In a real implementation, you might have a logout endpoint
        # that invalidates the token. For now, we just test that the token
        # continues to work until it expires naturally.
        
        # Token should still work (until expiration)
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
