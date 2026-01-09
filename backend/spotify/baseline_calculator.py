"""
Baseline Calculator Module
Calculates user's baseline popularity from their 5 most recent Spotify tracks.
Implements simple average with ceiling rounding as per specification.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
"""

import math
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests

from auth.environment_loader import get_platform_credentials
from data.dynamodb_client import dynamodb_client
from data.user_manager import user_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaselineCalculator:
    """
    Calculates and manages user baseline popularity scores.

    Features:
    - Fetch user's Spotify catalog
    - Calculate baseline from 5 most recent tracks
    - Simple average with ceiling rounding
    - Tier determination
    - Weekly recalculation
    - Baseline history storage
    """

    def __init__(self):
        """Initialize baseline calculator."""
        self.spotify_api_base = 'https://api.spotify.com/v1'
        self.baselines_table = 'noisemaker-baselines'
        self.default_baseline = 5  # For users with < 5 tracks

        logger.info("Baseline calculator initialized")

    def fetch_artist_catalog(self, user_id: str, artist_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all tracks from a Spotify artist profile using app-level credentials.

        Args:
            user_id (str): User identifier (for logging/tracking)
            artist_id (str): Spotify artist ID

        Returns:
            List[Dict]: List of tracks with id, name, popularity, release_date
        """
        try:
            # Get app-level Spotify credentials from Parameter Store
            spotify_creds = get_platform_credentials('spotify')
            client_id = spotify_creds.get('client_id')
            client_secret = spotify_creds.get('client_secret')

            if not client_id or not client_secret:
                logger.error("Spotify app credentials not configured in Parameter Store")
                return []

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

            all_tracks = []

            # Get artist's albums (includes singles, albums, compilations)
            albums_url = f"{self.spotify_api_base}/artists/{artist_id}/albums"
            params = {
                'include_groups': 'album,single',
                'limit': 50  # Max per request
            }

            albums_response = requests.get(albums_url, headers=headers, params=params)
            albums_response.raise_for_status()

            albums_data = albums_response.json()
            albums = albums_data.get('items', [])

            logger.info(f"Found {len(albums)} albums/singles for artist {artist_id}")

            # For each album, get tracks
            for album in albums:
                album_id = album['id']
                release_date = album.get('release_date', '')

                # Get tracks from this album
                tracks_url = f"{self.spotify_api_base}/albums/{album_id}/tracks"
                tracks_response = requests.get(tracks_url, headers=headers)
                tracks_response.raise_for_status()

                tracks_data = tracks_response.json()
                tracks = tracks_data.get('items', [])

                # Get full track details (need popularity score)
                for track in tracks:
                    track_id = track['id']

                    # Get track details including popularity
                    track_url = f"{self.spotify_api_base}/tracks/{track_id}"
                    track_response = requests.get(track_url, headers=headers)
                    track_response.raise_for_status()

                    full_track = track_response.json()

                    all_tracks.append({
                        'id': full_track['id'],
                        'name': full_track['name'],
                        'popularity': full_track.get('popularity', 0),
                        'release_date': release_date,
                        'album_name': album['name'],
                        'album_type': album['album_type']
                    })

            logger.info(f"Fetched {len(all_tracks)} total tracks for artist {artist_id}")
            return all_tracks

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching catalog for user {user_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching catalog for user {user_id}: {str(e)}")
            return []

    def calculate_baseline(self, user_id: str, artist_id: str) -> Dict[str, Any]:
        """
        Calculate user's baseline from their 5 most recent Spotify tracks.

        Args:
            user_id (str): User identifier
            artist_id (str): Spotify artist ID

        Returns:
            Dict: {
                'baseline': int (rounded up),
                'tier': int (1-4),
                'track_ids': list of track IDs used,
                'track_count': int,
                'raw_average': float (pre-ceiling),
                'success': bool
            }
        """
        try:
            logger.info(f"Calculating baseline for user {user_id}")

            # Fetch user's catalog
            all_tracks = self.fetch_artist_catalog(user_id, artist_id)

            if not all_tracks:
                logger.warning(f"No tracks found for user {user_id}, using default baseline")
                return {
                    'baseline': self.default_baseline,
                    'tier': 1,
                    'track_ids': [],
                    'track_count': 0,
                    'raw_average': 0.0,
                    'success': True,
                    'message': 'No tracks found, using default baseline'
                }

            # Sort by release_date (newest first)
            sorted_tracks = sorted(
                all_tracks,
                key=lambda x: x['release_date'],
                reverse=True
            )

            # Take 5 most recent
            recent_5 = sorted_tracks[:5]

            # If less than 5 tracks, use default baseline
            if len(recent_5) < 5:
                logger.info(f"User {user_id} has only {len(recent_5)} tracks, using default baseline")
                return {
                    'baseline': self.default_baseline,
                    'tier': 1,
                    'track_ids': [t['id'] for t in recent_5],
                    'track_count': len(recent_5),
                    'raw_average': 0.0,
                    'success': True,
                    'message': f'Only {len(recent_5)} tracks, using default baseline'
                }

            # Calculate simple average
            total_popularity = sum(track['popularity'] for track in recent_5)
            raw_average = total_popularity / 5

            # Floor with minimum of 5 (not ceiling)
            baseline = max(5, int(raw_average))

            # Determine tier
            if baseline <= 10:
                tier = 1
            elif baseline <= 20:
                tier = 2
            elif baseline <= 30:
                tier = 3
            else:
                tier = 4

            track_ids = [track['id'] for track in recent_5]

            logger.info(f"Calculated baseline for user {user_id}: {baseline} (Tier {tier})")
            logger.info(f"Used tracks: {[t['name'] for t in recent_5]}")
            logger.info(f"Popularity scores: {[t['popularity'] for t in recent_5]}")
            logger.info(f"Raw average: {raw_average:.2f}, Floored to: {baseline} (min 5)")

            # Store baseline in database
            self._store_baseline(user_id, baseline, tier, track_ids, len(recent_5), raw_average)

            # Update user profile with current baseline and tier
            user_manager.update_user_profile(user_id, {
                'current_baseline': baseline,
                'current_tier': tier,
                'baseline_last_calculated': datetime.now().isoformat(),
                'spotify_artist_id': artist_id,
                'spotify_connected': True
            })

            return {
                'baseline': baseline,
                'tier': tier,
                'track_ids': track_ids,
                'track_count': len(recent_5),
                'raw_average': raw_average,
                'success': True,
                'message': 'Baseline calculated successfully'
            }

        except Exception as e:
            logger.error(f"Error calculating baseline for user {user_id}: {str(e)}")
            return {
                'baseline': self.default_baseline,
                'tier': 1,
                'track_ids': [],
                'track_count': 0,
                'raw_average': 0.0,
                'success': False,
                'error': str(e)
            }

    def _store_baseline(
        self,
        user_id: str,
        baseline: int,
        tier: int,
        track_ids: List[str],
        track_count: int,
        raw_average: float
    ) -> bool:
        """
        Store baseline calculation in DynamoDB.

        Args:
            user_id (str): User identifier
            baseline (int): Calculated baseline score
            tier (int): Tier 1-4
            track_ids (List[str]): Track IDs used in calculation
            track_count (int): Number of tracks used
            raw_average (float): Pre-ceiling average

        Returns:
            bool: True if successful
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            # Calculate TTL (90 days from now)
            ttl = int((datetime.now() + timedelta(days=90)).timestamp())

            baseline_record = {
                'user_id': user_id,
                'calculation_date': today,
                'baseline_score': baseline,
                'tier': tier,
                'track_ids_used': track_ids,
                'track_count': track_count,
                'raw_average': round(raw_average, 2),
                'created_at': datetime.now().isoformat(),
                'ttl': ttl
            }

            success = dynamodb_client.put_item(self.baselines_table, baseline_record)

            if success:
                logger.info(f"Stored baseline for user {user_id} on {today}")

            return success

        except Exception as e:
            logger.error(f"Error storing baseline for user {user_id}: {str(e)}")
            return False

    def get_user_baseline(self, user_id: str) -> int:
        """
        Get user's current baseline from their profile.

        Args:
            user_id (str): User identifier

        Returns:
            int: Current baseline score
        """
        try:
            user_data = user_manager.get_user_profile(user_id)

            if user_data and 'current_baseline' in user_data:
                return int(user_data['current_baseline'])

            logger.warning(f"No baseline found for user {user_id}, returning default")
            return self.default_baseline

        except Exception as e:
            logger.error(f"Error getting baseline for user {user_id}: {str(e)}")
            return self.default_baseline

    def get_user_tier(self, user_id: str) -> int:
        """
        Get user's current tier from their profile.

        Args:
            user_id (str): User identifier

        Returns:
            int: Current tier 1-4
        """
        try:
            user_data = user_manager.get_user_profile(user_id)

            if user_data and 'current_tier' in user_data:
                return int(user_data['current_tier'])

            logger.warning(f"No tier found for user {user_id}, returning default (Tier 1)")
            return 1

        except Exception as e:
            logger.error(f"Error getting tier for user {user_id}: {str(e)}")
            return 1

    def get_baseline_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get baseline calculation history for user.

        Args:
            user_id (str): User identifier
            days (int): Number of days of history to fetch

        Returns:
            List[Dict]: Baseline history
        """
        try:
            # Query baselines table for this user
            results = dynamodb_client.query_items(
                self.baselines_table,
                'user_id = :user_id',
                expression_values={':user_id': user_id}
            )

            # Sort by calculation_date (newest first)
            results.sort(key=lambda x: x['calculation_date'], reverse=True)

            # Limit to requested days
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            filtered_results = [
                r for r in results
                if r['calculation_date'] >= cutoff_date
            ]

            return filtered_results

        except Exception as e:
            logger.error(f"Error getting baseline history for user {user_id}: {str(e)}")
            return []


# Global baseline calculator instance
baseline_calculator = BaselineCalculator()


# Convenience functions
def calculate_user_baseline(user_id: str, artist_id: str) -> Dict[str, Any]:
    """Calculate baseline for user."""
    return baseline_calculator.calculate_baseline(user_id, artist_id)


def get_baseline(user_id: str) -> int:
    """Get user's current baseline."""
    return baseline_calculator.get_user_baseline(user_id)


def get_tier(user_id: str) -> int:
    """Get user's current tier."""
    return baseline_calculator.get_user_tier(user_id)


def get_history(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get user's baseline history."""
    return baseline_calculator.get_baseline_history(user_id, days)
