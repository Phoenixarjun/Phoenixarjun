"""Contribution Atlas metrics engine.

Computes verified statistics from GitHub contribution calendar data:
- Total contributions
- Active days (count > 0)
- Busiest day (max count, date, labelled 'contributions')
- Current streak (consecutive active days ending today or yesterday without arbitrary timezone shift)
- Longest streak (longest consecutive active days within reporting window)
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional, Tuple


def parse_date(date_str: str) -> dt.date:
    """Safely parse ISO date string (YYYY-MM-DD)."""
    return dt.date.fromisoformat(date_str)


def validate_contribution_data(data: Dict[str, Any], expected_username: str = "Phoenixarjun") -> List[str]:
    """Validate raw contribution dataset structure and integrity.
    
    Returns a list of warning/error strings (empty if completely valid).
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return ["Contribution data is not a valid dictionary"]

    username = data.get("username", "")
    if username.lower() != expected_username.lower():
        errors.append(f"Username '{username}' does not match expected '{expected_username}'")

    days = data.get("days")
    if not isinstance(days, list) or len(days) == 0:
        errors.append("No contribution days found in dataset")
        return errors

    seen_dates = set()
    for i, d in enumerate(days):
        if not isinstance(d, dict):
            errors.append(f"Day record at index {i} is not a dictionary")
            continue
        date_str = d.get("date")
        if not date_str:
            errors.append(f"Missing date at index {i}")
            continue
        try:
            d_date = parse_date(date_str)
        except Exception as e:
            errors.append(f"Invalid date format '{date_str}' at index {i}: {e}")
            continue

        if date_str in seen_dates:
            errors.append(f"Duplicate date detected: {date_str}")
        seen_dates.add(date_str)

        count = d.get("count")
        if count is None or not isinstance(count, int) or count < 0:
            errors.append(f"Invalid contribution count {count} for date {date_str}")

    return errors


def compute_metrics(
    days: List[Dict[str, Any]],
    total_reported: Optional[int] = None,
    reference_date: Optional[dt.date] = None,
) -> Dict[str, Any]:
    """Calculate verified contribution metrics from daily records.
    
    Args:
        days: List of day records with 'date' (YYYY-MM-DD) and 'count' (int).
        total_reported: Optional total reported directly by GitHub API.
        reference_date: Optional reference 'today' date (defaults to max date in days or UTC today).
    
    Returns:
        Dict with total, active_days, busiest_day, current_streak, longest_streak, and metadata.
    """
    if not days:
        return {
            "total_contributions": 0,
            "active_days": 0,
            "busiest_day": {"count": 0, "date": "", "label": "0 contributions"},
            "current_streak": 0,
            "longest_streak": 0,
            "total_days": 0,
            "start_date": "",
            "end_date": "",
        }

    # Sort strictly by date ascending
    sorted_days = sorted(days, key=lambda d: d["date"])
    total_days = len(sorted_days)
    start_date = sorted_days[0]["date"]
    end_date = sorted_days[-1]["date"]

    sum_count = sum(d["count"] for d in sorted_days)
    total_contributions = total_reported if total_reported is not None else sum_count
    active_days = sum(1 for d in sorted_days if d["count"] > 0)

    # Busiest day (deterministic tie-breaker: first occurrence of max)
    busiest_rec = max(sorted_days, key=lambda d: d["count"])
    busiest_day = {
        "count": busiest_rec["count"],
        "date": busiest_rec["date"],
        "label": f"{busiest_rec['count']} contributions",
    }

    # Longest streak
    longest_streak = 0
    running_streak = 0
    for d in sorted_days:
        if d["count"] > 0:
            running_streak += 1
            if running_streak > longest_streak:
                longest_streak = running_streak
        else:
            running_streak = 0

    # Current streak:
    # Consecutive active days ending today or yesterday, allowing for the fact
    # that today's contribution window may still be in progress.
    # If the streak is broken, returns 0.
    last_day_obj = parse_date(sorted_days[-1]["date"])
    ref_date = reference_date or last_day_obj

    current_streak = 0
    # Map dates to counts for direct calendar arithmetic
    day_map = {d["date"]: d["count"] for d in sorted_days}

    # Check starting from ref_date
    check_date = ref_date
    if day_map.get(check_date.isoformat(), 0) > 0:
        # Streak includes today
        while day_map.get(check_date.isoformat(), 0) > 0:
            current_streak += 1
            check_date -= dt.timedelta(days=1)
    else:
        # Today is 0 or pending; check if streak was active as of yesterday
        yesterday = check_date - dt.timedelta(days=1)
        if day_map.get(yesterday.isoformat(), 0) > 0:
            check_date = yesterday
            while day_map.get(check_date.isoformat(), 0) > 0:
                current_streak += 1
                check_date -= dt.timedelta(days=1)
        else:
            current_streak = 0

    return {
        "total_contributions": total_contributions,
        "active_days": active_days,
        "busiest_day": busiest_day,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_days": total_days,
        "start_date": start_date,
        "end_date": end_date,
    }

