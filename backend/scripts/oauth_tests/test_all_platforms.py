#!/usr/bin/env python3
"""
Master OAuth Test Script
Tests all 8 platform OAuth configurations

Run: python3 test_all_platforms.py
"""

import os
import sys
import subprocess

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

SCRIPTS_DIR = os.path.dirname(__file__)

PLATFORM_TESTS = [
    ('instagram', 'test_instagram.py'),
    ('twitter', 'test_twitter.py'),
    ('facebook', 'test_facebook.py'),
    ('tiktok', 'test_tiktok.py'),
    ('youtube', 'test_youtube.py'),
    ('reddit', 'test_reddit.py'),
    ('discord', 'test_discord.py'),
    ('threads', 'test_threads.py'),
]


def run_all_tests():
    """Run all platform OAuth tests."""
    print("\n" + "="*70)
    print("NOISEMAKER - FULL PLATFORM OAUTH AUDIT")
    print("="*70)
    print("\nThis will test OAuth credentials for all 8 platforms:")
    print("  1. Instagram (Meta)")
    print("  2. Twitter/X")
    print("  3. Facebook (Meta)")
    print("  4. TikTok")
    print("  5. YouTube (Google)")
    print("  6. Reddit")
    print("  7. Discord (Bot)")
    print("  8. Threads (Meta)")

    results = {}

    for platform, script in PLATFORM_TESTS:
        script_path = os.path.join(SCRIPTS_DIR, script)

        try:
            # Import and run the test function
            module_name = script.replace('.py', '')
            exec(open(script_path).read())

            # Get the test function based on platform
            if platform == 'discord':
                test_func = test_discord_bot
            else:
                test_func = eval(f'test_{platform}_oauth')

            success = test_func()
            results[platform] = 'OK' if success else 'FAIL'

        except Exception as e:
            print(f"\n[ERROR] Failed to run {script}: {e}")
            results[platform] = 'ERROR'

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for platform, status in results.items():
        icon = '✓' if status == 'OK' else '✗'
        print(f"  {icon} {platform.upper()}: {status}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("  1. Fix any [FAIL] credentials in AWS SSM Parameter Store")
    print("  2. Test each auth URL in browser manually")
    print("  3. Complete OAuth flow to verify end-to-end")
    print("  4. Check app review status for each platform")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run individual tests if platform specified
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        script = f'test_{platform}.py'
        script_path = os.path.join(SCRIPTS_DIR, script)

        if os.path.exists(script_path):
            exec(open(script_path).read())
            if platform == 'discord':
                test_discord_bot()
            else:
                eval(f'test_{platform}_oauth')()
        else:
            print(f"Unknown platform: {platform}")
            print(f"Available: {', '.join([p for p, _ in PLATFORM_TESTS])}")
    else:
        run_all_tests()
