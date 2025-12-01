# /backend/tests/test_gantt.py
"""
Tests for Gantt chart functionality.
"""
import pytest
from datetime import date, timedelta

from app.services.gantt_service import calculate_scale, get_date_range_info


class TestCalculateScale:
    """Tests for scale calculation logic."""

    def test_scale_day_for_short_range(self):
        """Should return 'day' for ranges <= 30 days."""
        start = date.today()
        end = start + timedelta(days=15)
        assert calculate_scale(start, end) == "day"

    def test_scale_day_for_30_days(self):
        """Should return 'day' for exactly 30 days."""
        start = date.today()
        end = start + timedelta(days=29)  # 30 days total
        assert calculate_scale(start, end) == "day"

    def test_scale_week_for_medium_range(self):
        """Should return 'week' for ranges 31-180 days."""
        start = date.today()
        end = start + timedelta(days=60)
        assert calculate_scale(start, end) == "week"

    def test_scale_week_for_180_days(self):
        """Should return 'week' for exactly 180 days."""
        start = date.today()
        end = start + timedelta(days=179)  # 180 days total
        assert calculate_scale(start, end) == "week"

    def test_scale_month_for_long_range(self):
        """Should return 'month' for ranges > 180 days."""
        start = date.today()
        end = start + timedelta(days=200)
        assert calculate_scale(start, end) == "month"


class TestDateRangeInfo:
    """Tests for date range information."""

    def test_get_date_range_info(self):
        """Should return correct days, weeks, months."""
        start = date.today()
        end = start + timedelta(days=29)  # 30 days total

        info = get_date_range_info(start, end)

        assert info["total_days"] == 30
        assert info["total_weeks"] == pytest.approx(4.3, rel=0.1)
        assert info["total_months"] == 1.0

