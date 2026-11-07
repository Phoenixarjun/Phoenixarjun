"""Unit tests for Contribution Atlas geometry and isometric projection."""
from __future__ import annotations

import unittest

from scripts.contribution_geometry import (
    IsometricGrid,
    calculate_tower_height,
    get_intensity_level,
)


class TestContributionGeometry(unittest.TestCase):

    def test_height_monotonicity(self):
        counts = [0, 1, 2, 3, 5, 10, 15, 26, 50, 100]
        heights = [calculate_tower_height(c, ref_max=26) for c in counts]
        # Check zero count is 0
        self.assertEqual(heights[0], 0.0)
        # Check strictly monotonic for c > 0
        for i in range(1, len(heights) - 1):
            self.assertLessEqual(heights[i], heights[i + 1])

    def test_height_visual_cap(self):
        h = calculate_tower_height(10000, ref_max=26, h_cap=76.0)
        self.assertEqual(h, 76.0)

    def test_intensity_levels(self):
        self.assertEqual(get_intensity_level(0), 0)
        self.assertEqual(get_intensity_level(1), 1)
        self.assertEqual(get_intensity_level(2), 1)
        self.assertEqual(get_intensity_level(3), 2)
        self.assertEqual(get_intensity_level(6), 2)
        self.assertEqual(get_intensity_level(7), 3)
        self.assertEqual(get_intensity_level(14), 3)
        self.assertEqual(get_intensity_level(15), 4)
        self.assertEqual(get_intensity_level(26), 4)

    def test_day_to_tower_mapping(self):
        grid = IsometricGrid()
        days = [
            {"date": "2026-01-04", "count": 0},  # Sunday
            {"date": "2026-01-05", "count": 3},  # Monday
            {"date": "2026-01-06", "count": 12}, # Tuesday
        ]
        towers = grid.compute_day_towers(days, ref_max=12)
        self.assertEqual(len(towers), 3)

        # Map back to date
        t_map = {t["date"]: t for t in towers}
        self.assertEqual(t_map["2026-01-04"]["current_height"], 0.0)
        self.assertGreater(t_map["2026-01-05"]["current_height"], 0.0)
        self.assertGreater(t_map["2026-01-06"]["current_height"], t_map["2026-01-05"]["current_height"])

    def test_occlusion_depth_sorting(self):
        grid = IsometricGrid()
        # Days across multiple weeks and days
        days = [
            {"date": "2026-01-04", "count": 2}, # Week 0, Sunday
            {"date": "2026-01-10", "count": 5}, # Week 0, Saturday
            {"date": "2026-01-11", "count": 1}, # Week 1, Sunday
            {"date": "2026-01-17", "count": 4}, # Week 1, Saturday
        ]
        towers = grid.compute_day_towers(days)
        # Verify sorted ascending by depth
        depths = [t["depth"] for t in towers]
        self.assertEqual(depths, sorted(depths))

    def test_animation_progress_scaling(self):
        grid = IsometricGrid()
        days = [{"date": "2026-01-05", "count": 10}]
        towers_0 = grid.compute_day_towers(days, height_progress=0.0)
        self.assertEqual(towers_0[0]["current_height"], 0.0)

        towers_half = grid.compute_day_towers(days, height_progress=0.5)
        towers_full = grid.compute_day_towers(days, height_progress=1.0)
        self.assertAlmostEqual(towers_half[0]["current_height"], towers_full[0]["target_height"] * 0.5, places=1)
        self.assertEqual(towers_full[0]["current_height"], towers_full[0]["target_height"])


if __name__ == "__main__":
    unittest.main()

