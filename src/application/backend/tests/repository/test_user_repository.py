import pytest
from unittest.mock import MagicMock
from app.repositories.user_repository import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    create_user
)
from app.db.models.user import DBUser
from app.db.models.role import DBRole
from app.schemas.db.user import UserCreate


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
        hashed_password="hashed_password_123",
        is_active=True
    )
    user.roles = []
    return user


@pytest.fixture
def mock_user_create():
    """Mock user creation schema."""
    return UserCreate(
        username="newuser",
        email="new@example.com",
        first_name="New",
        last_name="User",
        password="password123"
    )


@pytest.fixture
def mock_role():
    """Mock user role."""
    return DBRole(id=1, name="user", description="Default user role")


class TestUserRepository:

    def test_get_all_users(self, mock_db, mock_user):
        """Test getting all users with pagination."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_user]

        result = get_all_users(mock_db, skip=0, limit=100)

        assert len(result) == 1
        assert result[0].username == "testuser"
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)

    def test_get_all_users_empty(self, mock_db):
        """Test getting all users when database is empty."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = get_all_users(mock_db, skip=0, limit=100)

        assert len(result) == 0

    def test_get_user_by_id_success(self, mock_db, mock_user):
        """Test getting user by ID successfully."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = get_user_by_id(mock_db, user_id=1)

        assert result is not None
        assert result.id == 1
        assert result.username == "testuser"

    def test_get_user_by_id_not_found(self, mock_db):
        """Test getting user by ID when user doesn't exist."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = get_user_by_id(mock_db, user_id=999)

        assert result is None

    def test_get_user_by_username_success(self, mock_db, mock_user):
        """Test getting user by username successfully."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = get_user_by_username(mock_db, username="testuser")

        assert result is not None
        assert result.username == "testuser"

    def test_get_user_by_username_not_found(self, mock_db):
        """Test getting user by username when user doesn't exist."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = get_user_by_username(mock_db, username="nonexistent")

        assert result is None

    def test_get_user_by_email_success(self, mock_db, mock_user):
        """Test getting user by email successfully."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = get_user_by_email(mock_db, email="test@example.com")

        assert result is not None
        assert result.email == "test@example.com"

    def test_get_user_by_email_not_found(self, mock_db):
        """Test getting user by email when user doesn't exist."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = get_user_by_email(mock_db, email="nonexistent@example.com")

        assert result is None

    def test_create_user_success(self, mocker, mock_db, mock_user_create, mock_role):
        """Test creating a new user successfully."""
        # Mock password hashing
        mocker.patch("app.repositories.user_repository.password_hash_context.hash", return_value="hashed_password")

        # Mock role query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_role

        # Mock the created user
        created_user = DBUser(
            id=1,
            username=mock_user_create.username,
            email=mock_user_create.email,
            first_name=mock_user_create.first_name,
            last_name=mock_user_create.last_name,
            hashed_password="hashed_password",
            is_active=True
        )
        created_user.roles = [mock_role]

        # Mock db operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', 1))

        result = create_user(mock_db, mock_user_create)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_user_without_role(self, mocker, mock_db, mock_user_create):
        """Test creating a user when default role doesn't exist."""
        # Mock password hashing
        mocker.patch("app.repositories.user_repository.password_hash_context.hash", return_value="hashed_password")

        # Mock role query returning None
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Mock db operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        result = create_user(mock_db, mock_user_create)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
