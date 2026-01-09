#!/usr/bin/env python3
"""
Reddit OAuth Test Script
Tests Reddit API credentials

Run: python3 test_reddit.py
"""

import os
import sys
import boto3
import secrets
import base64
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_ssm_param(name: str) -> str:
    """Get parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name='us-east-2')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        return None


def test_reddit_oauth():
    """Test Reddit OAuth credentials."""
    print("\n" + "="*60)
    print("REDDIT API OAUTH TEST")
    print("="*60)

    # Scopes for posting
    REQUIRED_SCOPES = [
        'identity',    # Access username
        'submit',      # Submit posts and links
        'read'         # Read subreddit content
    ]

    ALL_AVAILABLE_SCOPES = [
        'identity', 'edit', 'flair', 'history', 'modconfig',
        'modflair', 'modlog', 'modposts', 'modwiki', 'mysubreddits',
        'privatemessages', 'read', 'report', 'save', 'submit',
        'subscribe', 'vote', 'wikiedit', 'wikiread'
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    client_id = get_ssm_param('/noisemaker/reddit_client_id')
    client_secret = get_ssm_param('/noisemaker/reddit_client_secret')

    if not client_id:
        print("   [FAIL] /noisemaker/reddit_client_id NOT FOUND")
        print("   → Create app at https://www.reddit.com/prefs/apps")
        print("   → Choose 'web app' type")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:10]}...")

    if not client_secret:
        print("   [FAIL] /noisemaker/reddit_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. ALL AVAILABLE SCOPES:")
    print(f"   {', '.join(ALL_AVAILABLE_SCOPES)}")
    print("   → Full list: https://www.reddit.com/api/v1/scopes")

    print("\n4. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/reddit"
    scopes = '%20'.join(REQUIRED_SCOPES)  # Space-separated, URL encoded
    state = secrets.token_urlsafe(16)

    auth_url = (
        f"https://www.reddit.com/api/v1/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&state={state}"
        f"&redirect_uri={redirect_uri}"
        f"&duration=permanent"
        f"&scope={scopes}"
    )

    print("\n5. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n6. VERIFICATION CHECKLIST:")
    print("   [ ] Reddit app created at /prefs/apps?")
    print("   [ ] App type is 'web app'?")
    print("   [ ] Redirect URI matches exactly?")

    print("\n7. TOKEN DETAILS:")
    print("   • Access token expires in 1 hour")
    print("   • Use duration=permanent for refresh token")
    print("   • Refresh tokens are long-lived")

    print("\n8. RATE LIMITS:")
    print("   • 60 requests per minute")
    print("   • Must include User-Agent header")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_reddit_oauth()
