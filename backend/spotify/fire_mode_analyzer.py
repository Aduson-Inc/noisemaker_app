"""
Fire Mode Analyzer Module
Implements the 4-tier Fire Mode system with phase-based maintenance requirements.
All increases are ABSOLUTE points, not percentages.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
Specification: PHASE_A_PLANNING_AND_FIRE_MODE_SPECIFICATION.md
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FireModeAnalyzer:
    """
    Analyzes songs for Fire Mode eligibility and maintenance.

    4-Tier System:
    - Tier 1 (0-10% baseline): 3-phase maintenance
    - Tier 2 (11-20% baseline): 3-phase maintenance
    - Tier 3 (21-30% baseline): 3-phase maintenance
    - Tier 4 (31-100% baseline): 7-day lookback maintenance

    All increases are ABSOLUTE points (e.g., +2 points, not 2% of current score).
    """

    def __init__(self):
        """Initialize Fire Mode analyzer."""
        logger.info("Fire Mode analyzer initialized")

    def calculate_fire_mode_eligibility(
        self,
        user_baseline: int,
        song_current_popularity: int,
        song_fire_mode_active: bool,
        song_fire_mode_start_date: str,
        song_peak_popularity: int,
        song_popularity_history: List[Dict[str, Any]],
        has_been_on_fire_before: bool = False
    ) -> Dict[str, Any]:
        """
        Determines if a song qualifies for Fire Mode or should maintain/exit Fire Mode.

        Args:
            user_baseline (int): User's baseline popularity average (0-100)
            song_current_popularity (int): Current popularity score for this song
            song_fire_mode_active (bool): Is Fire Mode currently active for this song?
            song_fire_mode_start_date (str): When Fire Mode started (ISO format)
            song_peak_popularity (int): Highest popularity score achieved while in Fire Mode
            song_popularity_history (List[Dict]): Recent daily popularity scores
                                                  [{date: str, score: int}, ...]
            has_been_on_fire_before (bool): Has this song ever been on Fire Mode before?
                                            Used to determine entry vs re-entry logic.

        Returns:
            dict with:
                - eligible: bool - Can enter Fire Mode
                - should_maintain: bool - Should stay in Fire Mode
                - should_exit: bool - Should exit Fire Mode
                - tier: int (1-4)
                - phase: Optional[int] (1-3 for Tiers 1-3, None for Tier 4)
                - check_frequency: str ('daily')
                - reason: str - Explanation of decision
        """

        # Determine tier based on baseline
        if user_baseline <= 10:
            tier = 1
        elif user_baseline <= 20:
            tier = 2
        elif user_baseline <= 30:
            tier = 3
        else:  # 31-100
            tier = 4

        # Check if song can ENTER Fire Mode (not currently active)
        if not song_fire_mode_active:
            if not has_been_on_fire_before:
                # FIRST ENTRY: Simple baseline check
                eligible = song_current_popularity >= user_baseline
                reason = f'First entry check: Song {song_current_popularity} vs baseline {user_baseline}'
            else:
                # RE-ENTRY: Must meet tier maintenance requirements
                # This prevents songs from bouncing in/out easily
                eligible = self._check_reentry_requirements(
                    tier, song_popularity_history, song_current_popularity, user_baseline
                )
                reason = f'Re-entry check (tier {tier}): Song {song_current_popularity} must meet maintenance requirements'

            return {
                'eligible': eligible,
                'should_maintain': False,
                'should_exit': False,
                'tier': tier,
                'phase': None,
                'check_frequency': 'daily',
                'reason': reason
            }

        # Song is ALREADY in Fire Mode - check maintenance requirements

        # TIER 4: Daily check with 7-day lookback, need +3 points over 7 days
        if tier == 4:
            seven_days_ago_score = self._get_score_n_days_ago(song_popularity_history, 7)

            if seven_days_ago_score is None:
                # Not enough history yet (less than 7 days), maintain Fire Mode
                return {
                    'eligible': True,
                    'should_maintain': True,
                    'should_exit': False,
                    'tier': tier,
                    'phase': None,
                    'check_frequency': 'daily',
                    'reason': 'Tier 4: Insufficient 7-day history (guaranteed 7 days minimum)'
                }

            increase_needed = 3  # ABSOLUTE points, not percentage
            actual_increase = song_current_popularity - seven_days_ago_score
            should_maintain = actual_increase >= increase_needed

            return {
                'eligible': True,
                'should_maintain': should_maintain,
                'should_exit': not should_maintain,
                'tier': tier,
                'phase': None,
                'check_frequency': 'daily',
                'reason': f'Tier 4: 7-day increase {actual_increase} points (need +{increase_needed} points)'
            }

        # TIERS 1-3: Daily check with phase-based requirements

        # Determine which phase the song is in based on current popularity
        if song_current_popularity < 20:
            # Phase 1: Below 20% - need +2 points every 2 days
            phase = 1
            increase_needed = 2  # ABSOLUTE points
            check_days = 2
        elif song_current_popularity < 30:
            # Phase 2: 20-30% - need +1 point every 2 days
            phase = 2
            increase_needed = 1  # ABSOLUTE points
            check_days = 2
        else:
            # Phase 3: Above 30% - maintain peak, 3 days grace
            phase = 3

            # Check if we've had no increase for 3 days
            three_days_ago_score = self._get_score_n_days_ago(song_popularity_history, 3)

            if three_days_ago_score is None:
                # Not enough history, maintain
                return {
                    'eligible': True,
                    'should_maintain': True,
                    'should_exit': False,
                    'tier': tier,
                    'phase': phase,
                    'check_frequency': 'daily',
                    'reason': f'Phase 3: Insufficient history, maintaining'
                }

            # No increase in 3 days = exit Fire Mode
            if song_current_popularity <= three_days_ago_score:
                return {
                    'eligible': True,
                    'should_maintain': False,
                    'should_exit': True,
                    'tier': tier,
                    'phase': phase,
                    'check_frequency': 'daily',
                    'reason': f'Phase 3: No increase in 3 days ({three_days_ago_score} -> {song_current_popularity})'
                }

            # Check if +1 point past peak = reactivate/maintain
            if song_current_popularity >= song_peak_popularity + 1:
                return {
                    'eligible': True,
                    'should_maintain': True,
                    'should_exit': False,
                    'tier': tier,
                    'phase': phase,
                    'check_frequency': 'daily',
                    'reason': f'Phase 3: Exceeded peak by +1 point ({song_peak_popularity} -> {song_current_popularity})'
                }

            # Maintaining within peak
            return {
                'eligible': True,
                'should_maintain': True,
                'should_exit': False,
                'tier': tier,
                'phase': phase,
                'check_frequency': 'daily',
                'reason': f'Phase 3: Maintaining at {song_current_popularity}'
            }

        # Phase 1 or 2: Check if growth requirement met
        n_days_ago_score = self._get_score_n_days_ago(song_popularity_history, check_days)

        if n_days_ago_score is None:
            # Not enough history yet, maintain
            return {
                'eligible': True,
                'should_maintain': True,
                'should_exit': False,
                'tier': tier,
                'phase': phase,
                'check_frequency': 'daily',
                'reason': f'Phase {phase}: Insufficient {check_days}-day history, maintaining'
            }

        actual_increase = song_current_popularity - n_days_ago_score
        should_maintain = actual_increase >= increase_needed

        return {
            'eligible': True,
            'should_maintain': should_maintain,
            'should_exit': not should_maintain,
            'tier': tier,
            'phase': phase,
            'check_frequency': 'daily',
            'reason': f'Phase {phase}: {check_days}-day increase {actual_increase} points (need +{increase_needed} points)'
        }

    def _get_score_n_days_ago(
        self,
        popularity_history: List[Dict[str, Any]],
        days: int
    ) -> Optional[int]:
        """
        Helper function to get popularity score from N days ago.

        Args:
            popularity_history (List[Dict]): List of {date: str, score: int} sorted by date
            days (int): How many days back to look

        Returns:
            Optional[int]: Popularity score from N days ago, or None if not available
        """
        try:
            target_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            for entry in popularity_history:
                if entry['date'] == target_date:
                    return entry['score']

            logger.debug(f"No data found for {days} days ago (target: {target_date})")
            return None

        except Exception as e:
            logger.error(f"Error getting score from {days} days ago: {str(e)}")
            return None

    def _check_reentry_requirements(
        self,
        tier: int,
        popularity_history: List[Dict[str, Any]],
        current_popularity: int,
        user_baseline: int
    ) -> bool:
        """
        Check if song meets tier requirements for RE-ENTERING Fire Mode.

        Re-entry is harder than first entry. Songs that exited Fire Mode must
        demonstrate they're growing again before re-entering. This prevents
        songs from bouncing in and out of Fire Mode repeatedly.

        Re-entry window is from TODAY looking back N days (not from exit date).

        Args:
            tier (int): User's tier (1-4)
            popularity_history (List[Dict]): Recent daily popularity scores
            current_popularity (int): Current popularity score
            user_baseline (int): User's baseline for fallback

        Returns:
            bool: True if song meets re-entry requirements
        """
        try:
            if tier == 4:
                # Tier 4: Need +3 points over 7 days (same as maintenance)
                seven_days_ago = self._get_score_n_days_ago(popularity_history, 7)
                if seven_days_ago is None:
                    # Not enough history - require baseline check as fallback
                    logger.info(f"Re-entry Tier 4: Insufficient history, using baseline check")
                    return current_popularity >= user_baseline
                eligible = current_popularity >= seven_days_ago + 3
                logger.info(f"Re-entry Tier 4: {current_popularity} vs {seven_days_ago}+3 = {eligible}")
                return eligible

            # Tiers 1-3: Check based on current popularity phase
            if current_popularity < 20:
                # Phase 1 equivalent: Need +2 points over 2 days
                two_days_ago = self._get_score_n_days_ago(popularity_history, 2)
                if two_days_ago is None:
                    logger.info(f"Re-entry Phase 1: Insufficient history, using baseline check")
                    return current_popularity >= user_baseline
                eligible = current_popularity >= two_days_ago + 2
                logger.info(f"Re-entry Phase 1: {current_popularity} vs {two_days_ago}+2 = {eligible}")
                return eligible

            elif current_popularity < 30:
                # Phase 2 equivalent: Need +1 point over 2 days
                two_days_ago = self._get_score_n_days_ago(popularity_history, 2)
                if two_days_ago is None:
                    logger.info(f"Re-entry Phase 2: Insufficient history, using baseline check")
                    return current_popularity >= user_baseline
                eligible = current_popularity >= two_days_ago + 1
                logger.info(f"Re-entry Phase 2: {current_popularity} vs {two_days_ago}+1 = {eligible}")
                return eligible

            else:
                # Phase 3 equivalent (30+): Need growth in last 3 days
                three_days_ago = self._get_score_n_days_ago(popularity_history, 3)
                if three_days_ago is None:
                    logger.info(f"Re-entry Phase 3: Insufficient history, using baseline check")
                    return current_popularity >= user_baseline
                eligible = current_popularity > three_days_ago
                logger.info(f"Re-entry Phase 3: {current_popularity} > {three_days_ago} = {eligible}")
                return eligible

        except Exception as e:
            logger.error(f"Error checking re-entry requirements: {str(e)}")
            # Fallback to baseline check on error
            return current_popularity >= user_baseline

    def determine_tier_from_baseline(self, baseline: int) -> int:
        """
        Determine tier from baseline score.

        Args:
            baseline (int): User's baseline score

        Returns:
            int: Tier 1-4
        """
        if baseline <= 10:
            return 1
        elif baseline <= 20:
            return 2
        elif baseline <= 30:
            return 3
        else:
            return 4

    def get_tier_description(self, tier: int) -> str:
        """
        Get human-readable tier description.

        Args:
            tier (int): Tier 1-4

        Returns:
            str: Tier description
        """
        descriptions = {
            1: "Emerging Artists (0-10% baseline)",
            2: "Growing Artists (11-20% baseline)",
            3: "Established Artists (21-30% baseline)",
            4: "High-Performing Artists (31-100% baseline)"
        }
        return descriptions.get(tier, "Unknown Tier")

    def get_phase_description(self, phase: Optional[int]) -> str:
        """
        Get human-readable phase description.

        Args:
            phase (Optional[int]): Phase 1-3, or None for Tier 4

        Returns:
            str: Phase description
        """
        if phase is None:
            return "Tier 4 (7-day lookback)"

        descriptions = {
            1: "Phase 1: Below 20% (+2 points every 2 days)",
            2: "Phase 2: 20-30% (+1 point every 2 days)",
            3: "Phase 3: Above 30% (maintain peak)"
        }
        return descriptions.get(phase, "Unknown Phase")


# Global Fire Mode analyzer instance
fire_mode_analyzer = FireModeAnalyzer()


# Convenience functions
def check_fire_mode(
    user_baseline: int,
    song_current_popularity: int,
    song_fire_mode_active: bool,
    song_fire_mode_start_date: str,
    song_peak_popularity: int,
    song_popularity_history: List[Dict[str, Any]],
    has_been_on_fire_before: bool = False
) -> Dict[str, Any]:
    """
    Check Fire Mode eligibility for a song.

    Args:
        user_baseline (int): User's baseline score
        song_current_popularity (int): Current song popularity
        song_fire_mode_active (bool): Is Fire Mode currently active?
        song_fire_mode_start_date (str): When Fire Mode started (ISO)
        song_peak_popularity (int): Peak score while in Fire Mode
        song_popularity_history (List[Dict]): Daily popularity history
        has_been_on_fire_before (bool): Has this song been on Fire Mode before?

    Returns:
        Dict: Fire Mode analysis results
    """
    return fire_mode_analyzer.calculate_fire_mode_eligibility(
        user_baseline,
        song_current_popularity,
        song_fire_mode_active,
        song_fire_mode_start_date,
        song_peak_popularity,
        song_popularity_history,
        has_been_on_fire_before
    )


def get_tier(baseline: int) -> int:
    """Determine tier from baseline."""
    return fire_mode_analyzer.determine_tier_from_baseline(baseline)


def describe_tier(tier: int) -> str:
    """Get tier description."""
    return fire_mode_analyzer.get_tier_description(tier)


def describe_phase(phase: Optional[int]) -> str:
    """Get phase description."""
    return fire_mode_analyzer.get_phase_description(phase)
