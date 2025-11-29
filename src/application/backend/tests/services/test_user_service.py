import pytest
from app.services.user_service import convert_db_user_to_user
from app.db.models.user import DBUser
from app.db.models.role import DBRole
from app.schemas.db.user import User


@pytest.fixture
def mock_db_user():
    """Mock database user with roles."""
    user = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password_123",
        is_active=True
    )
    role1 = DBRole(id=1, name="user", description="Default user role")
    role2 = DBRole(id=2, name="admin", description="Administrator role")
    user.roles = [role1, role2]
    return user


@pytest.fixture
def mock_db_user_inactive():
    """Mock inactive database user."""
    user = DBUser(
        id=2,
        username="inactiveuser",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        hashed_password="hashed_password_456",
        is_active=False
    )
    user.roles = []
    return user


class TestUserService:

    def test_convert_db_user_to_user_active(self, mock_db_user):
        """Test converting active database user to Pydantic user."""
        result = convert_db_user_to_user(mock_db_user)

        assert isinstance(result, User)
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.first_name == "Test"
        assert result.last_name == "User"
        assert result.disabled is False  # is_active=True -> disabled=False
        assert len(result.roles) == 2
        assert "user" in result.roles
        assert "admin" in result.roles

    def test_convert_db_user_to_user_inactive(self, mock_db_user_inactive):
        """Test converting inactive database user to Pydantic user."""
        result = convert_db_user_to_user(mock_db_user_inactive)

        assert isinstance(result, User)
        assert result.username == "inactiveuser"
        assert result.email == "inactive@example.com"
        assert result.disabled is True  # is_active=False -> disabled=True
        assert len(result.roles) == 0

    def test_convert_db_user_to_user_no_roles(self):
        """Test converting database user with no roles."""
        user = DBUser(
            id=3,
            username="noroleuser",
            email="norole@example.com",
            first_name="No",
            last_name="Role",
            hashed_password="hashed_password_789",
            is_active=True
        )
        user.roles = []

        result = convert_db_user_to_user(user)

        assert isinstance(result, User)
        assert result.username == "noroleuser"
        assert result.disabled is False
        assert len(result.roles) == 0

    def test_convert_db_user_preserves_all_fields(self, mock_db_user):
        """Test that all fields are correctly preserved during conversion."""
        result = convert_db_user_to_user(mock_db_user)

        # Verify all fields match
        assert result.username == mock_db_user.username
        assert result.email == mock_db_user.email
        assert result.first_name == mock_db_user.first_name
        assert result.last_name == mock_db_user.last_name
        assert result.disabled == (not mock_db_user.is_active)
        assert result.roles == [role.name for role in mock_db_user.roles]
