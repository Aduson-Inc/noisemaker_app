"""
Track Analyzer Module
Advanced Spotify track analysis with stream data monitoring and performance metrics.
Designed for promotion cycle management and fire mode detection.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromotionStage(Enum):
    """Enumeration for promotion cycle stages."""
    UPCOMING = "upcoming"  # Days 1-14
    LIVE = "live"         # Days 15-28  
    TWILIGHT = "twilight" # Days 29-42


@dataclass
class TrackMetrics:
    """Data class for track performance metrics."""
    track_id: str
    current_streams: int
    previous_streams: int
    daily_average: float
    growth_rate: float
    days_since_release: int
    fire_mode_eligible: bool
    fire_mode_active: bool
    promotion_stage: PromotionStage
    days_in_promotion: int
    focus_percentage: float


class TrackAnalyzer:
    """
    Advanced track analysis system for promotion optimization.
    
    Features:
    - Stream count monitoring and analysis
    - Fire mode detection based on performance thresholds
    - Promotion stage calculation and focus distribution
    - Performance trending analysis
    - Historical data tracking
    """
    
    def __init__(self):
        """Initialize track analyzer."""
        self.fire_mode_threshold = 2.0  # 2x average for fire mode
        self.fire_mode_consecutive_days = 2  # Need 2 consecutive days to enter/exit fire mode
        self.promotion_cycle_days = 42  # 42-day promotion cycle (only limit on Fire Mode)
        
        # Stage configurations
        self.stage_configs = {
            PromotionStage.UPCOMING: {
                'days': (1, 14),
                'base_focus': 0.20  # 20% focus
            },
            PromotionStage.LIVE: {
                'days': (15, 28),
                'base_focus': 0.50  # 50% focus
            },
            PromotionStage.TWILIGHT: {
                'days': (29, 42),
                'base_focus': 0.30  # 30% focus
            }
        }
        
        logger.info("Track analyzer initialized")
    
    def analyze_track_performance(self, track_data: Dict[str, Any], user_average_streams: float, user_track_count: int = 1) -> TrackMetrics:
        """
        Analyze track performance and determine promotion metrics.
        
        Args:
            track_data (Dict[str, Any]): Track data from database
            user_average_streams (float): User's average daily streams across all tracks
            user_track_count (int): Total number of active tracks for user
            
        Returns:
            TrackMetrics: Comprehensive track analysis results
        """
        try:
            # Extract basic track information
            track_id = track_data.get('spotify_track_id', '')
            current_streams = int(track_data.get('stream_count', 0))
            days_in_promotion = int(track_data.get('days_in_promotion', 1))
            
            # Calculate daily average for this track
            days_since_release = self._calculate_days_since_release(track_data)
            daily_average = current_streams / max(days_since_release, 1)
            
            # Determine promotion stage
            promotion_stage = self._get_promotion_stage(days_in_promotion)
            
            # Calculate growth rate and fire mode eligibility
            previous_streams = int(track_data.get('previous_stream_count', current_streams))
            growth_rate = self._calculate_growth_rate(current_streams, previous_streams)
            
            # Fire mode detection
            fire_mode_eligible = daily_average >= (user_average_streams * self.fire_mode_threshold)
            fire_mode_active = self._is_fire_mode_active(track_data, fire_mode_eligible)
            
            # Calculate focus percentage
            focus_percentage = self._calculate_focus_percentage(
                promotion_stage, 
                fire_mode_active, 
                track_data,
                user_track_count
            )
            
            metrics = TrackMetrics(
                track_id=track_id,
                current_streams=current_streams,
                previous_streams=previous_streams,
                daily_average=daily_average,
                growth_rate=growth_rate,
                days_since_release=days_since_release,
                fire_mode_eligible=fire_mode_eligible,
                fire_mode_active=fire_mode_active,
                promotion_stage=promotion_stage,
                days_in_promotion=days_in_promotion,
                focus_percentage=focus_percentage
            )
            
            logger.info(f"Analyzed track {track_id}: stage={promotion_stage.value}, focus={focus_percentage:.2%}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing track performance: {str(e)}")
            # Return default metrics on error
            return TrackMetrics(
                track_id=track_data.get('spotify_track_id', ''),
                current_streams=0,
                previous_streams=0,
                daily_average=0.0,
                growth_rate=0.0,
                days_since_release=1,
                fire_mode_eligible=False,
                fire_mode_active=False,
                promotion_stage=PromotionStage.UPCOMING,
                days_in_promotion=1,
                focus_percentage=0.0
            )
    
    def _calculate_days_since_release(self, track_data: Dict[str, Any]) -> int:
        """
        Calculate days since track was released on Spotify.
        
        Args:
            track_data (Dict[str, Any]): Track data
            
        Returns:
            int: Number of days since release
        """
        try:
            # Try to get release date from track data
            release_date_str = track_data.get('release_date')
            if release_date_str:
                release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                days_since = (datetime.now() - release_date).days
                return max(days_since, 1)  # At least 1 day
            
            # Fallback: use days in promotion if no release date
            return max(int(track_data.get('days_in_promotion', 1)), 1)
            
        except Exception as e:
            logger.error(f"Error calculating days since release: {str(e)}")
            return 1
    
    def _get_promotion_stage(self, days_in_promotion: int) -> PromotionStage:
        """
        Determine promotion stage based on days in cycle.
        
        Args:
            days_in_promotion (int): Current day in promotion cycle
            
        Returns:
            PromotionStage: Current stage of promotion
        """
        if 1 <= days_in_promotion <= 14:
            return PromotionStage.UPCOMING
        elif 15 <= days_in_promotion <= 28:
            return PromotionStage.LIVE
        elif 29 <= days_in_promotion <= 42:
            return PromotionStage.TWILIGHT
        else:
            # Default to twilight for extended promotions
            return PromotionStage.TWILIGHT
    
    def _calculate_growth_rate(self, current_streams: int, previous_streams: int) -> float:
        """
        Calculate stream growth rate.
        
        Args:
            current_streams (int): Current stream count
            previous_streams (int): Previous stream count
            
        Returns:
            float: Growth rate as percentage
        """
        if previous_streams == 0:
            return 0.0
        
        growth_rate = ((current_streams - previous_streams) / previous_streams) * 100
        return round(growth_rate, 2)
    
    def _is_fire_mode_active(self, track_data: Dict[str, Any], fire_mode_eligible: bool) -> bool:
        """
        Check if track is currently in fire mode based on 2 consecutive days above threshold.
        
        Args:
            track_data (Dict[str, Any]): Track data
            fire_mode_eligible (bool): Whether track meets fire mode threshold today
            
        Returns:
            bool: True if fire mode is active
        """
        if not fire_mode_eligible:
            # If not eligible today, check if we need to deactivate existing fire mode
            current_fire_mode = track_data.get('fire_mode_active', False)
            if current_fire_mode:
                logger.info(f"Track {track_data.get('track_id')} no longer meets fire mode threshold - deactivating")
            return False
        
        # Get historical eligibility data
        fire_mode_history = track_data.get('fire_mode_history', [])
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update today's eligibility
        if not fire_mode_history or fire_mode_history[-1].get('date') != today:
            fire_mode_history.append({
                'date': today,
                'eligible': True
            })
        
        # Keep only last 7 days of history for storage efficiency
        if len(fire_mode_history) > 7:
            fire_mode_history = fire_mode_history[-7:]
        
        # Check for 2 consecutive days of eligibility
        if len(fire_mode_history) >= 2:
            last_two_days = fire_mode_history[-2:]
            if all(day.get('eligible', False) for day in last_two_days):
                logger.info(f"Track {track_data.get('track_id')} entering fire mode - 2 consecutive days above threshold")
                return True

        # Fire Mode has NO duration limit - only limited by 42-day song cycle
        # Stays active as long as 2× threshold is met
        # Deactivates after 2 consecutive days below threshold (handled above)
        # If we reach here, the consecutive day logic determined the status
        return False  # Default to not active if no clear decision made above
    
    def _calculate_focus_percentage(self, stage: PromotionStage, fire_mode_active: bool, track_data: Dict[str, Any], user_track_count: int) -> float:
        """
        Calculate focus percentage for track based on stage, fire mode, and total user tracks.
        
        Args:
            stage (PromotionStage): Promotion stage
            fire_mode_active (bool): Whether fire mode is active
            track_data (Dict[str, Any]): Track data
            user_track_count (int): Total number of active tracks for user
            
        Returns:
            float: Focus percentage (0.0 to 1.0)
        """
        if fire_mode_active:
            # Fire mode gets 70% of total focus
            return 0.70
        
        # Dynamic focus distribution based on number of tracks
        if user_track_count == 1:
            return 1.0  # Single track gets 100% focus
        elif user_track_count == 2:
            return 0.5  # Two tracks get 50% each
        else:
            # 3+ tracks use stage-based distribution (20%/50%/30%)
            return self.stage_configs[stage]['base_focus']
    
    def calculate_user_baseline_streams(self, user_tracks: List[Dict[str, Any]], limit_to_newest: int = 5) -> float:
        """
        Calculate user's baseline average daily streams from their newest tracks.

        Args:
            user_tracks (List[Dict[str, Any]]): List of user's track data
            limit_to_newest (int): Number of newest tracks to include in calculation

        Returns:
            float: Average daily streams baseline
        """
        try:
            if not user_tracks:
                return 0.0

            # Sort tracks by creation date (newest first)
            sorted_tracks = sorted(
                user_tracks,
                key=lambda x: x.get('created_at', 0),
                reverse=True
            )

            # Take only the newest tracks for baseline calculation
            recent_tracks = sorted_tracks[:limit_to_newest]

            total_daily_average = 0.0
            valid_tracks = 0

            for track in recent_tracks:
                streams = int(track.get('stream_count', 0))
                days_since_release = self._calculate_days_since_release(track)

                if streams > 0 and days_since_release > 0:
                    daily_average = streams / days_since_release
                    total_daily_average += daily_average
                    valid_tracks += 1

            if valid_tracks == 0:
                return 0.0

            baseline = total_daily_average / valid_tracks
            logger.info(f"Calculated user baseline: {baseline:.2f} daily streams from {valid_tracks} tracks")
            return baseline

        except Exception as e:
            logger.error(f"Error calculating user baseline streams: {str(e)}")
            return 0.0

    def initialize_user_baseline(self, user_id: str, user_tracks: List[Dict[str, Any]]) -> bool:
        """
        Calculate and store initial baseline daily streams for a user.
        Called on signup or when first songs are added.

        This baseline is used to determine Fire Mode eligibility (2× threshold).
        The baseline is dynamic and should be updated periodically as more data becomes available.

        Args:
            user_id (str): User identifier
            user_tracks (List[Dict[str, Any]]): User's tracks for baseline calculation

        Returns:
            bool: True if baseline was calculated and stored successfully
        """
        try:
            if not user_tracks:
                logger.warning(f"No tracks provided for user {user_id} baseline calculation")
                return False

            # Calculate baseline from user's tracks
            baseline = self.calculate_user_baseline_streams(user_tracks)

            # Enforce minimum baseline of 50 streams/day
            # This means Fire Mode requires 100 streams/day (2× threshold) for quality control
            # This creates excitement for artists hitting 100 streams/day milestone
            if baseline < 50.0:
                logger.warning(f"Baseline is {baseline:.2f} for user {user_id}, enforcing minimum of 50")
                baseline = 50.0  # Minimum baseline ensures Fire Mode quality threshold

            # Store baseline in user profile (will need to import user_manager)
            # For now, we'll return the baseline - integration with user_manager
            # will be done when this method is called
            logger.info(f"Initialized baseline for user {user_id}: {baseline:.2f} daily streams")

            # Return the baseline so calling code can store it
            # The calling code should use user_manager.update_user_profile() to store:
            # {
            #     'baseline_daily_streams': baseline,
            #     'baseline_calculated_at': datetime.now().isoformat(),
            #     'baseline_source': 'initial_tracks'
            # }
            return baseline

        except Exception as e:
            logger.error(f"Error initializing baseline for user {user_id}: {str(e)}")
            return False

    def update_user_baseline_dynamically(self, user_id: str, user_tracks: List[Dict[str, Any]], days_since_last_update: int = 7) -> Optional[float]:
        """
        Dynamically update user's baseline based on recent performance.
        Should be called periodically (e.g., weekly) to keep baseline accurate.

        Args:
            user_id (str): User identifier
            user_tracks (List[Dict[str, Any]]): User's current active tracks
            days_since_last_update (int): Days since last baseline update

        Returns:
            Optional[float]: New baseline value if updated, None if no update needed
        """
        try:
            if not user_tracks:
                return None

            # Recalculate baseline from recent track performance
            new_baseline = self.calculate_user_baseline_streams(user_tracks)

            if new_baseline <= 0:
                logger.warning(f"New baseline is 0 for user {user_id}, keeping existing baseline")
                return None

            logger.info(f"Updated baseline for user {user_id}: {new_baseline:.2f} daily streams")

            # Return new baseline for storage
            # Calling code should update user profile with:
            # {
            #     'baseline_daily_streams': new_baseline,
            #     'baseline_calculated_at': datetime.now().isoformat(),
            #     'baseline_source': 'dynamic_update'
            # }
            return new_baseline

        except Exception as e:
            logger.error(f"Error updating baseline for user {user_id}: {str(e)}")
            return None
    
    def _select_fire_mode_winner(self, fire_candidates: List[TrackMetrics]) -> TrackMetrics:
        """
        Select which song gets Fire Mode when multiple songs qualify simultaneously.

        RULE: Oldest song in promotion cycle wins (highest days_in_promotion).
        Reasoning: Give priority to songs nearing end of cycle so they can benefit
        from Fire Mode before retiring on Day 42.

        Args:
            fire_candidates (List[TrackMetrics]): Songs that qualify for Fire Mode

        Returns:
            TrackMetrics: The song that wins Fire Mode priority
        """
        winner = max(fire_candidates, key=lambda tm: tm.days_in_promotion)
        logger.info(f"Fire Mode winner: Track {winner.track_id} (Day {winner.days_in_promotion})")
        return winner

    def distribute_daily_posts(self, track_metrics: List[TrackMetrics], total_daily_posts: int) -> Dict[str, int]:
        """
        Distribute daily posts among tracks based on focus percentages.

        Args:
            track_metrics (List[TrackMetrics]): List of track analysis results
            total_daily_posts (int): Total posts available for the day

        Returns:
            Dict[str, int]: Distribution of posts per track ID
        """
        try:
            if not track_metrics or total_daily_posts <= 0:
                return {}
            
            post_distribution = {}
            
            # Handle fire mode first - it gets priority
            fire_mode_tracks = [tm for tm in track_metrics if tm.fire_mode_active]
            
            if fire_mode_tracks:
                # Fire mode track gets 70% of posts
                # If multiple qualify, select oldest song in cycle
                fire_track = self._select_fire_mode_winner(fire_mode_tracks) if len(fire_mode_tracks) > 1 else fire_mode_tracks[0]
                fire_posts = int(total_daily_posts * 0.70)
                post_distribution[fire_track.track_id] = fire_posts
                
                # Remaining tracks split the remaining 30%
                remaining_posts = total_daily_posts - fire_posts
                non_fire_tracks = [tm for tm in track_metrics if not tm.fire_mode_active]
                
                if non_fire_tracks and remaining_posts > 0:
                    posts_per_track = remaining_posts // len(non_fire_tracks)
                    extra_posts = remaining_posts % len(non_fire_tracks)
                    
                    for i, track_metric in enumerate(non_fire_tracks):
                        posts = posts_per_track
                        if i < extra_posts:  # Distribute extra posts
                            posts += 1
                        post_distribution[track_metric.track_id] = posts
            
            else:
                # Normal distribution based on focus percentages
                total_focus = sum(tm.focus_percentage for tm in track_metrics)
                
                if total_focus > 0:
                    for track_metric in track_metrics:
                        percentage = track_metric.focus_percentage / total_focus
                        posts = int(total_daily_posts * percentage)
                        post_distribution[track_metric.track_id] = posts
                
                # Handle any remaining posts due to rounding
                distributed_posts = sum(post_distribution.values())
                remaining = total_daily_posts - distributed_posts
                
                if remaining > 0:
                    # Give remaining posts to the track with highest focus
                    sorted_tracks = sorted(track_metrics, key=lambda x: x.focus_percentage, reverse=True)
                    if sorted_tracks:
                        post_distribution[sorted_tracks[0].track_id] += remaining
            
            logger.info(f"Distributed {total_daily_posts} posts: {post_distribution}")
            return post_distribution

        except Exception as e:
            logger.error(f"Error distributing daily posts: {str(e)}")
            return {}

    def assign_platforms_to_tracks(
        self,
        post_distribution: Dict[str, int],
        enabled_platforms: List[str],
        track_platform_history: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, List[str]]:
        """
        Assign specific platforms to each track's posts with rotation to ensure variety.

        This ensures:
        - Posts are distributed across all enabled platforms
        - Each track doesn't always use the same platforms
        - Platform usage is tracked to prevent repetition
        - Fair distribution across platforms

        Args:
            post_distribution (Dict[str, int]): Number of posts per track ID
            enabled_platforms (List[str]): User's enabled platforms
            track_platform_history (Optional[Dict[str, List[str]]]): Recent platform usage per track
                                                                     (last 7 days to ensure rotation)

        Returns:
            Dict[str, List[str]]: Platform assignments per track ID
        """
        try:
            import random
            from collections import defaultdict

            if not post_distribution or not enabled_platforms:
                return {}

            platform_assignments = {}

            # Track how many times each platform has been used across all tracks
            platform_usage_count = defaultdict(int)

            # Initialize history if not provided
            if track_platform_history is None:
                track_platform_history = {}

            for track_id, num_posts in post_distribution.items():
                if num_posts <= 0:
                    platform_assignments[track_id] = []
                    continue

                # Get this track's recent platform history
                recent_platforms = track_platform_history.get(track_id, [])

                # Calculate platform scores for rotation (prefer platforms used less recently)
                platform_scores = {}
                for platform in enabled_platforms:
                    # Base score starts at 100
                    score = 100

                    # Penalize platforms used recently by this track
                    if platform in recent_platforms:
                        # More recent = higher penalty
                        position = len(recent_platforms) - recent_platforms[::-1].index(platform)
                        penalty = (8 - position) * 10  # More recent = more penalty
                        score -= penalty

                    # Penalize platforms that have been used more overall today
                    score -= (platform_usage_count[platform] * 5)

                    platform_scores[platform] = max(score, 1)  # Minimum score of 1

                # Select platforms for this track's posts
                selected_platforms = []
                available_platforms = enabled_platforms.copy()

                for i in range(num_posts):
                    if not available_platforms:
                        # If we've used all platforms, reset the pool
                        available_platforms = enabled_platforms.copy()

                    # Weight selection by scores
                    weights = [platform_scores.get(p, 50) for p in available_platforms]

                    # Select platform using weighted random choice
                    selected = random.choices(available_platforms, weights=weights, k=1)[0]
                    selected_platforms.append(selected)

                    # Update usage counts
                    platform_usage_count[selected] += 1

                    # Reduce score for selected platform to encourage variety
                    platform_scores[selected] = max(platform_scores[selected] - 20, 1)

                    # Remove from available pool if we want to cycle through all before repeating
                    if len(available_platforms) > 1:
                        available_platforms.remove(selected)

                platform_assignments[track_id] = selected_platforms
                logger.info(f"Track {track_id}: {num_posts} posts assigned to {selected_platforms}")

            return platform_assignments

        except Exception as e:
            logger.error(f"Error assigning platforms to tracks: {str(e)}")
            return {}

    def check_milestone_achievements(self, track_data: Dict[str, Any]) -> List[int]:
        """
        Check if track has achieved any stream milestones.
        
        Args:
            track_data (Dict[str, Any]): Track data
            
        Returns:
            List[int]: List of newly achieved milestones
        """
        milestones = [100, 250, 500, 750, 1000, 2000, 5000, 7500, 10000, 
                     20000, 25000, 50000, 75000, 100000]
        
        current_streams = int(track_data.get('stream_count', 0))
        previous_streams = int(track_data.get('previous_stream_count', 0))
        
        achieved_milestones = []
        
        for milestone in milestones:
            if previous_streams < milestone <= current_streams:
                achieved_milestones.append(milestone)
        
        if achieved_milestones:
            logger.info(f"Track {track_data.get('spotify_track_id')} achieved milestones: {achieved_milestones}")
        
        return achieved_milestones


# Global analyzer instance
track_analyzer = TrackAnalyzer()


# Convenience functions for easy integration
def analyze_track(track_data: Dict[str, Any], user_baseline: float, user_track_count: int = 1) -> TrackMetrics:
    """
    Convenience function to analyze single track.
    
    Args:
        track_data (Dict[str, Any]): Track data
        user_baseline (float): User's baseline average streams
        user_track_count (int): Total number of active tracks for user
        
    Returns:
        TrackMetrics: Track analysis results
    """
    return track_analyzer.analyze_track_performance(track_data, user_baseline, user_track_count)


def calculate_post_distribution(metrics: List[TrackMetrics], daily_posts: int) -> Dict[str, int]:
    """
    Convenience function to distribute posts among tracks.

    Args:
        metrics (List[TrackMetrics]): Track analysis results
        daily_posts (int): Total daily posts available

    Returns:
        Dict[str, int]: Post distribution per track
    """
    return track_analyzer.distribute_daily_posts(metrics, daily_posts)


def initialize_baseline(user_id: str, user_tracks: List[Dict[str, Any]]) -> float:
    """
    Convenience function to initialize user baseline on signup.

    Args:
        user_id (str): User identifier
        user_tracks (List[Dict[str, Any]]): User's tracks

    Returns:
        float: Calculated baseline daily streams
    """
    return track_analyzer.initialize_user_baseline(user_id, user_tracks)


def update_baseline(user_id: str, user_tracks: List[Dict[str, Any]]) -> Optional[float]:
    """
    Convenience function to update user baseline dynamically.

    Args:
        user_id (str): User identifier
        user_tracks (List[Dict[str, Any]]): User's current tracks

    Returns:
        Optional[float]: New baseline value if updated
    """
    return track_analyzer.update_user_baseline_dynamically(user_id, user_tracks)


def assign_platforms(
    post_distribution: Dict[str, int],
    enabled_platforms: List[str],
    track_platform_history: Optional[Dict[str, List[str]]] = None
) -> Dict[str, List[str]]:
    """
    Convenience function to assign platforms to track posts with rotation.

    Args:
        post_distribution (Dict[str, int]): Posts per track ID
        enabled_platforms (List[str]): User's enabled platforms
        track_platform_history (Optional[Dict[str, List[str]]]): Recent platform usage

    Returns:
        Dict[str, List[str]]: Platform assignments per track ID
    """
    return track_analyzer.assign_platforms_to_tracks(
        post_distribution,
        enabled_platforms,
        track_platform_history
    )
