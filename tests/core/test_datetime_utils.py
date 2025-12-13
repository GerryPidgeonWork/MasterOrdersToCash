# ====================================================================================================
# test_datetime_utils.py
# ----------------------------------------------------------------------------------------------------
# Unit tests for core/C07_datetime_utils.py
# ====================================================================================================

from __future__ import annotations

import pytest
from datetime import date, datetime
from core.C07_datetime_utils import (
    parse_date,
    format_date,
    get_start_of_week,
    get_end_of_week,
    get_month_range,
)


class TestParseDate:
    """Tests for parse_date function."""
    
    @pytest.mark.unit
    def test_parse_date_iso_format(self):
        """Test parsing ISO format dates (YYYY-MM-DD)."""
        result = parse_date("2025-11-15")
        assert result == date(2025, 11, 15)
    
    @pytest.mark.unit
    def test_parse_date_uk_format(self):
        """Test parsing UK format dates (DD/MM/YYYY) with auto-detection."""
        # parse_date supports UK format when fmt=None (auto-detection)
        result = parse_date("15/11/2025", fmt=None)
        assert result == date(2025, 11, 15)

    @pytest.mark.unit
    def test_parse_date_invalid(self):
        """Test that invalid dates raise ValueError."""
        # parse_date raises ValueError for invalid dates (doesn't return None)
        with pytest.raises(ValueError):
            parse_date("invalid-date")

    @pytest.mark.unit
    def test_parse_date_none(self):
        """Test that None input raises TypeError."""
        # parse_date raises TypeError for None input
        with pytest.raises(TypeError):
            parse_date(None)


class TestFormatDate:
    """Tests for format_date function."""
    
    @pytest.mark.unit
    def test_format_date_default(self):
        """Test default date formatting (YYYY-MM-DD)."""
        test_date = date(2025, 11, 15)
        result = format_date(test_date)
        assert result == "2025-11-15"
    
    @pytest.mark.unit
    def test_format_date_custom(self):
        """Test custom date formatting."""
        test_date = date(2025, 11, 15)
        result = format_date(test_date, "%d/%m/%Y")
        assert result == "15/11/2025"
    
    @pytest.mark.unit
    def test_format_date_shorthand(self):
        """Test shorthand date formatting (yy.mm.dd)."""
        test_date = date(2025, 11, 15)
        result = format_date(test_date, "%y.%m.%d")
        assert result == "25.11.15"


class TestWeekHelpers:
    """Tests for week-related functions."""
    
    @pytest.mark.unit
    def test_get_start_of_week_monday(self):
        """Test getting Monday from any day of the week."""
        # Friday, 2025-11-14 (weekday=4)
        test_date = date(2025, 11, 14)
        result = get_start_of_week(test_date)
        # Should return Monday, 2025-11-10 (weekday=0)
        assert result == date(2025, 11, 10)
        assert result.weekday() == 0  # Monday = 0

    @pytest.mark.unit
    def test_get_start_of_week_already_monday(self):
        """Test that Monday returns itself."""
        # Monday, 2025-11-10
        monday = date(2025, 11, 10)
        result = get_start_of_week(monday)
        assert result == monday
        assert result.weekday() == 0

    @pytest.mark.unit
    def test_get_end_of_week_sunday(self):
        """Test getting Sunday from any day of the week."""
        # Friday, 2025-11-14 (weekday=4)
        test_date = date(2025, 11, 14)
        result = get_end_of_week(test_date)
        # Should return Sunday, 2025-11-16 (weekday=6)
        assert result == date(2025, 11, 16)
        assert result.weekday() == 6  # Sunday = 6


class TestMonthRange:
    """Tests for get_month_range function."""
    
    @pytest.mark.unit
    def test_get_month_range_november(self):
        """Test getting month range for November 2025."""
        start, end = get_month_range(2025, 11)
        assert start == date(2025, 11, 1)
        assert end == date(2025, 11, 30)
    
    @pytest.mark.unit
    def test_get_month_range_february_leap_year(self):
        """Test February in a leap year."""
        start, end = get_month_range(2024, 2)
        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)
    
    @pytest.mark.unit
    def test_get_month_range_february_non_leap(self):
        """Test February in a non-leap year."""
        start, end = get_month_range(2025, 2)
        assert start == date(2025, 2, 1)
        assert end == date(2025, 2, 28)
