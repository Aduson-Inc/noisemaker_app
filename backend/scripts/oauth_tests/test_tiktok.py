#!/usr/bin/env python3
"""
TikTok OAuth Test Script
Tests TikTok Content Posting API credentials

Run: python3 test_tiktok.py
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


def test_tiktok_oauth():
    """Test TikTok OAuth credentials."""
    print("\n" + "="*60)
    print("TIKTOK CONTENT POSTING API OAUTH TEST")
    print("="*60)

    # Scopes for video posting
    REQUIRED_SCOPES = [
        'user.info.basic',     # Basic user info
        'video.upload',        # Upload videos (user clicks to complete)
        'video.publish'        # Direct post (requires audit approval)
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    client_key = get_ssm_param('/noisemaker/tiktok_client_id')
    client_secret = get_ssm_param('/noisemaker/tiktok_client_secret')

    if not client_key:
        print("   [FAIL] /noisemaker/tiktok_client_id NOT FOUND")
        print("   → Create TikTok Developer App at https://developers.tiktok.com/")
        print("   → Apply for Content Posting API access")
        return False
    else:
        print(f"   [OK] Client Key found: {client_key[:10]}...")

    if not client_secret:
        print("   [FAIL] /noisemaker/tiktok_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        desc = {
            'user.info.basic': '(user profile access)',
            'video.upload': '(upload - user confirms in app)',
            'video.publish': '(direct post - requires audit)'
        }.get(scope, '')
        print(f"   • {scope} {desc}")

    print("\n3. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/tiktok"
    scopes = ','.join(REQUIRED_SCOPES)
    state = secrets.token_urlsafe(16)

    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize"
        f"?client_key={client_key}"
        f"&scope={scopes}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )

    print("\n4. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n5. VERIFICATION CHECKLIST:")
    print("   [ ] TikTok Developer App created?")
    print("   [ ] Content Posting API access approved?")
    print("   [ ] App passed TikTok audit for public posting?")
    print("   [ ] Redirect URI registered?")

    print("\n6. IMPORTANT RESTRICTIONS:")
    print("   ⚠️  UNAUDITED APPS:")
    print("      • Limited to 5 users per 24 hours")
    print("      • All posts are PRIVATE visibility only")
    print("      • Users must be in 'private mode'")
    print("")
    print("   ✓  AUDITED APPS:")
    print("      • ~15 posts per day per creator")
    print("      • Public visibility available")

    print("\n7. TOKEN DETAILS:")
    print("   • Access token expires in 24 hours")
    print("   • Refresh token for long-term access")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_tiktok_oauth()
