import pytest
from unittest.mock import MagicMock
from app.repositories.role_repository import (
    get_role_by_name,
    create_role
)
from app.db.models.role import DBRole


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def mock_role():
    """Mock database role."""
    return DBRole(id=1, name="admin", description="Administrator role")


class TestRoleRepository:

    def test_get_role_by_name_success(self, mock_db, mock_role):
        """Test getting role by name successfully."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_role

        result = get_role_by_name(mock_db, name="admin")

        assert result is not None
        assert result.name == "admin"
        assert result.description == "Administrator role"

    def test_get_role_by_name_not_found(self, mock_db):
        """Test getting role by name when role doesn't exist."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = get_role_by_name(mock_db, name="nonexistent")

        assert result is None

    def test_create_role_success(self, mock_db):
        """Test creating a new role successfully."""
        # Mock db operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        result = create_role(mock_db, name="moderator", description="Moderator role")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_role_without_description(self, mock_db):
        """Test creating a role without description."""
        # Mock db operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        result = create_role(mock_db, name="user")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
