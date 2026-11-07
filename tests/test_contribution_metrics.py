"""Unit tests for contribution metrics calculation and validation."""
from __future__ import annotations

import datetime as dt
import unittest

from scripts.contribution_metrics import compute_metrics, validate_contribution_data


class TestContributionMetrics(unittest.TestCase):

    def test_empty_contributions(self):
        m = compute_metrics([])
        self.assertEqual(m["total_contributions"], 0)
        self.assertEqual(m["active_days"], 0)
        self.assertEqual(m["current_streak"], 0)
        self.assertEqual(m["longest_streak"], 0)
        self.assertEqual(m["busiest_day"]["count"], 0)

    def test_single_active_day(self):
        days = [{"date": "2026-05-10", "count": 5}]
        m = compute_metrics(days, reference_date=dt.date(2026, 5, 10))
        self.assertEqual(m["total_contributions"], 5)
        self.assertEqual(m["active_days"], 1)
        self.assertEqual(m["current_streak"], 1)
        self.assertEqual(m["longest_streak"], 1)
        self.assertEqual(m["busiest_day"]["count"], 5)
        self.assertEqual(m["busiest_day"]["date"], "2026-05-10")

    def test_all_days_active(self):
        days = [
            {"date": f"2026-01-0{i}", "count": i * 2} for i in range(1, 8)
        ]
        m = compute_metrics(days, reference_date=dt.date(2026, 1, 7))
        self.assertEqual(m["total_contributions"], sum(i * 2 for i in range(1, 8)))
        self.assertEqual(m["active_days"], 7)
        self.assertEqual(m["current_streak"], 7)
        self.assertEqual(m["longest_streak"], 7)
        self.assertEqual(m["busiest_day"]["count"], 14)
        self.assertEqual(m["busiest_day"]["date"], "2026-01-07")

    def test_streak_broken_today_but_active_yesterday(self):
        # 3 active days ending yesterday, today is 0 (in-progress day rule)
        days = [
            {"date": "2026-05-01", "count": 3},
            {"date": "2026-05-02", "count": 2},
            {"date": "2026-05-03", "count": 4},
            {"date": "2026-05-04", "count": 0},  # today
        ]
        m = compute_metrics(days, reference_date=dt.date(2026, 5, 4))
        self.assertEqual(m["current_streak"], 3)
        self.assertEqual(m["longest_streak"], 3)
        self.assertEqual(m["active_days"], 3)

    def test_streak_broken_yesterday(self):
        # Both yesterday and today are 0 -> streak broken
        days = [
            {"date": "2026-05-01", "count": 3},
            {"date": "2026-05-02", "count": 2},
            {"date": "2026-05-03", "count": 0},  # yesterday
            {"date": "2026-05-04", "count": 0},  # today
        ]
        m = compute_metrics(days, reference_date=dt.date(2026, 5, 4))
        self.assertEqual(m["current_streak"], 0)
        self.assertEqual(m["longest_streak"], 2)

    def test_longest_streak_separate_from_current(self):
        days = [
            {"date": "2026-03-01", "count": 1},
            {"date": "2026-03-02", "count": 2},
            {"date": "2026-03-03", "count": 1},
            {"date": "2026-03-04", "count": 1},
            {"date": "2026-03-05", "count": 1},  # 5 days
            {"date": "2026-03-06", "count": 0},
            {"date": "2026-03-07", "count": 4},
            {"date": "2026-03-08", "count": 2},  # 2 days (current)
        ]
        m = compute_metrics(days, reference_date=dt.date(2026, 3, 8))
        self.assertEqual(m["current_streak"], 2)
        self.assertEqual(m["longest_streak"], 5)
        self.assertEqual(m["active_days"], 7)

    def test_year_boundary_and_leap_year(self):
        # 2024 is a leap year (Feb 29)
        days = [
            {"date": "2023-12-30", "count": 1},
            {"date": "2023-12-31", "count": 2},
            {"date": "2024-01-01", "count": 3},
            {"date": "2024-02-28", "count": 0},
            {"date": "2024-02-29", "count": 4},
            {"date": "2024-03-01", "count": 1},
        ]
        m = compute_metrics(days, reference_date=dt.date(2024, 3, 1))
        self.assertEqual(m["active_days"], 5)
        self.assertEqual(m["current_streak"], 2)
        self.assertEqual(m["longest_streak"], 3)  # Dec 30, 31, Jan 01

    def test_validation_detects_duplicates_and_invalids(self):
        invalid_data = {
            "username": "Phoenixarjun",
            "days": [
                {"date": "2026-01-01", "count": 2},
                {"date": "2026-01-01", "count": 4},  # duplicate
                {"date": "not-a-date", "count": 1},  # invalid date
                {"date": "2026-01-03", "count": -5},  # negative count
            ],
        }
        errors = validate_contribution_data(invalid_data, expected_username="Phoenixarjun")
        self.assertTrue(any("Duplicate date" in e for e in errors))
        self.assertTrue(any("Invalid date format" in e for e in errors))
        self.assertTrue(any("Invalid contribution count" in e for e in errors))

    def test_validation_username_mismatch(self):
        data = {"username": "WrongUser", "days": [{"date": "2026-01-01", "count": 1}]}
        errors = validate_contribution_data(data, expected_username="Phoenixarjun")
        self.assertTrue(any("does not match" in e for e in errors))

    def test_extremely_high_daily_count(self):
        days = [
            {"date": "2026-04-01", "count": 1250},
            {"date": "2026-04-02", "count": 3},
        ]
        m = compute_metrics(days, reference_date=dt.date(2026, 4, 2))
        self.assertEqual(m["busiest_day"]["count"], 1250)
        self.assertEqual(m["total_contributions"], 1253)


if __name__ == "__main__":
    unittest.main()

