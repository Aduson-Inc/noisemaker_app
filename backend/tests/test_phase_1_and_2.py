"""
Comprehensive Test Suite for Phase 1 & Phase 2 Fixes
Tests all critical business logic and edge cases.

Author: Senior Python Backend Engineer
Version: 1.0
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import modules to test
from spotify.track_analyzer import TrackAnalyzer, TrackMetrics, PromotionStage, track_analyzer
from data.song_manager import SongManager, song_manager


def create_test_track_metrics(
    track_id: str,
    days_in_promotion: int,
    promotion_stage: PromotionStage,
    fire_mode_active: bool = False,
    focus_percentage: float = 33.3
) -> TrackMetrics:
    """Helper function to create TrackMetrics for testing."""
    return TrackMetrics(
        track_id=track_id,
        current_streams=1000,
        previous_streams=900,
        daily_average=50.0,
        growth_rate=1.1,
        days_since_release=days_in_promotion,
        fire_mode_eligible=fire_mode_active,
        fire_mode_active=fire_mode_active,
        promotion_stage=promotion_stage,
        days_in_promotion=days_in_promotion,
        focus_percentage=focus_percentage
    )


class TestSongStagingLogic(unittest.TestCase):
    """Test Phase 2 fix: Song staging with correct days_in_promotion values."""

    def setUp(self):
        """Set up test fixtures."""
        self.song_manager = SongManager()
        self.user_id = "test_user_001"

    def test_initial_stage_assignment_best_song(self):
        """Test that best song gets 14 days → LIVE stage."""
        existing_songs = []  # No existing songs
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position='best'
        )

        self.assertEqual(days, 14, "Best song should start at 14 days")
        self.assertEqual(stage, 'live', "Best song should be in LIVE stage")

    def test_initial_stage_assignment_second_song(self):
        """Test that second song gets 28 days → TWILIGHT stage."""
        existing_songs = []
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position='second'
        )

        self.assertEqual(days, 28, "Second song should start at 28 days")
        self.assertEqual(stage, 'twilight', "Second song should be in TWILIGHT stage")

    def test_initial_stage_assignment_upcoming_song(self):
        """Test that upcoming song gets 0 days → UPCOMING stage."""
        existing_songs = []
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position='upcoming'
        )

        self.assertEqual(days, 0, "Upcoming song should start at 0 days")
        self.assertEqual(stage, 'upcoming', "Upcoming song should be in UPCOMING stage")

    def test_auto_detection_first_song(self):
        """Test auto-detection assigns first song as best (14 days, LIVE)."""
        existing_songs = []  # 0 existing songs
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position=None
        )

        self.assertEqual(days, 14, "First song auto-detected should be best (14 days)")
        self.assertEqual(stage, 'live', "First song auto-detected should be LIVE")

    def test_auto_detection_second_song(self):
        """Test auto-detection assigns second song as second best (28 days, TWILIGHT)."""
        existing_songs = [{'song_id': 'song1'}]  # 1 existing song
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position=None
        )

        self.assertEqual(days, 28, "Second song auto-detected should be 28 days")
        self.assertEqual(stage, 'twilight', "Second song auto-detected should be TWILIGHT")

    def test_auto_detection_third_song(self):
        """Test auto-detection assigns third song as upcoming (0 days, UPCOMING)."""
        existing_songs = [{'song_id': 'song1'}, {'song_id': 'song2'}]  # 2 existing songs
        days, stage = self.song_manager._determine_initial_stage_and_days(
            self.user_id, existing_songs, position=None
        )

        self.assertEqual(days, 0, "Third song auto-detected should be 0 days")
        self.assertEqual(stage, 'upcoming', "Third song auto-detected should be UPCOMING")


class TestFireModeLogic(unittest.TestCase):
    """Test Phase 1 fix: Fire Mode logic without 7-day cap."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrackAnalyzer()

    def test_fire_mode_threshold_is_2x(self):
        """Test that Fire Mode threshold is set to 2.0 (2× user average)."""
        self.assertEqual(self.analyzer.fire_mode_threshold, 2.0,
                        "Fire Mode threshold should be 2× user average")

    def test_fire_mode_no_duration_limit(self):
        """Test that Fire Mode has no duration limit in __init__."""
        # Check that fire_mode_duration is NOT in the instance
        self.assertFalse(hasattr(self.analyzer, 'fire_mode_duration'),
                        "Fire Mode should NOT have a duration limit")

    def test_fire_mode_consecutive_days_requirement(self):
        """Test that Fire Mode requires 2 consecutive days above threshold."""
        self.assertEqual(self.analyzer.fire_mode_consecutive_days, 2,
                        "Fire Mode should require 2 consecutive days")

    def test_fire_mode_minimum_baseline(self):
        """Test that Fire Mode has minimum baseline of 50 streams."""
        # Test with baseline below 50
        user_tracks = [
            {
                'stream_count': 30,
                'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
                'release_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            }
        ]

        baseline = self.analyzer.initialize_user_baseline('test_user', user_tracks)

        # Should enforce minimum of 50.0
        # This means Fire Mode requires 100 streams/day (2× threshold)
        self.assertEqual(baseline, 50.0, "Baseline should enforce minimum of 50.0")
        self.assertIsInstance(baseline, (int, float), "Baseline should be numeric")


class TestPostDistribution(unittest.TestCase):
    """Test Phase 1 fix: Post distribution based on platforms × schedule."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrackAnalyzer()

    def test_fire_mode_gets_70_percent(self):
        """Test that Fire Mode song gets 70% of posts."""
        # Create track metrics
        upcoming_song = create_test_track_metrics(
            track_id='upcoming_track',
            days_in_promotion=5,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=20.0
        )

        live_song = create_test_track_metrics(
            track_id='live_track',
            days_in_promotion=20,
            promotion_stage=PromotionStage.LIVE,
            fire_mode_active=True,  # Fire Mode active
            focus_percentage=70.0
        )

        twilight_song = create_test_track_metrics(
            track_id='twilight_track',
            days_in_promotion=35,
            promotion_stage=PromotionStage.TWILIGHT,
            fire_mode_active=False,
            focus_percentage=30.0
        )

        metrics = [upcoming_song, live_song, twilight_song]
        total_posts = 10

        distribution = self.analyzer.distribute_daily_posts(metrics, total_posts)

        # Fire Mode song should get 7 posts (70% of 10)
        self.assertEqual(distribution['live_track'], 7,
                        "Fire Mode song (live song) should get 70% = 7 posts")

        # Other songs split remaining 3 posts (30%)
        total_other_posts = distribution['upcoming_track'] + distribution['twilight_track']
        self.assertEqual(total_other_posts, 3,
                        "Non-Fire Mode songs should split remaining 30% = 3 posts")

    def test_stage_distribution_no_fire_mode(self):
        """Test stage-based distribution: 20% upcoming, 50% live, 30% twilight."""
        upcoming_song = create_test_track_metrics(
            track_id='upcoming_track',
            days_in_promotion=5,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=20.0
        )

        live_song = create_test_track_metrics(
            track_id='live_track',
            days_in_promotion=20,
            promotion_stage=PromotionStage.LIVE,
            fire_mode_active=False,
            focus_percentage=50.0
        )

        twilight_song = create_test_track_metrics(
            track_id='twilight_track',
            days_in_promotion=35,
            promotion_stage=PromotionStage.TWILIGHT,
            fire_mode_active=False,
            focus_percentage=30.0
        )

        metrics = [upcoming_song, live_song, twilight_song]
        total_posts = 10

        distribution = self.analyzer.distribute_daily_posts(metrics, total_posts)

        # Check distribution percentages
        self.assertEqual(distribution['upcoming_track'], 2,
                        "Upcoming song should get 20% = 2 posts")
        self.assertEqual(distribution['live_track'], 5,
                        "Live song should get 50% = 5 posts")
        self.assertEqual(distribution['twilight_track'], 3,
                        "Twilight song should get 30% = 3 posts")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases: 1 song, 2 songs, misaligned timing."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrackAnalyzer()
        self.song_manager = SongManager()

    def test_one_song_only(self):
        """Test system with only 1 song."""
        single_song = create_test_track_metrics(
            track_id='only_track',
            days_in_promotion=10,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=100.0
        )

        metrics = [single_song]
        total_posts = 10

        distribution = self.analyzer.distribute_daily_posts(metrics, total_posts)

        # Single song should get all posts
        self.assertEqual(distribution['only_track'], 10,
                        "Single song should get 100% of posts")

    def test_two_songs_only(self):
        """Test system with only 2 songs."""
        song_1 = create_test_track_metrics(
            track_id='track_1',
            days_in_promotion=5,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=40.0
        )

        song_2 = create_test_track_metrics(
            track_id='track_2',
            days_in_promotion=20,
            promotion_stage=PromotionStage.LIVE,
            fire_mode_active=False,
            focus_percentage=60.0
        )

        metrics = [song_1, song_2]
        total_posts = 10

        distribution = self.analyzer.distribute_daily_posts(metrics, total_posts)

        # Should distribute based on focus percentages
        self.assertEqual(distribution['track_1'], 4,
                        "Track 1 should get 40% = 4 posts")
        self.assertEqual(distribution['track_2'], 6,
                        "Track 2 should get 60% = 6 posts")

    def test_misaligned_song_ages(self):
        """Test songs with misaligned ages: 38 days, 12 days, 5 days."""
        # This test verifies the system can handle songs with non-standard timing
        # Song at day 38 (TWILIGHT stage - very old)
        old_song = create_test_track_metrics(
            track_id='old_track',
            days_in_promotion=38,
            promotion_stage=PromotionStage.TWILIGHT,
            fire_mode_active=False,
            focus_percentage=30.0
        )

        # Song at day 12 (UPCOMING stage - about to go live)
        mid_song = create_test_track_metrics(
            track_id='mid_track',
            days_in_promotion=12,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=20.0
        )

        # Song at day 5 (UPCOMING stage - new)
        new_song = create_test_track_metrics(
            track_id='new_track',
            days_in_promotion=5,
            promotion_stage=PromotionStage.UPCOMING,
            fire_mode_active=False,
            focus_percentage=20.0
        )

        metrics = [old_song, mid_song, new_song]
        total_posts = 10

        distribution = self.analyzer.distribute_daily_posts(metrics, total_posts)

        # Verify all posts are distributed
        total_distributed = sum(distribution.values())
        self.assertEqual(total_distributed, 10,
                        "All 10 posts should be distributed even with misaligned ages")

        # Verify all tracks received at least some posts
        for track_id in ['old_track', 'mid_track', 'new_track']:
            self.assertGreater(distribution.get(track_id, 0), 0,
                             f"Track {track_id} should receive at least 1 post")


class TestBaselineCalculation(unittest.TestCase):
    """Test Phase 2: User baseline stream calculation."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrackAnalyzer()

    def test_baseline_calculation_from_tracks(self):
        """Test baseline calculation from user's track data."""
        # Create mock track data
        user_tracks = [
            {
                'stream_count': 1000,
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'release_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            },
            {
                'stream_count': 500,
                'created_at': (datetime.now() - timedelta(days=20)).isoformat(),
                'release_date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
            },
            {
                'stream_count': 300,
                'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
                'release_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            }
        ]

        baseline = self.analyzer.calculate_user_baseline_streams(user_tracks)

        # Baseline should be calculated as average daily streams
        # Track 1: 1000/30 = 33.33 streams/day
        # Track 2: 500/20 = 25 streams/day
        # Track 3: 300/10 = 30 streams/day
        # Average: (33.33 + 25 + 30) / 3 = 29.44 streams/day

        self.assertGreater(baseline, 0, "Baseline should be greater than 0")
        self.assertIsInstance(baseline, float, "Baseline should be float")

    def test_baseline_minimum_default(self):
        """Test that baseline defaults to 50.0 when calculated below minimum."""
        user_tracks = [
            {
                'stream_count': 0,
                'created_at': datetime.now().isoformat(),
                'release_date': datetime.now().strftime('%Y-%m-%d')
            }
        ]

        baseline = self.analyzer.initialize_user_baseline('test_user', user_tracks)

        # Should default to 50.0 when streams are below minimum
        # This ensures Fire Mode requires 100 streams/day (2× threshold)
        # Creates excitement for artists hitting 100 streams/day milestone
        self.assertEqual(baseline, 50.0,
                        "Baseline should enforce minimum of 50.0 for quality control")


class TestPlatformRotation(unittest.TestCase):
    """Test Phase 2: Platform rotation logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrackAnalyzer()

    def test_platform_assignment_basic(self):
        """Test basic platform assignment with 3 songs."""
        post_distribution = {
            'upcoming_track': 2,
            'live_track': 5,
            'twilight_track': 3
        }

        enabled_platforms = ['instagram', 'twitter', 'facebook', 'youtube', 'tiktok']

        platform_assignments = self.analyzer.assign_platforms_to_tracks(
            post_distribution, enabled_platforms
        )

        # Check that each song got the correct number of platform assignments
        self.assertEqual(len(platform_assignments['upcoming_track']), 2,
                        "Upcoming song should have 2 platform assignments")
        self.assertEqual(len(platform_assignments['live_track']), 5,
                        "Live song should have 5 platform assignments")
        self.assertEqual(len(platform_assignments['twilight_track']), 3,
                        "Twilight song should have 3 platform assignments")

        # Check that all platforms are from enabled list
        for track_id, platforms in platform_assignments.items():
            for platform in platforms:
                self.assertIn(platform, enabled_platforms,
                            f"Platform {platform} should be in enabled platforms list")

    def test_platform_rotation_avoids_repetition(self):
        """Test that platform rotation considers history to avoid repetition."""
        post_distribution = {'live_track': 5}
        enabled_platforms = ['instagram', 'twitter', 'facebook']

        # Track was recently on instagram and twitter
        track_platform_history = {
            'live_track': ['instagram', 'twitter', 'instagram']
        }

        platform_assignments = self.analyzer.assign_platforms_to_tracks(
            post_distribution, enabled_platforms, track_platform_history
        )

        # Should have 5 platform assignments
        self.assertEqual(len(platform_assignments['live_track']), 5,
                        "Live song should have 5 platform assignments")

        # Facebook should be preferred since it wasn't used recently
        platforms = platform_assignments['live_track']
        facebook_count = platforms.count('facebook')

        # Facebook should appear at least once (likely more due to lower penalty)
        self.assertGreaterEqual(facebook_count, 1,
                              "Facebook should be used since it has no recent history")

    def test_platform_distribution_with_limited_platforms(self):
        """Test platform assignment when posts exceed available platforms."""
        post_distribution = {'live_track': 10}
        enabled_platforms = ['instagram', 'twitter', 'facebook']  # Only 3 platforms

        platform_assignments = self.analyzer.assign_platforms_to_tracks(
            post_distribution, enabled_platforms
        )

        # Should have 10 platform assignments (will cycle through platforms)
        self.assertEqual(len(platform_assignments['live_track']), 10,
                        "Should assign 10 platforms even with only 3 available")

        # All platforms should be used multiple times
        platforms = platform_assignments['live_track']
        for platform in enabled_platforms:
            self.assertIn(platform, platforms,
                         f"Platform {platform} should be used at least once")


def run_all_tests():
    """Run all test suites and print results."""
    print("=" * 70)
    print("PHASE 1 & PHASE 2 COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSongStagingLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestFireModeLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestPostDistribution))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestBaselineCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformRotation))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print()
        print("✅ ALL TESTS PASSED! Ready for Phase 3.")
    else:
        print()
        print("❌ SOME TESTS FAILED. Review failures above.")

    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
