"""
Milestone Detection — NOiSEMaKER
Checks user metrics against milestone thresholds.
Detection runs daily via the daily processor.
Achievement recording is handled by user_manager.achieve_milestone().
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def check_follower_milestones(followers_at_signup: int, followers_current: int, achieved_milestones: List[str]) -> List[str]:
    """
    Check which follower milestones have been newly reached.

    Args:
        followers_at_signup: Frozen follower count from signup
        followers_current: Current follower count from Spotify
        achieved_milestones: List of milestone_type strings already achieved

    Returns:
        List of newly triggered milestone_type strings
    """
    growth = followers_current - followers_at_signup
    thresholds = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000, 25000, 50000, 100000]
    triggered = []
    for t in thresholds:
        key = f"followers_{t}"
        if growth >= t and key not in achieved_milestones:
            triggered.append(key)
    return triggered


def check_popularity_milestones(song_id: str, current_popularity: int, achieved_milestones: List[str]) -> List[str]:
    """
    Check which popularity milestones a song has newly reached.
    achieved_milestones should contain entries like "song_popularity_5#<song_id>"
    """
    thresholds = [5, 10, 15, 20, 25, 30]
    triggered = []
    for t in thresholds:
        key = f"song_popularity_{t}#{song_id}"
        if current_popularity >= t and key not in achieved_milestones:
            triggered.append(f"song_popularity_{t}")
    return triggered


def check_fire_mode_milestones(total_fire_modes: int, achieved_milestones: List[str]) -> List[str]:
    """Check fire mode count milestones."""
    triggered = []
    if total_fire_modes >= 1 and 'first_fire_mode' not in achieved_milestones:
        triggered.append('first_fire_mode')
    if total_fire_modes >= 3 and 'fire_mode_3' not in achieved_milestones:
        triggered.append('fire_mode_3')
    if total_fire_modes >= 10 and 'fire_mode_10' not in achieved_milestones:
        triggered.append('fire_mode_10')
    return triggered


def check_post_milestones(total_posts: int, achieved_milestones: List[str]) -> List[str]:
    """Check posting activity milestones."""
    triggered = []
    thresholds = [(100, 'posts_100'), (500, 'posts_500'), (1000, 'posts_1000')]
    for threshold, key in thresholds:
        if total_posts >= threshold and key not in achieved_milestones:
            triggered.append(key)
    return triggered


def check_longevity_milestones(days_active: int, achieved_milestones: List[str]) -> List[str]:
    """Check account longevity milestones."""
    triggered = []
    thresholds = [(90, 'active_3_months'), (180, 'active_6_months'), (365, 'active_1_year')]
    for threshold, key in thresholds:
        if days_active >= threshold and key not in achieved_milestones:
            triggered.append(key)
    return triggered
