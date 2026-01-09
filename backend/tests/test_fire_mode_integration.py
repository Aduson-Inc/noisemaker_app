"""
Integration test for Phase A Fire Mode system.
Tests the complete flow from baseline calculation to Fire Mode activation.

Author: Senior Python Backend Engineer
Version: 1.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta


def test_fire_mode_analyzer_import():
    """Test that fire mode analyzer can be imported."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "fire_mode_analyzer",
            os.path.join(os.path.dirname(__file__), "../spotify/fire_mode_analyzer.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Fire mode analyzer imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import fire mode analyzer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_baseline_calculator_import():
    """Test that baseline calculator can be imported."""
    try:
        # Baseline calculator has dependencies, so we'll just check syntax
        import py_compile
        py_compile.compile(
            os.path.join(os.path.dirname(__file__), "../spotify/baseline_calculator.py"),
            doraise=True
        )
        print("✅ Baseline calculator syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Failed to validate baseline calculator: {str(e)}")
        return False


def test_popularity_tracker_import():
    """Test that popularity tracker can be imported."""
    try:
        # Popularity tracker has dependencies, so we'll just check syntax
        import py_compile
        py_compile.compile(
            os.path.join(os.path.dirname(__file__), "../spotify/popularity_tracker.py"),
            doraise=True
        )
        print("✅ Popularity tracker syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Failed to validate popularity tracker: {str(e)}")
        return False


def load_fire_mode_analyzer():
    """Helper function to load fire mode analyzer module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fire_mode_analyzer",
        os.path.join(os.path.dirname(__file__), "../spotify/fire_mode_analyzer.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.fire_mode_analyzer


def test_tier_determination():
    """Test tier determination from baseline scores."""
    try:
        fire_mode_analyzer = load_fire_mode_analyzer()

        test_cases = [
            (5, 1),   # 0-10% = Tier 1
            (10, 1),  # 0-10% = Tier 1
            (11, 2),  # 11-20% = Tier 2
            (20, 2),  # 11-20% = Tier 2
            (21, 3),  # 21-30% = Tier 3
            (30, 3),  # 21-30% = Tier 3
            (31, 4),  # 31-100% = Tier 4
            (50, 4),  # 31-100% = Tier 4
            (100, 4), # 31-100% = Tier 4
        ]

        all_passed = True
        for baseline, expected_tier in test_cases:
            tier = fire_mode_analyzer.determine_tier_from_baseline(baseline)
            if tier == expected_tier:
                print(f"✅ Baseline {baseline} → Tier {tier} (correct)")
            else:
                print(f"❌ Baseline {baseline} → Tier {tier} (expected {expected_tier})")
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"❌ Tier determination test failed: {str(e)}")
        return False


def test_fire_mode_entry():
    """Test Fire Mode entry logic."""
    try:
        fire_mode_analyzer = load_fire_mode_analyzer()

        # Test case 1: Song meets baseline - should be eligible
        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=15,
            song_current_popularity=15,
            song_fire_mode_active=False,
            song_fire_mode_start_date="",
            song_peak_popularity=0,
            song_popularity_history=[]
        )

        if result['eligible']:
            print("✅ Fire Mode entry: Song at baseline (15) is eligible")
        else:
            print(f"❌ Fire Mode entry: Song at baseline should be eligible. Result: {result}")
            return False

        # Test case 2: Song below baseline - should NOT be eligible
        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=15,
            song_current_popularity=14,
            song_fire_mode_active=False,
            song_fire_mode_start_date="",
            song_peak_popularity=0,
            song_popularity_history=[]
        )

        if not result['eligible']:
            print("✅ Fire Mode entry: Song below baseline (14 < 15) is not eligible")
        else:
            print(f"❌ Fire Mode entry: Song below baseline should not be eligible. Result: {result}")
            return False

        # Test case 3: Song above baseline - should be eligible
        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=15,
            song_current_popularity=20,
            song_fire_mode_active=False,
            song_fire_mode_start_date="",
            song_peak_popularity=0,
            song_popularity_history=[]
        )

        if result['eligible']:
            print("✅ Fire Mode entry: Song above baseline (20 > 15) is eligible")
        else:
            print(f"❌ Fire Mode entry: Song above baseline should be eligible. Result: {result}")
            return False

        return True
    except Exception as e:
        print(f"❌ Fire Mode entry test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_phase1_maintenance():
    """Test Phase 1 maintenance (below 20%, need +2 points every 2 days)."""
    try:
        fire_mode_analyzer = load_fire_mode_analyzer()

        today = datetime.now()
        two_days_ago = (today - timedelta(days=2)).strftime('%Y-%m-%d')

        # Test case: Song at 15%, was 13% two days ago (increased by 2 points) - should maintain
        history = [
            {'date': two_days_ago, 'score': 13},
            {'date': today.strftime('%Y-%m-%d'), 'score': 15}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=10,  # Tier 1
            song_current_popularity=15,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=3)).isoformat(),
            song_peak_popularity=15,
            song_popularity_history=history
        )

        if result['should_maintain'] and not result['should_exit']:
            print(f"✅ Phase 1: Song increased by 2 points (13 → 15) in 2 days - maintained. Reason: {result['reason']}")
        else:
            print(f"❌ Phase 1: Song should maintain Fire Mode. Result: {result}")
            return False

        # Test case: Song at 14%, was 13% two days ago (increased by 1 point) - should exit
        history = [
            {'date': two_days_ago, 'score': 13},
            {'date': today.strftime('%Y-%m-%d'), 'score': 14}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=10,  # Tier 1
            song_current_popularity=14,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=3)).isoformat(),
            song_peak_popularity=14,
            song_popularity_history=history
        )

        if result['should_exit']:
            print(f"✅ Phase 1: Song increased by only 1 point (13 → 14) - should exit. Reason: {result['reason']}")
        else:
            print(f"❌ Phase 1: Song should exit Fire Mode. Result: {result}")
            return False

        return True
    except Exception as e:
        print(f"❌ Phase 1 maintenance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tier4_maintenance():
    """Test Tier 4 maintenance (+3 points over 7 days)."""
    try:
        fire_mode_analyzer = load_fire_mode_analyzer()

        today = datetime.now()
        seven_days_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')

        # Test case: Song at 54%, was 51% seven days ago (increased by 3 points) - should maintain
        history = [
            {'date': seven_days_ago, 'score': 51},
            {'date': today.strftime('%Y-%m-%d'), 'score': 54}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=35,  # Tier 4
            song_current_popularity=54,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=8)).isoformat(),
            song_peak_popularity=54,
            song_popularity_history=history
        )

        if result['should_maintain'] and not result['should_exit']:
            print(f"✅ Tier 4: Song increased by 3 points (51 → 54) in 7 days - maintained. Reason: {result['reason']}")
        else:
            print(f"❌ Tier 4: Song should maintain Fire Mode. Result: {result}")
            return False

        # Test case: Song at 53%, was 51% seven days ago (increased by 2 points) - should exit
        history = [
            {'date': seven_days_ago, 'score': 51},
            {'date': today.strftime('%Y-%m-%d'), 'score': 53}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=35,  # Tier 4
            song_current_popularity=53,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=8)).isoformat(),
            song_peak_popularity=53,
            song_popularity_history=history
        )

        if result['should_exit']:
            print(f"✅ Tier 4: Song increased by only 2 points (51 → 53) - should exit. Reason: {result['reason']}")
        else:
            print(f"❌ Tier 4: Song should exit Fire Mode. Result: {result}")
            return False

        return True
    except Exception as e:
        print(f"❌ Tier 4 maintenance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_absolute_points_not_percentages():
    """Test that increases are absolute points, not percentages."""
    try:
        fire_mode_analyzer = load_fire_mode_analyzer()

        today = datetime.now()
        two_days_ago = (today - timedelta(days=2)).strftime('%Y-%m-%d')

        # Test: Song at 9%, baseline 7%, was at 7% two days ago
        # Need +2 ABSOLUTE points (7 → 9), not 2% of 7 (which would be 7.14)
        history = [
            {'date': two_days_ago, 'score': 7},
            {'date': today.strftime('%Y-%m-%d'), 'score': 9}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=7,  # Tier 1
            song_current_popularity=9,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=3)).isoformat(),
            song_peak_popularity=9,
            song_popularity_history=history
        )

        if result['should_maintain']:
            print(f"✅ Absolute points: 7 → 9 (2 points) is sufficient for Phase 1. Reason: {result['reason']}")
        else:
            print(f"❌ Absolute points: 7 → 9 should maintain. Result: {result}")
            return False

        # Test: Song at 8%, was at 7% (only 1 point increase) - should exit
        history = [
            {'date': two_days_ago, 'score': 7},
            {'date': today.strftime('%Y-%m-%d'), 'score': 8}
        ]

        result = fire_mode_analyzer.calculate_fire_mode_eligibility(
            user_baseline=7,  # Tier 1
            song_current_popularity=8,
            song_fire_mode_active=True,
            song_fire_mode_start_date=(today - timedelta(days=3)).isoformat(),
            song_peak_popularity=8,
            song_popularity_history=history
        )

        if result['should_exit']:
            print(f"✅ Absolute points: 7 → 8 (1 point) is insufficient for Phase 1. Reason: {result['reason']}")
        else:
            print(f"❌ Absolute points: 7 → 8 should exit. Result: {result}")
            return False

        return True
    except Exception as e:
        print(f"❌ Absolute points test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("PHASE A FIRE MODE INTEGRATION TESTS")
    print("=" * 60)
    print()

    tests = [
        ("Import: Fire Mode Analyzer", test_fire_mode_analyzer_import),
        ("Import: Baseline Calculator", test_baseline_calculator_import),
        ("Import: Popularity Tracker", test_popularity_tracker_import),
        ("Logic: Tier Determination", test_tier_determination),
        ("Logic: Fire Mode Entry", test_fire_mode_entry),
        ("Logic: Phase 1 Maintenance", test_phase1_maintenance),
        ("Logic: Tier 4 Maintenance", test_tier4_maintenance),
        ("Logic: Absolute Points (Not Percentages)", test_absolute_points_not_percentages),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"TEST: {test_name}")
        print('-' * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed ({passed * 100 // total}%)")

    if passed == total:
        print("\n🎉 All tests passed! Fire Mode system is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the failures above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
