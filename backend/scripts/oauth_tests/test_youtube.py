#!/usr/bin/env python3
"""
YouTube OAuth Test Script
Tests Google/YouTube Data API v3 credentials

Run: python3 test_youtube.py
"""

import os
import sys
import boto3
import secrets

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_ssm_param(name: str) -> str:
    """Get parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name='us-east-2')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        return None


def test_youtube_oauth():
    """Test YouTube/Google OAuth credentials."""
    print("\n" + "="*60)
    print("YOUTUBE DATA API v3 OAUTH TEST")
    print("="*60)

    # Scopes for video upload
    REQUIRED_SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',   # Upload videos/Shorts
        'https://www.googleapis.com/auth/youtube'           # Full account access
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    client_id = get_ssm_param('/noisemaker/youtube_client_id')
    client_secret = get_ssm_param('/noisemaker/youtube_client_secret')

    if not client_id:
        print("   [FAIL] /noisemaker/youtube_client_id NOT FOUND")
        print("   → Create project at https://console.cloud.google.com/")
        print("   → Enable YouTube Data API v3")
        print("   → Create OAuth 2.0 credentials")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:20]}...")

    if not client_secret:
        print("   [FAIL] /noisemaker/youtube_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/youtube"
    scopes = '%20'.join(REQUIRED_SCOPES)  # Space-separated, URL encoded
    state = secrets.token_urlsafe(16)

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
        f"&response_type=code"
        f"&state={state}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    print("\n4. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n5. VERIFICATION CHECKLIST:")
    print("   [ ] Google Cloud project created?")
    print("   [ ] YouTube Data API v3 enabled?")
    print("   [ ] OAuth consent screen configured?")
    print("   [ ] OAuth consent screen verified by Google?")
    print("   [ ] Redirect URI added to authorized redirects?")

    print("\n6. IMPORTANT LIMITATION:")
    print("   ⚠️  COMMUNITY POSTS NOT SUPPORTED!")
    print("      YouTube API does NOT allow posting to Community tab.")
    print("      Only video/Shorts uploads are available via API.")

    print("\n7. UPLOAD CAPABILITIES:")
    print("   ✓  Regular videos")
    print("   ✓  YouTube Shorts (vertical video < 60 seconds)")
    print("   ✗  Community posts (NOT available)")
    print("   ✗  Stories (NOT available)")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_youtube_oauth()
