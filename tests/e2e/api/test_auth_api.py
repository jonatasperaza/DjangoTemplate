import json

import pytest
from django.test import Client


@pytest.mark.django_db
class TestAuthAPI:
    """E2E tests for auth endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = Client()

    def test_health_check(self):
        """Health endpoint should return 200."""
        response = self.client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_register_success(self):
        """Registration should create user and return 201."""
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "newuser@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["email"] == "newuser@example.com"

    def test_register_invalid_password(self):
        """Registration with weak password should fail."""
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "newuser@example.com",
                    "password": "weak",
                    "password_confirm": "weak",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_register_duplicate_email(self):
        """Registration with existing email should fail."""
        # Register first user
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "existing@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        # Try to register again
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "existing@example.com",
                    "password": "SecurePass456",
                    "password_confirm": "SecurePass456",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 409

    def test_login_success(self):
        """Login should return tokens in cookies."""
        # Register user first
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        # Login
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "access_expires_in" in data

        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_invalid_credentials(self):
        """Login with wrong password should fail."""
        # Register user
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        # Login with wrong password
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "WrongPass123",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_logout(self):
        """Logout should clear cookies."""
        # Register and login
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        # Logout
        response = self.client.post("/api/auth/logout")

        assert response.status_code == 200

    def test_me_authenticated(self):
        """Authenticated user should get their info."""
        # Register and login
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "user@example.com",
                    "password": "SecurePass123",
                }
            ),
            content_type="application/json",
        )

        # Get current user
        response = self.client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@example.com"

    def test_me_unauthenticated(self):
        """Unauthenticated request to /me should fail."""
        response = self.client.get("/api/auth/me")

        assert response.status_code == 401
