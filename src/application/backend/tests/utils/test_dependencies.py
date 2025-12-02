import pytest
from unittest.mock import MagicMock, patch, Mock
from fastapi import HTTPException
from jose import jwt
from app.dependencies import (
    get_db,
    get_current_user_from_access_token,
    get_current_active_user,
)
from app.schemas.db.user import User


class TestGetDb:
    """Test the get_db dependency function."""

    @patch("app.dependencies.SessionLocal")
    def test_get_db_yields_session(self, mock_session_local):
        """Test get_db yields a database session."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()
        db = next(gen)

        assert db == mock_db
        mock_session_local.assert_called_once()

    @patch("app.dependencies.SessionLocal")
    def test_get_db_closes_session(self, mock_session_local):
        """Test get_db closes session after use."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()
        next(gen)

        try:
            next(gen)
        except StopIteration:
            pass

        mock_db.close.assert_called_once()

    @patch("app.dependencies.SessionLocal")
    def test_get_db_closes_session_on_exception(self, mock_session_local):
        """Test get_db closes session even if exception occurs."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()
        next(gen)

        try:
            gen.throw(Exception("Test exception"))
        except Exception:
            pass

        mock_db.close.assert_called_once()


class TestGetCurrentUserFromAccessToken:
    """Test the get_current_user_from_access_token dependency function."""


    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = MagicMock()
        request.cookies = {}
        return request

    @pytest.fixture
    def valid_token(self):
        """Create a valid JWT token."""
        secret_key = "test-secret-key-for-testing-only"
        algorithm = "HS256"
        
        payload = {"sub": "testuser"}
        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @pytest.mark.asyncio
    @patch("app.dependencies.jwt.decode")
    @patch("app.dependencies.get_user_by_username")
    @patch("app.dependencies.convert_db_user_to_user")
    async def test_get_current_user_with_bearer_token(
        self, mock_convert, mock_get_user, mock_jwt_decode, mock_db, mock_request, valid_token
    ):
        """Test getting current user with valid bearer token."""
        from app.db.models.user import DBUser
        
        mock_jwt_decode.return_value = {"sub": "testuser"}
        
        mock_db_user = DBUser(
            id=1,
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        mock_db_user.roles = []
        
        mock_user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            disabled=False,
            roles=[]
        )
        
        mock_get_user.return_value = mock_db_user
        mock_convert.return_value = mock_user

        result = await get_current_user_from_access_token(
            request=mock_request,
            token=valid_token,
            db=mock_db
        )

        assert result == mock_user
        mock_get_user.assert_called_once_with(mock_db, username="testuser")
        mock_convert.assert_called_once_with(mock_db_user)


    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, mock_db, mock_request):
        """Test getting current user with no token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_access_token(
                request=mock_request,
                token=None,
                db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db, mock_request):
        """Test getting current user with invalid token raises exception."""
        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_access_token(
                request=mock_request,
                token=invalid_token,
                db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    @patch("app.dependencies.jwt.decode")
    async def test_get_current_user_token_missing_sub(
        self, mock_jwt_decode, mock_db, mock_request
    ):
        """Test getting current user with token missing 'sub' claim."""
        mock_jwt_decode.return_value = {"other": "data"}
        token = "fake.token.here"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_access_token(
                request=mock_request,
                token=token,
                db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    @patch("app.dependencies.jwt.decode")
    @patch("app.dependencies.get_user_by_username")
    async def test_get_current_user_user_not_found(
        self, mock_get_user, mock_jwt_decode, mock_db, mock_request, valid_token
    ):
        """Test getting current user when user doesn't exist in database."""
        mock_jwt_decode.return_value = {"sub": "testuser"}
        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_access_token(
                request=mock_request,
                token=valid_token,
                db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_get_user.assert_called_once_with(mock_db, username="testuser")

    @pytest.mark.asyncio
    @patch("app.dependencies.jwt.decode")
    async def test_get_current_user_expired_token(
        self, mock_jwt_decode, mock_db, mock_request
    ):
        """Test getting current user with expired token."""
        from jose import JWTError
        
        mock_jwt_decode.side_effect = JWTError("Token has expired")
        expired_token = "expired.token.here"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_access_token(
                request=mock_request,
                token=expired_token,
                db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"


class TestGetCurrentActiveUser:
    """Test the get_current_active_user dependency function."""

    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self):
        """Test getting current active user with active user."""
        current_user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            disabled=False,
            roles=["user"]
        )

        result = await get_current_active_user(current_user=current_user)

        assert result == current_user

    @pytest.mark.asyncio
    async def test_get_current_active_user_disabled(self):
        """Test getting current active user with disabled user raises exception."""
        current_user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            disabled=True,
            roles=["user"]
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=current_user)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Inactive user"

    @pytest.mark.asyncio
    async def test_get_current_active_user_with_roles(self):
        """Test getting current active user with multiple roles."""
        current_user = User(
            username="adminuser",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            disabled=False,
            roles=["user", "admin"]
        )

        result = await get_current_active_user(current_user=current_user)

        assert result == current_user
        assert "admin" in result.roles


class TestSecurityConfig:
    """Test security configuration module."""

    @patch.dict("os.environ", {"ENVIRONMENT": "testing"}, clear=True)
    @patch("app.config.security.boto3")
    def test_skip_aws_in_testing_environment(self, mock_boto3):
        """Test that AWS SSM is not called in testing environment."""
        # Re-import to trigger the module-level code
        import importlib
        import app.config.security as security_module
        importlib.reload(security_module)

        # boto3.client should not be called in testing environment
        mock_boto3.client.assert_not_called()

    @patch.dict("os.environ", {"ENVIRONMENT": "development"}, clear=True)
    @patch("app.config.security.boto3")
    def test_skip_aws_in_development_environment(self, mock_boto3):
        """Test that AWS SSM is not called in development environment."""
        # Re-import to trigger the module-level code
        import importlib
        import app.config.security as security_module
        importlib.reload(security_module)

        # boto3.client should not be called in development environment
        mock_boto3.client.assert_not_called()

    @patch.dict("os.environ", {"ENVIRONMENT": "production", "ACCESS_TOKEN_SECRET_KEY": "fallback-key"}, clear=True)
    @patch("app.config.security.boto3")
    def test_fallback_to_environment_variable_on_aws_failure(self, mock_boto3):
        """Test fallback to environment variable when AWS SSM fails."""
        # Mock AWS SSM to raise an exception
        mock_boto3.client.side_effect = Exception("AWS connection failed")

        # Re-import to trigger the module-level code
        import importlib
        import app.config.security as security_module
        importlib.reload(security_module)

        assert security_module.ACCESS_TOKEN_SECRET_KEY == "fallback-key"

    @patch.dict("os.environ", {"ENVIRONMENT": "testing", "ACCESS_TOKEN_SECRET_KEY": "test-secret"}, clear=True)
    def test_use_environment_variable_in_testing(self):
        """Test that environment variable is used directly in testing."""
        # Re-import to trigger the module-level code
        import importlib
        import app.config.security as security_module
        importlib.reload(security_module)

        assert security_module.ACCESS_TOKEN_SECRET_KEY == "test-secret"

    def test_security_constants_defined(self):
        """Test that security constants are properly defined."""
        from app.config.security import (
            ACCESS_TOKEN_ALGORITHM,
            ACCESS_TOKEN_EXPIRE_MINUTES,
            oauth2_scheme,
            password_hash_context
        )

        assert ACCESS_TOKEN_ALGORITHM == "HS256"
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert oauth2_scheme is not None
        assert password_hash_context is not None

    def test_password_hash_context_configuration(self):
        """Test password hash context is configured with bcrypt."""
        from app.config.security import password_hash_context

        assert "bcrypt" in password_hash_context.schemes()



