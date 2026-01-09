"""
Popularity Tracker Module
Polls Spotify API for track popularity scores and stores daily snapshots.
Maintains historical data for Fire Mode calculations.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests

from auth.environment_loader import get_platform_credentials
from spotify.baseline_calculator import baseline_calculator
from data.dynamodb_client import dynamodb_client
from data.song_manager import song_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PopularityTracker:
    """
    Tracks Spotify popularity scores for user songs.

    Features:
    - Poll Spotify API for current popularity
    - Store daily snapshots in DynamoDB
    - Maintain popularity history
    - Query historical data for Fire Mode checks
    """

    def __init__(self):
        """Initialize popularity tracker."""
        self.spotify_api_base = 'https://api.spotify.com/v1'
        self.metrics_table = 'noisemaker-track-metrics'
        self.history_days = 30  # Keep 30 days of history in song record

        logger.info("Popularity tracker initialized")

    def poll_track_popularity(self, track_id: str, user_id: str) -> Optional[int]:
        """
        Fetch current popularity score from Spotify API using app-level credentials.

        Args:
            track_id (str): Spotify track ID
            user_id (str): User identifier (for logging/tracking)

        Returns:
            Optional[int]: Popularity score 0-100, or None if error
        """
        try:
            # Get app-level Spotify credentials from Parameter Store
            spotify_creds = get_platform_credentials('spotify')
            client_id = spotify_creds.get('client_id')
            client_secret = spotify_creds.get('client_secret')

            if not client_id or not client_secret:
                logger.error("Spotify app credentials not configured in Parameter Store")
                return None

            # Get access token using Client Credentials flow (app-level, no user auth)
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials

            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )

            headers = {
                'Authorization': f'Bearer {auth_manager.get_access_token(as_dict=False)}'
            }

            # Fetch track details
            url = f"{self.spotify_api_base}/tracks/{track_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            track_data = response.json()
            popularity = track_data.get('popularity', 0)

            logger.debug(f"Track {track_id} current popularity: {popularity}")
            return popularity

        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling popularity for track {track_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error polling track {track_id}: {str(e)}")
            return None

    def store_daily_snapshot(
        self,
        track_id: str,
        user_id: str,
        song_id: str,
        popularity: int
    ) -> bool:
        """
        Store today's popularity snapshot in DynamoDB.

        Args:
            track_id (str): Spotify track ID
            user_id (str): User identifier
            song_id (str): Internal song ID
            popularity (int): Current popularity score 0-100

        Returns:
            bool: True if successful
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            # Get current user baseline and tier
            baseline = baseline_calculator.get_user_baseline(user_id)
            tier = baseline_calculator.get_user_tier(user_id)

            # Get song's current Fire Mode status
            song = song_manager.get_song(user_id, song_id)
            if not song:
                logger.error(f"Song {song_id} not found for user {user_id}")
                return False

            fire_mode_active = song.get('fire_mode', False)
            fire_mode_phase = song.get('fire_mode_phase')
            peak_popularity = song.get('peak_popularity_in_fire_mode', 0)

            # Calculate TTL (365 days from now)
            ttl = int((datetime.now() + timedelta(days=365)).timestamp())

            # Create snapshot record
            snapshot = {
                'track_id': track_id,
                'poll_date': today,
                'user_id': user_id,
                'song_id': song_id,
                'popularity_score': popularity,
                'baseline_at_poll': baseline,
                'tier_at_poll': tier,
                'fire_mode_active': fire_mode_active,
                'fire_mode_phase': fire_mode_phase,
                'peak_popularity': peak_popularity,
                'created_at': datetime.now().isoformat(),
                'ttl': ttl
            }

            # Store in noisemaker-track-metrics table
            success = dynamodb_client.put_item(self.metrics_table, snapshot)

            if success:
                logger.info(f"Stored snapshot for track {track_id} on {today}: {popularity}")

                # Also update song's current popularity in songs table
                song_manager.update_song_field(user_id, song_id, {
                    'spotify_popularity': popularity,
                    'updated_at': datetime.now().isoformat()
                })

                # Update popularity_history in song record (keep last 30 days)
                self._update_song_popularity_history(user_id, song_id, today, popularity)

            return success

        except Exception as e:
            logger.error(f"Error storing snapshot for track {track_id}: {str(e)}")
            return False

    def _update_song_popularity_history(
        self,
        user_id: str,
        song_id: str,
        date: str,
        score: int
    ) -> bool:
        """
        Update song's popularity_history field with today's score.

        Args:
            user_id (str): User identifier
            song_id (str): Internal song ID
            date (str): Date (YYYY-MM-DD)
            score (int): Popularity score

        Returns:
            bool: True if successful
        """
        try:
            song = song_manager.get_song(user_id, song_id)
            if not song:
                return False

            # Get existing history
            history = song.get('popularity_history', [])

            # Add today's score
            history.append({
                'date': date,
                'score': score
            })

            # Keep only last 30 days
            cutoff_date = (datetime.now() - timedelta(days=self.history_days)).strftime('%Y-%m-%d')
            history = [h for h in history if h['date'] >= cutoff_date]

            # Sort by date (oldest first)
            history.sort(key=lambda x: x['date'])

            # Update song
            return song_manager.update_song_field(user_id, song_id, {
                'popularity_history': history
            })

        except Exception as e:
            logger.error(f"Error updating popularity history for song {song_id}: {str(e)}")
            return False

    def get_popularity_history(
        self,
        track_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get last N days of popularity scores for a track.

        Args:
            track_id (str): Spotify track ID
            days (int): Number of days of history to fetch

        Returns:
            List[Dict]: List of {date: str, score: int} sorted by date
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query noisemaker-track-metrics table
            # Note: This is a simplified version. In production, you'd use
            # a proper date range query with begins_with on the sort key

            results = dynamodb_client.query_items(
                self.metrics_table,
                'track_id = :track_id',
                expression_values={':track_id': track_id}
            )

            # Filter by date range
            cutoff_date = start_date.strftime('%Y-%m-%d')
            filtered_results = [
                {
                    'date': r['poll_date'],
                    'score': r['popularity_score']
                }
                for r in results
                if r['poll_date'] >= cutoff_date
            ]

            # Sort by date (oldest first)
            filtered_results.sort(key=lambda x: x['date'])

            logger.debug(f"Retrieved {len(filtered_results)} days of history for track {track_id}")
            return filtered_results

        except Exception as e:
            logger.error(f"Error getting popularity history for track {track_id}: {str(e)}")
            return []

    def get_score_n_days_ago(
        self,
        track_id: str,
        days: int
    ) -> Optional[int]:
        """
        Get popularity score from N days ago.

        Args:
            track_id (str): Spotify track ID
            days (int): How many days back

        Returns:
            Optional[int]: Popularity score, or None if not available
        """
        try:
            target_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # Query specific date
            key = {
                'track_id': track_id,
                'poll_date': target_date
            }

            result = dynamodb_client.get_item(self.metrics_table, key)

            if result:
                return result['popularity_score']

            logger.debug(f"No data found for track {track_id} on {target_date}")
            return None

        except Exception as e:
            logger.error(f"Error getting score for track {track_id} {days} days ago: {str(e)}")
            return None

    def poll_all_user_songs(self, user_id: str) -> Dict[str, Any]:
        """
        Poll popularity for all active songs for a user.

        Args:
            user_id (str): User identifier

        Returns:
            Dict: Summary of polling results
        """
        try:
            # Get user's active songs
            songs = song_manager.get_user_active_songs(user_id)

            if not songs:
                logger.info(f"No active songs for user {user_id}")
                return {
                    'success': True,
                    'songs_polled': 0,
                    'songs_failed': 0
                }

            polled_count = 0
            failed_count = 0

            for song in songs:
                spotify_track_id = song.get('spotify_track_id')
                song_id = song['song_id']

                if not spotify_track_id:
                    logger.warning(f"Song {song_id} has no Spotify track ID")
                    failed_count += 1
                    continue

                # Poll popularity
                popularity = self.poll_track_popularity(spotify_track_id, user_id)

                if popularity is not None:
                    # Store snapshot
                    success = self.store_daily_snapshot(
                        spotify_track_id,
                        user_id,
                        song_id,
                        popularity
                    )

                    if success:
                        polled_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

            logger.info(f"Polled {polled_count} songs for user {user_id} ({failed_count} failed)")

            return {
                'success': True,
                'songs_polled': polled_count,
                'songs_failed': failed_count,
                'total_songs': len(songs)
            }

        except Exception as e:
            logger.error(f"Error polling songs for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'songs_polled': 0,
                'songs_failed': 0
            }


# Global popularity tracker instance
popularity_tracker = PopularityTracker()


# Convenience functions
def poll_track(track_id: str, user_id: str) -> Optional[int]:
    """Poll track popularity from Spotify."""
    return popularity_tracker.poll_track_popularity(track_id, user_id)


def store_snapshot(track_id: str, user_id: str, song_id: str, popularity: int) -> bool:
    """Store popularity snapshot."""
    return popularity_tracker.store_daily_snapshot(track_id, user_id, song_id, popularity)


def get_history(track_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get popularity history for track."""
    return popularity_tracker.get_popularity_history(track_id, days)


def get_score_from_days_ago(track_id: str, days: int) -> Optional[int]:
    """Get score from N days ago."""
    return popularity_tracker.get_score_n_days_ago(track_id, days)


def poll_user_songs(user_id: str) -> Dict[str, Any]:
    """Poll all songs for a user."""
    return popularity_tracker.poll_all_user_songs(user_id)
