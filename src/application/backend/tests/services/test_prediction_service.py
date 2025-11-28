import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.prediction_service import (
    parse_bedrock_response,
    enrich_from_database,
    invoke_bedrock_model,
    get_bedrock_client
)
from app.schemas.db.prediction import DDIPredictRequest
from app.db.models.ddi import PatientDDI


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def mock_predict_request():
    """Mock prediction request."""
    return DDIPredictRequest(
        drug1="Warfarin",
        drug2="Aspirin",
        Age=65,
        Sex="M",
        Comorbidities=["Hypertension", "Diabetes"]
    )


@pytest.fixture
def mock_ddi_cases():
    """Mock DDI cases for testing."""
    case1 = PatientDDI(
        patient_uuid="patient-1",
        drug1="Warfarin",
        drug2="Aspirin",
        drug1_norm="warfarin",
        drug2_norm="aspirin",
        age=65,
        sex="M",
        comorbidities="['Hypertension', 'Diabetes']",
        unified_severity="Major",
        unified_mechanism_text="Both drugs affect blood clotting",
        ddi_confidence=0.95,
        ddi_known=True
    )
    case2 = PatientDDI(
        patient_uuid="patient-2",
        drug1="Aspirin",
        drug2="Warfarin",
        drug1_norm="aspirin",
        drug2_norm="warfarin",
        age=70,
        sex="F",
        comorbidities="['Hypertension']",
        unified_severity="Major",
        unified_mechanism_text="Increased bleeding risk",
        ddi_confidence=0.90,
        ddi_known=True
    )
    return [case1, case2]


class TestPredictionService:

    def test_parse_bedrock_response_with_reasoning(self):
        """Test parsing Bedrock response with reasoning tags."""
        response_text = '<reasoning>This is the reasoning</reasoning>{"severity": "Major", "confidence": 0.95}'
        
        result = parse_bedrock_response(response_text)
        
        assert result["reasoning"] == "This is the reasoning"
        assert result["content"]["severity"] == "Major"
        assert result["content"]["confidence"] == 0.95

    def test_parse_bedrock_response_without_reasoning(self):
        """Test parsing Bedrock response without reasoning tags."""
        response_text = '{"severity": "Moderate", "confidence": 0.80}'
        
        result = parse_bedrock_response(response_text)
        
        assert result["reasoning"] == ""
        assert result["content"]["severity"] == "Moderate"
        assert result["content"]["confidence"] == 0.80

    def test_parse_bedrock_response_multiline_reasoning(self):
        """Test parsing Bedrock response with multiline reasoning."""
        response_text = '''<reasoning>
        This is a multiline reasoning
        with multiple lines
        </reasoning>{"severity": "Minor"}'''
        
        result = parse_bedrock_response(response_text)
        
        assert "multiline reasoning" in result["reasoning"]
        assert result["content"]["severity"] == "Minor"

    def test_enrich_from_database_with_cases(self, mocker, mock_db, mock_predict_request, mock_ddi_cases):
        """Test enriching prediction with database context."""
        # Mock repository functions
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=mock_ddi_cases)
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 10,
            "known_severity_count": 8,
            "avg_confidence": 0.85,
            "is_known_interaction": True,
            "severity_distribution": {"Major": 6, "Moderate": 2}
        })

        result = enrich_from_database(mock_db, mock_predict_request)

        assert result["similar_cases_count"] == 2
        assert result["known_interaction"] is True
        assert result["avg_confidence"] == 0.85
        assert len(result["top_mechanisms"]) > 0
        assert len(result["representative_cases"]) > 0
        assert result["severity_distribution"]["known_severity_count"] == 8
        assert result["severity_distribution"]["total_cases"] == 10

    def test_enrich_from_database_no_cases(self, mocker, mock_db, mock_predict_request):
        """Test enriching prediction with no database matches."""
        # Mock repository functions to return empty results
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 0,
            "known_severity_count": 0,
            "avg_confidence": 0.0,
            "is_known_interaction": False,
            "severity_distribution": {}
        })

        result = enrich_from_database(mock_db, mock_predict_request)

        assert result["similar_cases_count"] == 0
        assert result["known_interaction"] is False
        assert result["avg_confidence"] == 0.0
        assert len(result["top_mechanisms"]) == 0
        assert len(result["representative_cases"]) == 0

    def test_enrich_from_database_filters_mechanisms(self, mocker, mock_db, mock_predict_request):
        """Test that enrichment filters out duplicate mechanisms."""
        # Create cases with duplicate mechanisms
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="Warfarin",
            drug2="Aspirin",
            unified_mechanism_text="Bleeding risk",
            unified_severity="Major",
            age=65,
            sex="M",
            comorbidities="[]",
            ddi_confidence=0.95,
            ddi_known=True
        )
        case2 = PatientDDI(
            patient_uuid="patient-2",
            drug1="Warfarin",
            drug2="Aspirin",
            unified_mechanism_text="Bleeding risk",  # Duplicate
            unified_severity="Major",
            age=70,
            sex="F",
            comorbidities="[]",
            ddi_confidence=0.90,
            ddi_known=True
        )

        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[case1, case2])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 2,
            "known_severity_count": 2,
            "avg_confidence": 0.925,
            "is_known_interaction": True,
            "severity_distribution": {"Major": 2}
        })

        result = enrich_from_database(mock_db, mock_predict_request)

        # Should have only one unique mechanism
        assert len(result["top_mechanisms"]) == 1
        assert "Bleeding risk" in result["top_mechanisms"]

    def test_enrich_from_database_limits_representative_cases(self, mocker, mock_db, mock_predict_request):
        """Test that enrichment limits representative cases to 5."""
        # Create 10 cases
        cases = [
            PatientDDI(
                patient_uuid=f"patient-{i}",
                drug1="Warfarin",
                drug2="Aspirin",
                unified_mechanism_text=f"Mechanism {i}",
                unified_severity="Major",
                age=65,
                sex="M",
                comorbidities="[]",
                ddi_confidence=0.95,
                ddi_known=True
            )
            for i in range(10)
        ]

        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=cases)
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 10,
            "known_severity_count": 10,
            "avg_confidence": 0.95,
            "is_known_interaction": True,
            "severity_distribution": {"Major": 10}
        })

        result = enrich_from_database(mock_db, mock_predict_request)

        # Should limit to 5 representative cases
        assert len(result["representative_cases"]) == 5

    def test_invoke_bedrock_model_openai(self, mocker):
        """Test invoking Bedrock model with OpenAI model."""
        # Mock get_bedrock_client
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        
        # Mock environment variable
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        # Mock invoke_model response
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'choices': [{'message': {'content': 'Test completion'}}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response

        result = invoke_bedrock_model("System prompt", "User prompt")

        assert result == "Test completion"
        mock_client.invoke_model.assert_called_once()

    def test_get_bedrock_client_success(self, mocker):
        """Test successful Bedrock client creation."""
        # Mock boto3.client
        mock_boto_client = MagicMock()
        mocker.patch("boto3.client", return_value=mock_boto_client)
        mocker.patch("os.getenv", return_value="us-east-1")

        result = get_bedrock_client()

        assert result is not None
        assert result == mock_boto_client

    def test_get_bedrock_client_error(self, mocker):
        """Test Bedrock client creation with error."""
        # Mock boto3.client to raise exception
        mocker.patch("boto3.client", side_effect=Exception("AWS error"))
        mocker.patch("os.getenv", return_value="us-east-1")

        with pytest.raises(Exception) as exc_info:
            get_bedrock_client()
        
        assert "AWS error" in str(exc_info.value)
