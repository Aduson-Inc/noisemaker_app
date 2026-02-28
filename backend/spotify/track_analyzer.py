"""
Track Analyzer Module
Provides TrackMetrics dataclass and TrackAnalyzer for post distribution and milestone checking.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PromotionStage(Enum):
    """Song promotion stages based on days_in_promotion."""
    upcoming = "upcoming"
    building = "building"
    live = "live"
    twilight = "twilight"
    retired = "retired"


@dataclass
class TrackMetrics:
    """Metrics for a single track used by the daily processor."""
    track_id: str
    fire_mode_active: bool = False
    fire_mode_eligible: bool = False
    daily_average: float = 0.0
    promotion_stage: PromotionStage = PromotionStage.building
    focus_percentage: float = 0.0


class TrackAnalyzer:
    """
    Analyzes track performance and distributes daily posts.
    """

    # Post allocation percentages by stage (from content pipeline design)
    STAGE_WEIGHTS = {
        PromotionStage.upcoming: 0.20,
        PromotionStage.building: 0.20,
        PromotionStage.live: 0.50,
        PromotionStage.twilight: 0.30,
        PromotionStage.retired: 0.0,
    }

    # Fire mode overrides
    FIRE_MODE_WEIGHT = 0.70
    FIRE_MODE_REMAINING = {
        PromotionStage.upcoming: 0.10,
        PromotionStage.building: 0.10,
        PromotionStage.live: 0.20,
        PromotionStage.twilight: 0.0,
    }

    def distribute_daily_posts(
        self, track_metrics: List[TrackMetrics], total_posts: int
    ) -> Dict[str, int]:
        """
        Distribute posts among tracks based on promotion stage and fire mode.

        Args:
            track_metrics: List of track metrics
            total_posts: Total posts to distribute

        Returns:
            Dict mapping track_id to number of posts allocated
        """
        if not track_metrics or total_posts <= 0:
            return {}

        distribution = {}
        fire_track = None

        # Check if any track is in fire mode
        for m in track_metrics:
            if m.fire_mode_active:
                fire_track = m
                break

        if fire_track and len(track_metrics) > 1:
            # Fire mode distribution
            fire_posts = max(1, int(total_posts * self.FIRE_MODE_WEIGHT))
            distribution[fire_track.track_id] = fire_posts
            remaining = total_posts - fire_posts

            non_fire = [m for m in track_metrics if m.track_id != fire_track.track_id]
            if non_fire and remaining > 0:
                per_track = max(1, remaining // len(non_fire))
                for m in non_fire:
                    distribution[m.track_id] = min(per_track, remaining)
                    remaining -= distribution[m.track_id]
                # Distribute leftover
                if remaining > 0:
                    distribution[non_fire[0].track_id] += remaining
        else:
            # Normal distribution by stage weight
            total_weight = sum(
                self.STAGE_WEIGHTS.get(m.promotion_stage, 0.2) for m in track_metrics
            )
            if total_weight == 0:
                total_weight = 1.0

            remaining = total_posts
            for i, m in enumerate(track_metrics):
                weight = self.STAGE_WEIGHTS.get(m.promotion_stage, 0.2)
                if i == len(track_metrics) - 1:
                    posts = remaining
                else:
                    posts = max(1, int(total_posts * (weight / total_weight)))
                    posts = min(posts, remaining)
                distribution[m.track_id] = posts
                remaining -= posts

        # Update focus percentages
        for m in track_metrics:
            allocated = distribution.get(m.track_id, 0)
            m.focus_percentage = (allocated / total_posts * 100) if total_posts > 0 else 0

        return distribution

    def check_milestone_achievements(self, song: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if a song has reached any milestones.
        Feature 7: Skips popularity milestones when popularity is 0/null.

        Args:
            song: Song data dict

        Returns:
            List of milestone dicts
        """
        milestones = []
        days = song.get("days_in_promotion", 0)
        popularity = song.get("spotify_popularity") or 0
        fire_mode = song.get("fire_mode", False)

        # Day milestones
        day_milestones = {7: "first_week", 14: "two_weeks", 28: "four_weeks", 42: "full_cycle"}
        if days in day_milestones:
            milestones.append({
                "type": "promotion_day",
                "milestone": day_milestones[days],
                "days": days,
            })

        # Popularity milestones (skip if no popularity data — Feature 7)
        if popularity > 0:
            pop_thresholds = [10, 20, 30, 40, 50, 60, 70, 80, 90]
            for threshold in pop_thresholds:
                if popularity >= threshold:
                    milestones.append({
                        "type": "popularity",
                        "milestone": f"popularity_{threshold}",
                        "popularity": popularity,
                    })

        # Fire mode milestone
        if fire_mode:
            milestones.append({
                "type": "fire_mode",
                "milestone": "fire_mode_achieved",
            })

        return milestones
