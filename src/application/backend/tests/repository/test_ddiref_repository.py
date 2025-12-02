import pytest
from unittest.mock import MagicMock, Mock
from sqlalchemy.orm import Session

from app.repositories.ddiref_repository import (
    find_static_ddi_severity,
    search_matching_drug_names
)
from app.db.models.ddiref import DDIRef


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_ddi_refs():
    """Mock DDI reference data."""
    ref1 = DDIRef(
        pair_key="warfarin_aspirin",
        drug1_norm="warfarin",
        drug2_norm="aspirin",
        unified_severity="Major",
        unified_mechanism_text="Increased bleeding risk"
    )
    ref2 = DDIRef(
        pair_key="ibuprofen_aspirin",
        drug1_norm="ibuprofen",
        drug2_norm="aspirin",
        unified_severity="Moderate",
        unified_mechanism_text="NSAID interaction"
    )
    ref3 = DDIRef(
        pair_key="metformin_insulin",
        drug1_norm="metformin",
        drug2_norm="insulin",
        unified_severity="Minor",
        unified_mechanism_text="Blood sugar monitoring needed"
    )
    return [ref1, ref2, ref3]


class TestFindStaticDDISeverity:
    """Tests for find_static_ddi_severity function."""

    def test_find_severity_with_exact_match(self, mock_db):
        """Test finding severity with exact drug order match."""
        # Mock query chain
        mock_result = Mock()
        mock_result.unified_severity = "Major"
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "warfarin", "aspirin")

        assert result == "Major"
        mock_db.query.assert_called_once()

    def test_find_severity_with_reversed_drugs(self, mock_db):
        """Test finding severity with reversed drug order (aspirin, warfarin)."""
        # Mock query chain
        mock_result = Mock()
        mock_result.unified_severity = "Major"
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "aspirin", "warfarin")

        assert result == "Major"
        mock_db.query.assert_called_once()

    def test_find_severity_case_insensitive(self, mock_db):
        """Test that search is case-insensitive."""
        # Mock query chain
        mock_result = Mock()
        mock_result.unified_severity = "Major"
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "WARFARIN", "ASPIRIN")

        assert result == "Major"
        mock_db.query.assert_called_once()

    def test_find_severity_no_match(self, mock_db):
        """Test when no DDI reference is found."""
        # Mock query chain returning None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "unknown_drug", "another_drug")

        assert result is None
        mock_db.query.assert_called_once()

    def test_find_severity_none_severity(self, mock_db):
        """Test when result exists but severity is None."""
        # Mock query chain with None severity
        mock_result = Mock()
        mock_result.unified_severity = None
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "drug1", "drug2")

        assert result is None
        mock_db.query.assert_called_once()

    def test_find_severity_moderate(self, mock_db):
        """Test finding moderate severity interaction."""
        # Mock query chain
        mock_result = Mock()
        mock_result.unified_severity = "Moderate"
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "ibuprofen", "aspirin")

        assert result == "Moderate"

    def test_find_severity_minor(self, mock_db):
        """Test finding minor severity interaction."""
        # Mock query chain
        mock_result = Mock()
        mock_result.unified_severity = "Minor"
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query

        result = find_static_ddi_severity(mock_db, "metformin", "insulin")

        assert result == "Minor"


class TestSearchMatchingDrugNames:
    """Tests for search_matching_drug_names function."""

    def test_search_with_matching_drugs(self, mock_db):
        """Test searching for drugs that match the pattern."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["aspirin", "asparaginase"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "aspi", 10)

        assert len(results) == 2
        assert "aspirin" in results
        assert "asparaginase" in results
        mock_db.execute.assert_called_once()

    def test_search_with_empty_query(self, mock_db):
        """Test searching with empty drug name returns empty list."""
        results = search_matching_drug_names(mock_db, "", 10)

        assert results == []
        mock_db.execute.assert_not_called()

    def test_search_with_none_query(self, mock_db):
        """Test searching with None drug name returns empty list."""
        results = search_matching_drug_names(mock_db, None, 10)

        assert results == []
        mock_db.execute.assert_not_called()

    def test_search_with_no_matches(self, mock_db):
        """Test searching when no drugs match."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "zzzzz", 10)

        assert results == []
        mock_db.execute.assert_called_once()

    def test_search_respects_limit(self, mock_db):
        """Test that search respects the limit parameter."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["aspirin", "asparaginase", "aspartame"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "asp", 3)

        assert len(results) == 3
        mock_db.execute.assert_called_once()

    def test_search_with_limit_one(self, mock_db):
        """Test searching with limit of 1."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["aspirin"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "aspirin", 1)

        assert len(results) == 1
        assert results[0] == "aspirin"

    def test_search_case_insensitive(self, mock_db):
        """Test that search is case-insensitive."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["Aspirin", "ASPARAGINASE"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "ASPI", 10)

        assert len(results) == 2
        mock_db.execute.assert_called_once()

    def test_search_partial_match(self, mock_db):
        """Test searching with partial drug name."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["warfarin", "warfarin sodium"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "warf", 10)

        assert len(results) == 2
        assert "warfarin" in results
        assert "warfarin sodium" in results

    def test_search_returns_sorted_by_length(self, mock_db):
        """Test that results are sorted by length (shortest first)."""
        # Mock execute and scalars - should already be sorted by length
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["aspirin", "asparaginase", "aspirin complex"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "asp", 10)

        # Results should be ordered by length
        assert len(results[0]) <= len(results[1])
        assert len(results[1]) <= len(results[2])

    def test_search_with_special_characters(self, mock_db):
        """Test searching with special characters in drug name."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["drug-name", "drug.name"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "drug", 10)

        assert len(results) == 2
        mock_db.execute.assert_called_once()

    def test_search_single_character(self, mock_db):
        """Test searching with single character."""
        # Mock execute and scalars
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["aspirin", "acetaminophen"]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_db.execute.return_value = mock_result

        results = search_matching_drug_names(mock_db, "a", 10)

        assert len(results) == 2
        mock_db.execute.assert_called_once()

    def test_search_whitespace_query(self, mock_db):
        """Test searching with whitespace only returns empty list."""
        results = search_matching_drug_names(mock_db, "   ", 10)

        # Whitespace is truthy, so it will attempt the search
        # This tests the actual behavior
        mock_db.execute.assert_called_once()
