import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.db.user import User
from app.db.models.user import DBUser
from app.db.models.role import DBRole
from app.dependencies import get_current_active_user


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_user_create():
    """Mock user creation data fixture"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "SecurePassword123!"
    }


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


@pytest.fixture
def mock_user():
    """Mock user fixture"""
    return User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        disabled=False,
        roles=["user"]
    )


@pytest.fixture
def client_with_auth(mock_user):
    """Test client with authentication override"""
    def override_get_current_active_user():
        return mock_user
    
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    client = TestClient(app)
    yield client
    # Clean up after test
    app.dependency_overrides.clear()

class TestAuth:

    def test_register_success(self, mocker, client, mock_user_create, mock_db_user):
        """Test registration endpoint success"""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user", return_value=mock_db_user)

        response = client.post("/users/register", json=mock_user_create)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert response.json()["email"] == "test@example.com"

    def test_register_failure_email_exists(self, mocker, client, mock_user_create, mock_db_user):
        """Test registration endpoint failure - email exists"""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=mock_db_user)
        mocker.patch("app.routers.users.create_user", return_value=mock_db_user)

        response = client.post("/users/register", json=mock_user_create)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"
    
    def test_register_failure_username_exists(self, mocker, client, mock_user_create, mock_db_user):
        """Test registration endpoint failure - username exists"""
        mocker.patch("app.routers.users.get_user_by_username", return_value=mock_db_user)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user", return_value=mock_db_user)

        response = client.post("/users/register", json=mock_user_create)
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

    def test_get_current_user_success(self, client_with_auth, mock_user):
        """Test get current user endpoint success"""
        response = client_with_auth.get("/users/me")
        assert response.status_code == 200
        assert response.json()["username"] == mock_user.username
        assert response.json()["email"] == mock_user.email
    
    def test_get_current_user_unauthorized(self, client):
        """Test get current user endpoint without authentication"""
        response = client.get("/users/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

