"""
Fire Mode Analyzer — NOiSEMaKER
Determines fire mode eligibility, maintenance, and exit for songs
based on Spotify popularity vs user baseline.

System:
- Entry: song popularity must exceed user baseline (strictly greater)
- 5-day guaranteed window once activated
- Maintenance after day 5: exit if below peak for 2 consecutive days
- Re-entry: must exceed previous fire mode peak by at least 1
- 4 levels based on baseline (informational only, same rules for all)
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FireModeAnalyzer:
    """
    Analyzes songs for Fire Mode eligibility and maintenance.

    Levels (informational — same rules for all):
    - Level 1 (baseline 0-3): Rising
    - Level 2 (baseline 4-10): Building
    - Level 3 (baseline 11-25): Established
    - Level 4 (baseline 26+): Breaking Out
    """

    LEVEL_BRACKETS = [
        (3, 1, "Rising"),
        (10, 2, "Building"),
        (25, 3, "Established"),
        (None, 4, "Breaking Out"),
    ]

    GUARANTEED_DAYS = 5
    CONSECUTIVE_DAYS_TO_EXIT = 2

    def __init__(self):
        logger.info("Fire Mode analyzer initialized")

    def calculate_fire_mode_eligibility(
        self,
        user_baseline: int,
        song_current_popularity: int,
        song_fire_mode_active: bool,
        song_fire_mode_start_date: Optional[str],
        song_peak_popularity: int,
        days_below_peak: int,
        song_previous_fire_peak: int = 0
    ) -> Dict[str, Any]:
        """
        Determine fire mode status for a song.

        Args:
            user_baseline: User's baseline popularity (0-100)
            song_current_popularity: Current Spotify popularity
            song_fire_mode_active: Is fire mode currently active?
            song_fire_mode_start_date: When fire mode started (ISO format or None)
            song_peak_popularity: Highest popularity during current fire mode
            days_below_peak: Consecutive days below peak (caller tracks this)
            song_previous_fire_peak: Peak from LAST fire mode session (0 if never)

        Returns:
            Dict with eligible, should_maintain, should_exit, level, level_label,
            new_peak, days_below_peak, reason
        """
        level, level_label = self.determine_level_from_baseline(user_baseline)
        new_peak = False

        # --- SONG IS NOT IN FIRE MODE ---
        if not song_fire_mode_active:
            if song_previous_fire_peak > 0:
                # RE-ENTRY: must exceed previous peak by at least 1
                eligible = song_current_popularity > song_previous_fire_peak
                reason = (
                    f"Re-entry check: popularity {song_current_popularity} "
                    f"vs previous peak {song_previous_fire_peak} "
                    f"(need {song_previous_fire_peak + 1}+)"
                )
            else:
                # FIRST ENTRY: must be strictly greater than baseline
                eligible = song_current_popularity > user_baseline
                reason = (
                    f"First entry check: popularity {song_current_popularity} "
                    f"vs baseline {user_baseline} (need {user_baseline + 1}+)"
                )

            return {
                'eligible': eligible,
                'should_maintain': False,
                'should_exit': False,
                'level': level,
                'level_label': level_label,
                'new_peak': False,
                'days_below_peak': 0,
                'reason': reason
            }

        # --- SONG IS IN FIRE MODE ---

        # Check if song set a new peak
        if song_current_popularity > song_peak_popularity:
            new_peak = True

        # Calculate days in fire mode
        days_in_fire_mode = self._days_since(song_fire_mode_start_date)

        # GUARANTEED WINDOW: first 5 days, always maintain
        if days_in_fire_mode < self.GUARANTEED_DAYS:
            return {
                'eligible': True,
                'should_maintain': True,
                'should_exit': False,
                'level': level,
                'level_label': level_label,
                'new_peak': new_peak,
                'days_below_peak': 0,
                'reason': (
                    f"Guaranteed window: day {days_in_fire_mode + 1} of "
                    f"{self.GUARANTEED_DAYS}"
                    f"{' (new peak!)' if new_peak else ''}"
                )
            }

        # MAINTENANCE: after day 5
        if song_current_popularity >= song_peak_popularity:
            # At or above peak — reset below-peak counter
            return {
                'eligible': True,
                'should_maintain': True,
                'should_exit': False,
                'level': level,
                'level_label': level_label,
                'new_peak': new_peak,
                'days_below_peak': 0,
                'reason': (
                    f"Maintenance: at/above peak "
                    f"({song_current_popularity} >= {song_peak_popularity})"
                    f"{' — new peak!' if new_peak else ''}"
                )
            }

        # Below peak
        updated_days_below = days_below_peak + 1

        if updated_days_below >= self.CONSECUTIVE_DAYS_TO_EXIT:
            # EXIT: 2 consecutive days below peak
            return {
                'eligible': False,
                'should_maintain': False,
                'should_exit': True,
                'level': level,
                'level_label': level_label,
                'new_peak': False,
                'days_below_peak': updated_days_below,
                'reason': (
                    f"Exit: {updated_days_below} consecutive days below peak "
                    f"({song_current_popularity} < {song_peak_popularity})"
                )
            }

        # Below peak but haven't hit 2 consecutive days yet
        return {
            'eligible': True,
            'should_maintain': True,
            'should_exit': False,
            'level': level,
            'level_label': level_label,
            'new_peak': False,
            'days_below_peak': updated_days_below,
            'reason': (
                f"Maintenance: below peak day {updated_days_below} of "
                f"{self.CONSECUTIVE_DAYS_TO_EXIT} "
                f"({song_current_popularity} < {song_peak_popularity})"
            )
        }

    def _days_since(self, iso_date: Optional[str]) -> int:
        """Calculate days since a given ISO date string."""
        if not iso_date:
            return 0
        try:
            start = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            now = datetime.utcnow()
            if start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            delta = now - start
            return max(0, delta.days)
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing fire mode start date '{iso_date}': {e}")
            return 0

    def determine_level_from_baseline(self, baseline: int) -> tuple:
        """
        Determine level and label from baseline popularity.

        Returns:
            Tuple of (level: int, label: str)
        """
        for max_val, level, label in self.LEVEL_BRACKETS:
            if max_val is None or baseline <= max_val:
                return level, label
        return 4, "Breaking Out"

    def get_level_description(self, level: int) -> str:
        """Get human-readable level description."""
        descriptions = {
            1: "Rising (baseline 0-3)",
            2: "Building (baseline 4-10)",
            3: "Established (baseline 11-25)",
            4: "Breaking Out (baseline 26+)"
        }
        return descriptions.get(level, "Unknown Level")


# Global instance
fire_mode_analyzer = FireModeAnalyzer()


# Convenience functions
def check_fire_mode(
    user_baseline: int,
    song_current_popularity: int,
    song_fire_mode_active: bool,
    song_fire_mode_start_date: Optional[str],
    song_peak_popularity: int,
    days_below_peak: int,
    song_previous_fire_peak: int = 0
) -> Dict[str, Any]:
    """Check fire mode status for a song."""
    return fire_mode_analyzer.calculate_fire_mode_eligibility(
        user_baseline,
        song_current_popularity,
        song_fire_mode_active,
        song_fire_mode_start_date,
        song_peak_popularity,
        days_below_peak,
        song_previous_fire_peak
    )


def get_level(baseline: int) -> tuple:
    """Determine level and label from baseline."""
    return fire_mode_analyzer.determine_level_from_baseline(baseline)


def describe_level(level: int) -> str:
    """Get level description."""
    return fire_mode_analyzer.get_level_description(level)
