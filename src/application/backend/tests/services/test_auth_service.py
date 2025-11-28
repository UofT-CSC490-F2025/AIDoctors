import pytest
from datetime import timedelta
from unittest.mock import MagicMock
from jose import jwt
from app.services.auth_service import (
    create_access_token,
    authenticate_user
)
from app.db.models.user import DBUser


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def mock_user():
    """Mock database user."""
    user = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="$2b$12$KIXqF3YqJx5vZqZ5vZqZ5eZqZ5vZqZ5vZqZ5vZqZ5vZqZ5vZqZ5vZ",  # hashed "password123"
        is_active=True
    )
    user.roles = []
    return user


class TestAuthService:

    def test_create_access_token_with_expiry(self, mocker):
        """Test creating access token with custom expiry."""
        # Mock the secret key
        mocker.patch("app.services.auth_service.ACCESS_TOKEN_SECRET_KEY", "test-secret-key")
        
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)

        token = create_access_token(data, expires_delta)

        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token contents
        # Note: We skip signature verification in tests
        decoded = jwt.decode(token, key="", options={"verify_signature": False})
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded

    def test_create_access_token_default_expiry(self, mocker):
        """Test creating access token with default expiry."""
        # Mock the secret key
        mocker.patch("app.services.auth_service.ACCESS_TOKEN_SECRET_KEY", "test-secret-key")
        
        data = {"sub": "testuser"}

        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        
        decoded = jwt.decode(token, key="", options={"verify_signature": False})
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded

    def test_create_access_token_with_additional_data(self, mocker):
        """Test creating access token with additional claims."""
        # Mock the secret key
        mocker.patch("app.services.auth_service.ACCESS_TOKEN_SECRET_KEY", "test-secret-key")
        
        data = {"sub": "testuser", "role": "admin", "email": "test@example.com"}
        expires_delta = timedelta(minutes=15)

        token = create_access_token(data, expires_delta)

        decoded = jwt.decode(token, key="", options={"verify_signature": False})
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "test@example.com"

    def test_authenticate_user_success(self, mocker, mock_db, mock_user):
        """Test successful user authentication."""
        # Mock get_user_by_username
        mocker.patch("app.services.auth_service.get_user_by_username", return_value=mock_user)
        
        # Mock password verification
        mocker.patch("app.services.auth_service.password_hash_context.verify", return_value=True)

        result = authenticate_user(mock_db, "testuser", "password123")

        assert result is not False
        assert result.username == "testuser"

    def test_authenticate_user_wrong_password(self, mocker, mock_db, mock_user):
        """Test authentication with wrong password."""
        # Mock get_user_by_username
        mocker.patch("app.services.auth_service.get_user_by_username", return_value=mock_user)
        
        # Mock password verification to fail
        mocker.patch("app.services.auth_service.password_hash_context.verify", return_value=False)

        result = authenticate_user(mock_db, "testuser", "wrongpassword")

        assert result is False

    def test_authenticate_user_not_found(self, mocker, mock_db):
        """Test authentication with non-existent user."""
        # Mock get_user_by_username to return None
        mocker.patch("app.services.auth_service.get_user_by_username", return_value=None)

        result = authenticate_user(mock_db, "nonexistent", "password123")

        assert result is False

    def test_authenticate_user_empty_credentials(self, mocker, mock_db):
        """Test authentication with empty credentials."""
        # Mock get_user_by_username to return None
        mocker.patch("app.services.auth_service.get_user_by_username", return_value=None)

        result = authenticate_user(mock_db, "", "")

        assert result is False
