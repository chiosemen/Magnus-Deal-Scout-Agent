# tests/test_api.py

import pytest
from fastapi import status


class TestHealth:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check returns 200"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuthentication:
    """Test authentication endpoints"""

    def test_register_user(self, client, test_user_data):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register again with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, test_user_data):
        """Test getting current user info"""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]


class TestSearches:
    """Test search endpoints"""

    @pytest.fixture
    def auth_headers(self, client, test_user_data):
        """Get authentication headers"""
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_search(self, client, auth_headers, test_search_data):
        """Test creating a search"""
        response = client.post(
            "/api/v1/searches",
            json=test_search_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == test_search_data["name"]
        assert data["keywords"] == test_search_data["keywords"]
        assert "id" in data

    def test_get_searches(self, client, auth_headers, test_search_data):
        """Test getting all searches"""
        # Create a search
        client.post("/api/v1/searches", json=test_search_data, headers=auth_headers)

        # Get searches
        response = client.get("/api/v1/searches", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_delete_search(self, client, auth_headers, test_search_data):
        """Test deleting a search"""
        # Create search
        create_response = client.post(
            "/api/v1/searches",
            json=test_search_data,
            headers=auth_headers
        )
        search_id = create_response.json()["id"]

        # Delete search
        response = client.delete(
            f"/api/v1/searches/{search_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify deleted
        get_response = client.get(
            f"/api/v1/searches/{search_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
