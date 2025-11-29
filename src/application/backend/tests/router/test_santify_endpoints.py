import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


class TestSanityCheck:
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to AIDoctors API"}

    def test_get_icon(self, client):
        response = client.get("/favicon.ico")
        assert response.status_code == 204
        
        
    
    

