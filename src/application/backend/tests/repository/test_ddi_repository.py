import pytest
from unittest.mock import MagicMock
from app.repositories.ddi_repository import (
    find_similar_interactions,
    get_interaction_statistics
)
from app.db.models.ddi import PatientDDI


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


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


class TestDDIRepository:

    def test_find_similar_interactions_basic(self, mocker, mock_db, mock_ddi_cases):
        """Test finding similar interactions with basic drug pair matching."""
        # Mock the query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_ddi_cases

        result = find_similar_interactions(
            db=mock_db,
            drug1="warfarin",
            drug2="aspirin",
            limit=10
        )

        assert len(result) == 2
        assert result[0].patient_uuid == "patient-1"
        assert result[1].patient_uuid == "patient-2"
        mock_db.query.assert_called_once()

    def test_find_similar_interactions_with_age_filter(self, mocker, mock_db, mock_ddi_cases):
        """Test finding similar interactions with age filtering."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_ddi_cases[0]]

        result = find_similar_interactions(
            db=mock_db,
            drug1="warfarin",
            drug2="aspirin",
            age=65,
            limit=10
        )

        assert len(result) == 1
        assert result[0].age == 65

    def test_find_similar_interactions_with_sex_filter(self, mocker, mock_db, mock_ddi_cases):
        """Test finding similar interactions with sex filtering."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_ddi_cases[0]]

        result = find_similar_interactions(
            db=mock_db,
            drug1="warfarin",
            drug2="aspirin",
            sex="M",
            limit=10
        )

        assert len(result) == 1
        assert result[0].sex == "M"

    def test_find_similar_interactions_with_comorbidities(self, mocker, mock_db, mock_ddi_cases):
        """Test finding similar interactions with comorbidity filtering."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_ddi_cases

        result = find_similar_interactions(
            db=mock_db,
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension"],
            limit=10
        )

        assert len(result) == 2

    def test_find_similar_interactions_empty_result(self, mocker, mock_db):
        """Test finding similar interactions with no matches."""
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = find_similar_interactions(
            db=mock_db,
            drug1="unknown_drug1",
            drug2="unknown_drug2",
            limit=10
        )

        assert len(result) == 0

    def test_get_interaction_statistics_success(self, mocker, mock_db):
        """Test getting interaction statistics for a drug pair."""
        # Mock the aggregate query result
        mock_stats = MagicMock()
        mock_stats.total_cases = 10
        mock_stats.known_severity_count = 8
        mock_stats.avg_confidence = 0.85
        mock_stats.is_known_interaction = 1

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_stats

        # Mock severity distribution query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [("Major", 6), ("Moderate", 2)]

        result = get_interaction_statistics(
            db=mock_db,
            drug1="warfarin",
            drug2="aspirin"
        )

        assert result["total_cases"] == 10
        assert result["known_severity_count"] == 8
        assert result["avg_confidence"] == 0.85
        assert result["is_known_interaction"] is True
        assert result["severity_distribution"]["Major"] == 6
        assert result["severity_distribution"]["Moderate"] == 2

    def test_get_interaction_statistics_no_data(self, mocker, mock_db):
        """Test getting interaction statistics with no data."""
        # Mock empty result
        mock_stats = MagicMock()
        mock_stats.total_cases = None
        mock_stats.known_severity_count = None
        mock_stats.avg_confidence = None
        mock_stats.is_known_interaction = None

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_stats
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []

        result = get_interaction_statistics(
            db=mock_db,
            drug1="unknown_drug1",
            drug2="unknown_drug2"
        )

        assert result["total_cases"] == 0
        assert result["known_severity_count"] == 0
        assert result["avg_confidence"] == 0.0
        assert result["is_known_interaction"] is False
        assert result["severity_distribution"] == {}
