import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models.user import DBUser
from app.db.models.role import DBRole


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_user():
    """Mock database user fixture"""
    user = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password",
        is_active=True
    )
    # Mock the roles relationship
    role = DBRole(id=1, name="user")
    user.roles = [role]
    return user


class TestAuthRouter:
    
    def test_login_success(self, mocker, client, mock_db_user):
        """Test login endpoint success"""
        # Mock at the router level where it's imported
        mocker.patch("app.routers.auth.authenticate_user", return_value=mock_db_user)
        mocker.patch("app.routers.auth.create_access_token", return_value="mock_token")

        response = client.post("/api/auth/token", data={"username": "testuser", "password": "testpassword"})
        assert response.status_code == 200
        assert response.json()["access_token"] == "mock_token"
        assert response.json()["token_type"] == "bearer"

    def test_login_failure(self, mocker, client):
        """Test login endpoint failure"""
        # Mock at the router level where it's imported
        mocker.patch("app.routers.auth.authenticate_user", return_value=None)
        
        response = client.post("/api/auth/token", data={"username": "testuser", "password": "wrongpassword"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_logout_success(self, client):
        """Test logout endpoint success"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json()["detail"] == "Successfully logged out."