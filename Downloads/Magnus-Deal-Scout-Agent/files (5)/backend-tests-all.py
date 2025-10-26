# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html


# tests/__init__.py

# Empty file to make tests a package


# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with test database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_search_data():
    """Test search data"""
    return {
        "name": "Test Search",
        "keywords": "vintage camera",
        "marketplaces": ["ebay", "gumtree"],
        "min_price": 50.0,
        "max_price": 500.0,
        "check_interval_minutes": 60
    }


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
        assert "items" in data
        assert len(data["items"]) > 0
    
    def test_get_search_by_id(self, client, auth_headers, test_search_data):
        """Test getting a specific search"""
        # Create search
        create_response = client.post(
            "/api/v1/searches",
            json=test_search_data,
            headers=auth_headers
        )
        search_id = create_response.json()["id"]
        
        # Get search
        response = client.get(f"/api/v1/searches/{search_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == search_id
    
    def test_update_search(self, client, auth_headers, test_search_data):
        """Test updating a search"""
        # Create search
        create_response = client.post(
            "/api/v1/searches",
            json=test_search_data,
            headers=auth_headers
        )
        search_id = create_response.json()["id"]
        
        # Update search
        update_data = {"name": "Updated Search Name"}
        response = client.put(
            f"/api/v1/searches/{search_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
    
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


class TestDashboard:
    """Test dashboard endpoints"""
    
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
    
    def test_get_dashboard_stats(self, client, auth_headers):
        """Test getting dashboard statistics"""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_searches" in data
        assert "active_searches" in data
        assert "total_listings" in data
        assert "new_listings_today" in data
        assert "saved_listings" in data
