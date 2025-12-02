import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.prediction_service import (
    parse_bedrock_response,
    enrich_from_database_async,
    invoke_bedrock_model,
    get_bedrock_client
)
from app.schemas.db.prediction import DDIPredictRequest
from app.db.models.patientddi import PatientDDI


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

    def test_parse_bedrock_response_with_json(self):
        """Test parsing Bedrock response with JSON."""
        response_text = '{"severity": "Major", "confidence": 0.95}'
        
        result = parse_bedrock_response(response_text)
        
        assert result["content"]["severity"] == "Major"
        assert result["content"]["confidence"] == 0.95

    def test_parse_bedrock_response_simple_json(self):
        """Test parsing simple JSON response."""
        response_text = '{"severity": "Moderate", "confidence": 0.80}'
        
        result = parse_bedrock_response(response_text)
        
        assert result["content"]["severity"] == "Moderate"
        assert result["content"]["confidence"] == 0.80

    def test_parse_bedrock_response_with_markdown_code_block(self):
        """Test parsing Bedrock response with markdown code block."""
        response_text = '''```json
{"severity": "Minor"}
```'''
        
        result = parse_bedrock_response(response_text)
        
        assert result["content"]["severity"] == "Minor"

    @pytest.mark.asyncio
    async def test_enrich_from_database_with_cases(self, mocker, mock_db, mock_predict_request, mock_ddi_cases):
        """Test enriching prediction with database context."""
        # Mock repository functions
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=mock_ddi_cases)
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 10,
            "known_severity_count": 8,
            "avg_confidence": 0.85,
            "is_known_interaction_from_patients": True,
            "severity_distribution": {"Major": 6, "Moderate": 2}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value="Major")

        result = await enrich_from_database_async(mock_db, mock_predict_request)

        assert result["similar_cases_count"] == 2
        assert result["known_interaction_from_patients"] is True
        assert result["avg_confidence"] == 0.85
        assert len(result["mechanisms"]) > 0
        assert len(result["representative_cases"]) > 0
        assert result["severity_distribution"]["known_severity_count"] == 8
        assert result["severity_distribution"]["total_cases"] == 10

    @pytest.mark.asyncio
    async def test_enrich_from_database_no_cases(self, mocker, mock_db, mock_predict_request):
        """Test enriching prediction with no database matches."""
        # Mock repository functions to return empty results
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 0,
            "known_severity_count": 0,
            "avg_confidence": 0.0,
            "is_known_interaction_from_patients": False,
            "severity_distribution": {}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value=None)

        result = await enrich_from_database_async(mock_db, mock_predict_request)

        assert result["similar_cases_count"] == 0
        assert result["known_interaction_from_patients"] is False
        assert result["avg_confidence"] == 0.0
        assert len(result["mechanisms"]) == 0
        assert len(result["representative_cases"]) == 0

    @pytest.mark.asyncio
    async def test_enrich_from_database_filters_mechanisms(self, mocker, mock_db, mock_predict_request):
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
            "is_known_interaction_from_patients": True,
            "severity_distribution": {"Major": 2}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value="Major")

        result = await enrich_from_database_async(mock_db, mock_predict_request)

        # Should have only one unique mechanism
        assert len(result["mechanisms"]) == 1
        assert "Bleeding risk" in result["mechanisms"]

    @pytest.mark.asyncio
    async def test_enrich_from_database_returns_all_representative_cases(self, mocker, mock_db, mock_predict_request):
        """Test that enrichment returns all representative cases."""
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
            "is_known_interaction_from_patients": True,
            "severity_distribution": {"Major": 10}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value="Major")

        result = await enrich_from_database_async(mock_db, mock_predict_request)

        # Should return all representative cases
        assert len(result["representative_cases"]) == 10

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

    # ==================================================================================
    # EDGE CASES AND FAILURE MODES - Added for comprehensive testing
    # ==================================================================================
    
    def test_parse_bedrock_response_malformed_json(self):
        """
        EDGE CASE: Malformed JSON in response content.
        Tests that parse_bedrock_response returns fallback structure when content is not valid JSON.
        This can happen if the model returns corrupted or incomplete responses.
        """
        response_text = 'This is not valid JSON'
        
        result = parse_bedrock_response(response_text)
        # Should return fallback structure with error info
        assert result["content"]["predicted_severity"] == "Unknown"
        assert "Error" in result["content"]["summary"]
    
    def test_parse_bedrock_response_empty_string(self):
        """
        EDGE CASE: Empty response string.
        Tests handling of completely empty responses from Bedrock.
        This could occur during network issues or API failures.
        """
        response_text = ''
        
        result = parse_bedrock_response(response_text)
        # Should return fallback structure
        assert result["content"]["predicted_severity"] == "Unknown"
    
    def test_parse_bedrock_response_only_text_no_json(self):
        """
        EDGE CASE: Response with only text, no JSON content.
        Tests that the function fails gracefully when JSON content is missing.
        """
        response_text = 'Only text here, no JSON'
        
        result = parse_bedrock_response(response_text)
        # Should return fallback structure
        assert result["content"]["predicted_severity"] == "Unknown"
    
    def test_parse_bedrock_response_with_extra_text(self):
        """
        EDGE CASE: Response with extra text around JSON.
        Tests that the function can extract JSON from text with surrounding content.
        """
        response_text = 'Here is the result: {"severity": "Major"} and some more text'
        
        result = parse_bedrock_response(response_text)
        # Should successfully extract the JSON
        assert result["content"]["severity"] == "Major"
    
    def test_parse_bedrock_response_nested_json(self):
        """
        EDGE CASE: Response with nested JSON objects.
        Tests handling of complex nested JSON structures.
        """
        response_text = '{"severity": "Minor", "details": {"mechanism": "test"}}'
        
        result = parse_bedrock_response(response_text)
        # Should successfully parse nested JSON
        assert result["content"]["severity"] == "Minor"
        assert result["content"]["details"]["mechanism"] == "test"
    
    def test_parse_bedrock_response_special_characters_in_json(self):
        """
        EDGE CASE: Special characters and unicode in JSON content.
        Tests handling of escaped characters, quotes, and unicode in the response.
        Important for international drug names and clinical text.
        """
        response_text = '{"severity": "Major", "note": "Patient has \\"severe\\" reaction", "drug": "Naproxène"}'
        
        result = parse_bedrock_response(response_text)
        
        assert result["content"]["severity"] == "Major"
        assert result["content"]["drug"] == "Naproxène"
    
    @pytest.mark.asyncio
    async def test_enrich_from_database_with_none_stats(self, mocker, mock_db, mock_predict_request):
        """
        EDGE CASE: Database returns None for statistics.
        Tests handling when get_interaction_statistics returns None instead of a dict.
        This can happen with database errors or empty result sets.
        """
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value=None)
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value=None)
        
        result = await enrich_from_database_async(mock_db, mock_predict_request)
        
        # Should handle None gracefully with defaults
        assert result["known_interaction_from_patients"] is False
        assert result["avg_confidence"] is None
        assert result["severity_distribution"] == {}
    
    @pytest.mark.asyncio
    async def test_enrich_from_database_cases_with_none_mechanisms(self, mocker, mock_db, mock_predict_request):
        """
        EDGE CASE: Cases with None or missing mechanism text.
        Tests filtering of cases where unified_mechanism_text is None.
        This is common in real-world data with incomplete records.
        """
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="Warfarin",
            drug2="Aspirin",
            unified_mechanism_text=None,  # Missing mechanism
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
            unified_mechanism_text="Valid mechanism",
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
            "is_known_interaction_from_patients": True,
            "severity_distribution": {"Major": 2}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value="Major")
        
        result = await enrich_from_database_async(mock_db, mock_predict_request)
        
        # Should only include non-None mechanisms
        assert len(result["mechanisms"]) == 1
        assert "Valid mechanism" in result["mechanisms"]
    
    @pytest.mark.asyncio
    async def test_enrich_from_database_empty_comorbidities(self, mocker, mock_db):
        """
        EDGE CASE: Request with None or empty comorbidities list.
        Tests that enrichment works when patient has no comorbidities.
        Important for healthy patients or incomplete medical records.
        """
        request = DDIPredictRequest(
            drug1="DrugA",
            drug2="DrugB",
            Age=30,
            Sex="F",
            Comorbidities=None  # No comorbidities
        )
        
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 0,
            "known_severity_count": 0,
            "avg_confidence": 0.0,
            "is_known_interaction_from_patients": False,
            "severity_distribution": {}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value=None)
        
        result = await enrich_from_database_async(mock_db, request)
        
        # Should complete without errors
        assert result["similar_cases_count"] == 0
        assert result["representative_cases"] == []
    
    def test_invoke_bedrock_model_anthropic_claude(self, mocker):
        """
        USE CASE: Invoking Bedrock with Anthropic Claude model.
        Tests the different response format for Claude models.
        Important because the system supports multiple model providers.
        """
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="anthropic.claude-v2")
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'content': [{'text': 'Claude completion'}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        result = invoke_bedrock_model("System prompt", "User prompt")
        
        assert result == "Claude completion"
    
    def test_invoke_bedrock_model_unknown_provider(self, mocker):
        """
        EDGE CASE: Unknown model provider fallback.
        Tests the fallback logic when model ID doesn't match known providers.
        This ensures the system degrades gracefully with new or custom models.
        """
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="custom.model-v1")
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'completion': 'Fallback completion'
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        result = invoke_bedrock_model("System prompt", "User prompt")
        
        assert result == "Fallback completion"
    
    def test_invoke_bedrock_model_client_error(self, mocker):
        """
        FAILURE MODE: AWS ClientError during model invocation.
        Tests error handling for AWS API errors (throttling, permissions, etc.).
        Critical for production reliability and debugging.
        """
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        # Simulate AWS ClientError
        error_response = {'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}}
        mock_client.invoke_model.side_effect = ClientError(error_response, 'InvokeModel')
        
        with pytest.raises(Exception) as exc_info:
            invoke_bedrock_model("System prompt", "User prompt")
        
        assert "ThrottlingException" in str(exc_info.value)
        assert "Rate exceeded" in str(exc_info.value)
    
    def test_invoke_bedrock_model_no_credentials_error(self, mocker):
        """
        FAILURE MODE: Missing AWS credentials.
        Tests error handling when AWS credentials are not configured.
        Important for deployment troubleshooting and local development.
        """
        from botocore.exceptions import NoCredentialsError
        
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        mock_client.invoke_model.side_effect = NoCredentialsError()
        
        with pytest.raises(Exception) as exc_info:
            invoke_bedrock_model("System prompt", "User prompt")
        
        assert "AWS credentials not found" in str(exc_info.value)
    
    def test_invoke_bedrock_model_malformed_response_body(self, mocker):
        """
        FAILURE MODE: Malformed JSON in Bedrock response body.
        Tests handling of corrupted or invalid response from AWS.
        This can happen during network issues or API bugs.
        """
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        # Return invalid JSON
        mock_response = {
            'body': MagicMock(read=lambda: b'Not valid JSON at all')
        }
        mock_client.invoke_model.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            invoke_bedrock_model("System prompt", "User prompt")
        
        assert "Error invoking Bedrock model" in str(exc_info.value)
    
    def test_invoke_bedrock_model_missing_expected_fields(self, mocker):
        """
        EDGE CASE: Response missing expected fields for model type.
        Tests fallback when OpenAI response doesn't have expected structure.
        Important for API version changes or unexpected response formats.
        """
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        # Missing 'choices' field
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'unexpected_field': 'value'
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        # Should raise an error due to missing fields
        with pytest.raises(Exception):
            invoke_bedrock_model("System prompt", "User prompt")
    
    @pytest.mark.asyncio
    async def test_enrich_from_database_with_partial_stats(self, mocker, mock_db, mock_predict_request):
        """
        EDGE CASE: Statistics with zero known_severity_count.
        Tests handling when stats exist but known_severity_count is 0.
        This affects whether severity_distribution is included in enriched context.
        """
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=[])
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 5,
            "known_severity_count": 0,  # No known severities
            "avg_confidence": 0.5,
            "is_known_interaction_from_patients": False,
            "severity_distribution": {}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value=None)
        
        result = await enrich_from_database_async(mock_db, mock_predict_request)
        
        # severity_distribution should be empty dict when known_severity_count is 0
        assert result["severity_distribution"] == {}
        assert result["avg_confidence"] == 0.5
    
    @pytest.mark.asyncio
    async def test_enrich_from_database_returns_exact_number_of_cases(self, mocker, mock_db, mock_predict_request):
        """
        EDGE CASE: Returns exact number of cases found.
        Tests that all similar cases are returned as representative cases.
        """
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
            for i in range(3)  # 3 cases
        ]
        
        mocker.patch("app.services.prediction_service.find_similar_interactions", return_value=cases)
        mocker.patch("app.services.prediction_service.get_interaction_statistics", return_value={
            "total_cases": 3,
            "known_severity_count": 3,
            "avg_confidence": 0.95,
            "is_known_interaction_from_patients": True,
            "severity_distribution": {"Major": 3}
        })
        mocker.patch("app.services.prediction_service.find_static_ddi_severity", return_value="Major")
        
        result = await enrich_from_database_async(mock_db, mock_predict_request)
        
        # Should include all 3 cases
        assert len(result["representative_cases"]) == 3
        assert result["similar_cases_count"] == 3
    
    def test_parse_bedrock_response_with_whitespace_variations(self):
        """
        EDGE CASE: Various whitespace patterns in response.
        Tests that whitespace handling (strip()) works correctly.
        Important for consistent parsing regardless of model output formatting.
        """
        response_text = '  \n  {"severity": "Major"}  '
        
        result = parse_bedrock_response(response_text)
        
        # Should successfully parse despite whitespace
        assert result["content"]["severity"] == "Major"
    
    def test_invoke_bedrock_model_empty_prompts(self, mocker):
        """
        EDGE CASE: Empty system or user prompts.
        Tests behavior when prompts are empty strings.
        This could happen due to upstream bugs or edge cases in prompt building.
        """
        mock_client = MagicMock()
        mocker.patch("app.services.prediction_service.get_bedrock_client", return_value=mock_client)
        mocker.patch("os.getenv", return_value="openai.gpt-oss-120b-1:0")
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'choices': [{'message': {'content': 'Response to empty prompts'}}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        # Should not crash with empty prompts
        result = invoke_bedrock_model("", "")
        
        assert result == "Response to empty prompts"
        # Verify the request was made with empty strings
        call_args = mock_client.invoke_model.call_args
        body = json.loads(call_args[1]['body'])
        assert body['messages'][0]['content'] == ""
        assert body['messages'][1]['content'] == ""
