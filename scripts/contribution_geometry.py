"""Contribution Atlas geometry engine.

Calculates isometric projection, tile footprints, 3D prism vertices,
logarithmic tower heights, and occlusion depth sorting.
"""
from __future__ import annotations

import datetime as dt
import math
from typing import Any, Dict, List, Optional, Tuple


def calculate_tower_height(
    count: int,
    ref_max: int = 26,
    h_min: float = 10.0,
    h_max: float = 65.0,
    h_cap: float = 76.0,
) -> float:
    """Calculate logarithmic tower height from contribution count.
    
    Monotonic: height strictly increases with count.
    Zero count produces height = 0.0.
    """
    if count <= 0:
        return 0.0
    safe_max = max(1, ref_max)
    scale = math.log(1.0 + count) / math.log(1.0 + safe_max)
    h = h_min + (h_max - h_min) * scale
    return min(h_cap, round(h, 2))


def get_intensity_level(count: int) -> int:
    """Map contribution count to one of 5 discrete intensity levels (0 to 4)."""
    if count <= 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 6:
        return 2
    elif count <= 14:
        return 3
    else:
        return 4


class IsometricGrid:
    """Configurable isometric projection engine for GitHub contribution calendar."""

    def __init__(
        self,
        origin_x: float = 160.0,
        origin_y: float = 230.0,
        dx_w: float = 17.2,
        dy_w: float = 1.4,
        dx_d: float = -8.5,
        dy_d: float = 7.8,
        tile_scale: float = 0.88,
        h_min: float = 10.0,
        h_max: float = 65.0,
        h_cap: float = 76.0,
    ):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.dx_w = dx_w
        self.dy_w = dy_w
        self.dx_d = dx_d
        self.dy_d = dy_d
        self.tile_scale = tile_scale
        self.h_min = h_min
        self.h_max = h_max
        self.h_cap = h_cap

    def project_cell(self, w: int, d: int) -> Tuple[float, float]:
        """Project calendar week index w and weekday d (0..6) to base (x, y)."""
        x = self.origin_x + w * self.dx_w + d * self.dx_d
        y = self.origin_y + w * self.dy_w + d * self.dy_d
        return round(x, 2), round(y, 2)

    def compute_tile_corners(self, cx: float, cy: float) -> Dict[str, Tuple[float, float]]:
        """Compute the 4 ground corners of an isometric diamond tile centered at (cx, cy)."""
        # Half vectors for diamond footprint
        hwx = (self.dx_w * self.tile_scale) / 2.0
        hwy = (self.dy_w * self.tile_scale) / 2.0
        hdx = (self.dx_d * self.tile_scale) / 2.0
        hdy = (self.dy_d * self.tile_scale) / 2.0

        # Back corner (topmost in Y)
        top = (round(cx - hwx - hdx, 2), round(cy - hwy - hdy, 2))
        # Right corner
        right = (round(cx + hwx - hdx, 2), round(cy + hwy - hdy, 2))
        # Front corner (bottommost in Y)
        bottom = (round(cx + hwx + hdx, 2), round(cy + hwy + hdy, 2))
        # Left corner
        left = (round(cx - hwx + hdx, 2), round(cy - hwy + hdy, 2))

        return {"top": top, "right": right, "bottom": bottom, "left": left}

    def compute_day_towers(
        self,
        days: List[Dict[str, Any]],
        ref_max: Optional[int] = None,
        height_progress: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """Compute complete geometry for all calendar days.
        
        Args:
            days: Ordered list of contribution day dicts (date, count).
            ref_max: Reference maximum for logarithmic scaling (defaults to max in days).
            height_progress: Global animation progress (0.0 to 1.0) or custom scale factor.
        
        Returns:
            List of tower dicts sorted back-to-front for proper occlusion.
        """
        if not days:
            return []

        sorted_days = sorted(days, key=lambda d: d["date"])
        if ref_max is None:
            max_c = max((d["count"] for d in sorted_days), default=1)
            ref_max = max(1, max_c)

        # Map dates to calendar weeks
        # Determine base date
        first_d_obj = dt.date.fromisoformat(sorted_days[0]["date"])
        # Find Sunday of first week
        gh_weekday_0 = (first_d_obj.weekday() + 1) % 7
        first_sunday = first_d_obj - dt.timedelta(days=gh_weekday_0)

        towers: List[Dict[str, Any]] = []

        for d in sorted_days:
            date_obj = dt.date.fromisoformat(d["date"])
            gh_weekday = (date_obj.weekday() + 1) % 7
            week_idx = (date_obj - first_sunday).days // 7
            count = d["count"]

            cx, cy = self.project_cell(week_idx, gh_weekday)
            ground = self.compute_tile_corners(cx, cy)

            target_height = calculate_tower_height(
                count,
                ref_max=ref_max,
                h_min=self.h_min,
                h_max=self.h_max,
                h_cap=self.h_cap,
            )
            current_height = round(target_height * height_progress, 2)
            intensity = get_intensity_level(count)

            # Top corners shifted upward by current_height
            top_corners = {
                "top": (ground["top"][0], round(ground["top"][1] - current_height, 2)),
                "right": (ground["right"][0], round(ground["right"][1] - current_height, 2)),
                "bottom": (ground["bottom"][0], round(ground["bottom"][1] - current_height, 2)),
                "left": (ground["left"][0], round(ground["left"][1] - current_height, 2)),
            }

            # Depth metric for back-to-front rendering:
            # Elements with smaller base Y or (week_idx + gh_weekday) are farther back.
            # In isometric projection, cy increases as we move frontward.
            depth = cy + (week_idx * 0.01)

            towers.append({
                "date": d["date"],
                "count": count,
                "week_idx": week_idx,
                "weekday_idx": gh_weekday,
                "cx": cx,
                "cy": cy,
                "ground": ground,
                "top": top_corners,
                "target_height": target_height,
                "current_height": current_height,
                "intensity": intensity,
                "depth": depth,
            })

        # Sort back-to-front (depth ascending)
        towers.sort(key=lambda t: t["depth"])
        return towers

