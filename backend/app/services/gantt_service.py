# /backend/app/services/gantt_service.py
"""
Gantt chart business logic.
"""
from datetime import date


def calculate_scale(start_date: date, end_date: date) -> str:
    """
    Calculate the appropriate scale for displaying a Gantt chart.

    Rules:
    - totalDays <= 30 → "day"
    - 30 < totalDays <= 180 → "week"
    - totalDays > 180 → "month"

    Args:
        start_date: Activity start date
        end_date: Activity end date

    Returns:
        Scale string: "day", "week", or "month"
    """
    total_days = (end_date - start_date).days + 1

    if total_days <= 30:
        return "day"
    elif total_days <= 180:
        return "week"
    else:
        return "month"


def get_date_range_info(start_date: date, end_date: date) -> dict:
    """
    Get detailed information about a date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Dictionary with days, weeks, months count
    """
    total_days = (end_date - start_date).days + 1
    total_weeks = total_days / 7
    total_months = total_days / 30

    return {
        "total_days": total_days,
        "total_weeks": round(total_weeks, 1),
        "total_months": round(total_months, 1),
    }

