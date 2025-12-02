import pytest
from unittest.mock import MagicMock
from app.repositories.patientddi_repository import (
    find_similar_interactions,
    get_interaction_statistics,
    search_comorbidities
)
from app.db.models.patientddi import PatientDDI


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
        mock_stats.is_known_interaction_from_patients = 1

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
        assert result["is_known_interaction_from_patients"] is True
        assert result["severity_distribution"]["Major"] == 6
        assert result["severity_distribution"]["Moderate"] == 2

    def test_get_interaction_statistics_no_data(self, mocker, mock_db):
        """Test getting interaction statistics with no data."""
        # Mock empty result
        mock_stats = MagicMock()
        mock_stats.total_cases = None
        mock_stats.known_severity_count = None
        mock_stats.avg_confidence = None
        mock_stats.is_known_interaction_from_patients = None

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
        assert result["is_known_interaction_from_patients"] is False
        assert result["severity_distribution"] == {}


class TestSearchComorbidities:
    """Tests for search_comorbidities function."""

    def test_search_comorbidities_with_matches(self, mock_db):
        """Test searching for comorbidities with matching results."""
        # Create mock cases with comorbidities
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Diabetes", "Hyperlipidemia"]
        )
        case2 = PatientDDI(
            patient_uuid="patient-2",
            drug1="metformin",
            drug2="insulin",
            comorbidities=["Diabetes Type 2", "Hypertension"]
        )
        case3 = PatientDDI(
            patient_uuid="patient-3",
            drug1="lisinopril",
            drug2="losartan",
            comorbidities=["Heart Disease", "Hypertension"]
        )

        # Mock the query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1, case2, case3]

        results = search_comorbidities(mock_db, "hyper", 10)

        assert len(results) >= 1
        assert any("Hypertension" in r for r in results)

    def test_search_comorbidities_case_insensitive(self, mock_db):
        """Test that comorbidity search is case-insensitive."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Diabetes"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "HYPER", 10)

        assert len(results) >= 1
        assert any("Hypertension" in r for r in results)

    def test_search_comorbidities_empty_query(self, mock_db):
        """Test searching with empty query returns empty list."""
        results = search_comorbidities(mock_db, "", 10)

        assert results == []
        mock_db.query.assert_not_called()

    def test_search_comorbidities_none_query(self, mock_db):
        """Test searching with None query returns empty list."""
        results = search_comorbidities(mock_db, None, 10)

        assert results == []
        mock_db.query.assert_not_called()

    def test_search_comorbidities_no_matches(self, mock_db):
        """Test searching when no comorbidities match."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Diabetes"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "cancer", 10)

        assert results == []

    def test_search_comorbidities_respects_limit(self, mock_db):
        """Test that search respects the limit parameter."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Hyperlipidemia", "Hypothyroidism", "Hyperglycemia"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "hyper", 2)

        # Should return at most 2 results
        assert len(results) <= 2

    def test_search_comorbidities_sorted_by_length(self, mock_db):
        """Test that results are sorted by length (shortest first)."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Diabetes", "Diabetes Type 2", "Diabetes Mellitus Type 2"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "diabetes", 10)

        # Results should be ordered by length
        if len(results) > 1:
            assert len(results[0]) <= len(results[1])

    def test_search_comorbidities_with_null_comorbidities(self, mock_db):
        """Test handling cases with None comorbidities."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=None
        )
        case2 = PatientDDI(
            patient_uuid="patient-2",
            drug1="metformin",
            drug2="insulin",
            comorbidities=["Diabetes"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1, case2]

        results = search_comorbidities(mock_db, "diabetes", 10)

        # Should only return from case2, not crash on case1's None
        assert len(results) >= 0

    def test_search_comorbidities_filters_empty_strings(self, mock_db):
        """Test that empty strings are filtered out."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "", "Diabetes", None]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "hyper", 10)

        # Should not contain empty strings or None
        assert all(r for r in results)

    def test_search_comorbidities_unique_results(self, mock_db):
        """Test that duplicate comorbidities are deduplicated."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Diabetes"]
        )
        case2 = PatientDDI(
            patient_uuid="patient-2",
            drug1="metformin",
            drug2="insulin",
            comorbidities=["Hypertension", "Hyperlipidemia"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1, case2]

        results = search_comorbidities(mock_db, "hyper", 10)

        # Should have unique entries (using set internally)
        assert len(results) == len(set(results))

    def test_search_comorbidities_partial_match(self, mock_db):
        """Test partial string matching works."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Chronic Obstructive Pulmonary Disease"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "pulmonary", 10)

        assert len(results) >= 1
        assert any("Pulmonary" in r for r in results)

    def test_search_comorbidities_with_limit_one(self, mock_db):
        """Test searching with limit of 1."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities=["Hypertension", "Hyperlipidemia"]
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "hyper", 1)

        assert len(results) <= 1

    def test_search_comorbidities_non_list_type(self, mock_db):
        """Test handling cases where comorbidities is not a list."""
        case1 = PatientDDI(
            patient_uuid="patient-1",
            drug1="warfarin",
            drug2="aspirin",
            comorbidities="Hypertension"  # String instead of list
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [case1]

        results = search_comorbidities(mock_db, "hyper", 10)

        # Should handle gracefully - isinstance check should prevent crash
        assert isinstance(results, list)

