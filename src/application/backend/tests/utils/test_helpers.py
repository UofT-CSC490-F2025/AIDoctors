import pytest
from datetime import datetime
from app.utils.helpers import parse_date, compute_overlap_days


class TestParseDate:
    """Test the parse_date function."""

    def test_parse_date_datetime_object(self):
        """Test parsing datetime object returns the same object."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = parse_date(dt)
        assert result == dt
        assert isinstance(result, datetime)

    def test_parse_date_invalid_type(self):
        """Test parsing invalid type returns None."""
        assert parse_date(12345) is None
        assert parse_date([]) is None
        assert parse_date({}) is None

    def test_parse_date_iso_format_date_only(self):
        """Test parsing ISO format date (YYYY-MM-DD)."""
        result = parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_iso_format_datetime(self):
        """Test parsing ISO format datetime (YYYY-MM-DD HH:MM:SS)."""
       
        result = parse_date("2024-01-15 10:30:45")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45

    def test_parse_date_iso_format_with_timezone(self):
        """Test parsing ISO format with timezone."""
        result = parse_date("2024-01-15 10:30:45+00:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_with_z_suffix(self):
        """Test parsing date with Z suffix (UTC indicator)."""
        result = parse_date("2024-01-15T10:30:45Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45

    def test_parse_date_with_whitespace(self):
        """Test parsing date with leading/trailing whitespace."""
        result = parse_date("  2024-01-15  ")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_various_formats(self):
        """Test parsing various valid date formats."""
        # Date only
        assert parse_date("2024-12-25") is not None
        
        # DateTime without timezone
        assert parse_date("2024-12-25 15:30:00") is not None
        
        # DateTime with +00:00 timezone
        assert parse_date("2024-12-25 15:30:00+00:00") is not None

    def test_parse_date_invalid_format(self):
        """Test parsing invalid date format returns None."""
        assert parse_date("not-a-date") is None
        assert parse_date("2024/01/15") is None
        assert parse_date("15-01-2024") is None
        assert parse_date("January 15, 2024") is None

    def test_parse_date_invalid_date_values(self):
        """Test parsing invalid date values returns None."""
        assert parse_date("2024-13-01") is None 
        assert parse_date("2024-01-32") is None 
        assert parse_date("2024-02-30") is None  

    def test_parse_date_edge_cases(self):
        """Test parsing edge case dates."""
        # Leap year
        result = parse_date("2024-02-29")
        assert result is not None
        assert result.day == 29
        
        # First day of year
        result = parse_date("2024-01-01")
        assert result is not None
        
        # Last day of year
        result = parse_date("2024-12-31")
        assert result is not None


class TestComputeOverlapDays:
    """Test the compute_overlap_days function."""

    def test_compute_overlap_days_valid_range(self):
        """Test computing overlap days with valid date range."""
        result = compute_overlap_days("2024-01-01", "2024-01-10")
        assert result == 9  # 10 - 1 = 9 days

    def test_compute_overlap_days_reversed_dates(self):
        """Test computing overlap days with reversed dates (end before start)."""
        result = compute_overlap_days("2024-01-10", "2024-01-01")
        assert result == 0 

    def test_compute_overlap_days_both_none(self):
        """Test computing overlap days with both dates None."""
        result = compute_overlap_days(None, None)
        assert result is None

    def test_compute_overlap_days_invalid_start(self):
        """Test computing overlap days with invalid start date."""
        result = compute_overlap_days("not-a-date", "2024-01-10")
        assert result is None

    def test_compute_overlap_days_invalid_end(self):
        """Test computing overlap days with invalid end date."""
        result = compute_overlap_days("2024-01-01", "not-a-date")
        assert result is None

    def test_compute_overlap_days_with_datetime_strings(self):
        """Test computing overlap days with datetime strings (not just dates)."""
        result = compute_overlap_days(
            "2024-01-01 10:00:00",
            "2024-01-05 15:30:00"
        )
        assert result == 4  

    def test_compute_overlap_days_with_timezone(self):
        """Test computing overlap days with timezone information."""
        result = compute_overlap_days(
            "2024-01-01 10:00:00+00:00",
            "2024-01-05 15:30:00+00:00"
        )
        assert result == 4

    def test_compute_overlap_days_across_years(self):
        """Test computing overlap days across year boundaries."""
        result = compute_overlap_days("2023-12-25", "2024-01-05")
        assert result == 11 

    def test_compute_overlap_days_empty_strings(self):
        """Test computing overlap days with empty strings."""
        result = compute_overlap_days("", "2024-01-10")
        assert result is None
        
        result = compute_overlap_days("2024-01-01", "")
        assert result is None

    def test_compute_overlap_days_with_z_suffix(self):
        """Test computing overlap days with Z suffix timestamps."""
        result = compute_overlap_days(
            "2024-01-01T10:00:00Z",
            "2024-01-05T15:30:00Z"
        )
        assert result == 4