import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.db.user import User
from app.dependencies import get_current_active_user
from app.schemas.db.prediction import DDIPredictRequest


@pytest.fixture
def authenticated_client():

    def override_get_current_active_user():
        return User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            disabled=False,
            roles=["user"]
        )
    
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    client = TestClient(app)
    yield client
    # Clean up after test
    app.dependency_overrides.clear()

@pytest.fixture
def predict_request():
    return DDIPredictRequest(
        drug1="Aspirin",
        drug2="Ibuprofen",
        Age=65,
        Sex="M",
        Comorbidities=["Hypertension", "Diabetes"],
        pair_key="aspirin_ibuprofen",
        unified_severity="Major",
        unified_mechanism_text="Both drugs affect blood clotting mechanisms",
        ddi_confidence=0.95,
        ddi_known=True
    )


class TestPredictionsRouter:

    def test_get_predictions_success(self, mocker, authenticated_client, predict_request):
        # Mock at the router level where functions are imported
        mocker.patch("app.routers.predictions.enrich_from_database", return_value={
            "similar_cases": [],
            "top_mechanisms": [],
            "representative_cases": [],
            "severity_distribution": {
                "known_severity_count": 10,
                "total_cases": 20
            }
        })
        mocker.patch("app.routers.predictions.build_system_prompt", return_value="System prompt")
        mocker.patch("app.routers.predictions.build_user_prompt", return_value="User prompt")
        mocker.patch("app.routers.predictions.invoke_bedrock_model", return_value="mock_completion")
        mocker.patch("app.routers.predictions.parse_bedrock_response", return_value={
            "reasoning": "Both drugs affect blood clotting mechanisms",
            "content": {
                "severity": "Major"
            }
        })
        
        response = authenticated_client.post("/predict", json=predict_request.model_dump())

        assert response.status_code == 200
        assert response.json()["severity"] == "Major"
        assert response.json()["drug1"] == "Aspirin"
        assert response.json()["drug2"] == "Ibuprofen"

