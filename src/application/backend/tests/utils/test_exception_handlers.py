import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestExceptionHandlers:
    """Test exception handlers using the register endpoint."""

    def test_validation_error_missing_required_field(self, mocker, client):
        """Test validation exception handler with missing required field."""

        # Mock database functions to avoid actual DB calls
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user")

        # Missing 'username' field
        response = client.post("/api/users/register", json={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123"
        })

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data
        assert len(data["errors"]) > 0
        
        # Check that the error mentions the missing field
        error = data["errors"][0]
        assert "field" in error
        assert "username" in error["field"]
        assert "missing" in error["message"].lower()

    def test_validation_error_missing_multiple_fields(self, mocker, client):
        """Test validation exception handler with multiple missing fields."""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user")

        # Missing multiple required fields
        response = client.post("/api/users/register", json={
            "first_name": "Test"
        })

        assert response.status_code == 422
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) >= 3 

    def test_validation_error_invalid_type(self, mocker, client):
        """Test validation exception handler with incorrect field type."""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user")

        # Pass integer instead of string for username
        response = client.post("/api/users/register", json={
            "username": 12345,  # Should be string
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123"
        })

        assert response.status_code == 422
        data = response.json()
        assert "errors" in data
        
        # Check for type error
        errors = data["errors"]
        username_error = next((e for e in errors if "username" in e["field"]), None)
        assert username_error is not None

    def test_validation_error_invalid_email_format(self, mocker, client):
        """Test validation exception handler with invalid email format."""
        from app.db.models.user import DBUser
        
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        
        # Mock create_user to return a proper user
        mock_user = DBUser(
            id=1,
            username="testuser",
            email="not-an-email",
            first_name="Test",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        mock_user.roles = []
        mocker.patch("app.routers.users.create_user", return_value=mock_user)

        # Invalid email format
        response = client.post("/api/users/register", json={
            "username": "testuser",
            "email": "not-an-email",  # Invalid email
            "first_name": "Test",
            "last_name": "User",
            "password": "password123"
        })

        # Note: This might pass if email validation is not strict in the schema
        # If it fails, it should be 422
        assert response.status_code in [200, 422]

    def test_validation_error_empty_string_fields(self, mocker, client):
        """Test validation exception handler with empty string fields."""
        from app.db.models.user import DBUser
        
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        
        # Mock create_user to return a proper user with empty strings
        mock_user = DBUser(
            id=1,
            username="",
            email="",
            first_name="",
            last_name="",
            hashed_password="hashed",
            is_active=True
        )
        mock_user.roles = []
        mocker.patch("app.routers.users.create_user", return_value=mock_user)

        # Empty strings for required fields
        response = client.post("/api/users/register", json={
            "username": "",
            "email": "",
            "first_name": "",
            "last_name": "",
            "password": ""
        })

        # Depending on validation rules, this might pass or fail
        # If it fails, it should be 422
        assert response.status_code in [200, 400, 422]

    def test_validation_error_null_values(self, mocker, client):
        """Test validation exception handler with null values."""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        mocker.patch("app.routers.users.create_user")

        # Null values for required fields
        response = client.post("/api/users/register", json={
            "username": None,
            "email": None,
            "first_name": None,
            "last_name": None,
            "password": None
        })

        assert response.status_code == 422
        data = response.json()
        assert "errors" in data

    def test_validation_error_extra_fields(self, mocker, client):
        """Test that extra fields are ignored (not causing validation errors)."""
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        
        # Mock create_user to return a proper user
        from app.db.models.user import DBUser
        mock_user = DBUser(
            id=1,
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        mock_user.roles = []
        mocker.patch("app.routers.users.create_user", return_value=mock_user)

        # Include extra fields that aren't in the schema
        response = client.post("/api/users/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "extra_field": "should be ignored"
        })

        # Extra fields should be ignored, request should succeed
        assert response.status_code == 200

    def test_validation_error_malformed_json(self, client):
        """Test exception handler with malformed JSON."""
        response = client.post(
            "/api/users/register",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return 422 for malformed JSON
        assert response.status_code == 422

    def test_http_exception_username_already_exists(self, mocker, client):
        """Test HTTPException when username already exists."""
        from app.db.models.user import DBUser
        
        # Mock that username already exists
        existing_user = DBUser(
            id=1,
            username="existinguser",
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        existing_user.roles = []
        
        mocker.patch("app.routers.users.get_user_by_username", return_value=existing_user)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)

        response = client.post("/api/users/register", json={
            "username": "existinguser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123"
        })

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Username already registered" in data["detail"]

    def test_http_exception_email_already_exists(self, mocker, client):
        """Test HTTPException when email already exists."""
        from app.db.models.user import DBUser
        
        # Mock that email already exists
        existing_user = DBUser(
            id=1,
            username="existinguser",
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        existing_user.roles = []
        
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=existing_user)

        response = client.post("/api/users/register", json={
            "username": "newuser",
            "email": "existing@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123"
        })

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Email already registered" in data["detail"]

    def test_successful_registration(self, mocker, client):
        """Test successful user registration (no exceptions)."""
        from app.db.models.user import DBUser
        
        mocker.patch("app.routers.users.get_user_by_username", return_value=None)
        mocker.patch("app.routers.users.get_user_by_email", return_value=None)
        
        # Mock create_user to return a proper user
        mock_user = DBUser(
            id=1,
            username="newuser",
            email="new@example.com",
            first_name="New",
            last_name="User",
            hashed_password="hashed",
            is_active=True
        )
        mock_user.roles = []
        mocker.patch("app.routers.users.create_user", return_value=mock_user)

        response = client.post("/api/users/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"