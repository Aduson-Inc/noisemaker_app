#!/usr/bin/env python3
"""
Instagram OAuth Test Script
Tests Meta/Instagram API credentials and permissions

Run: python3 test_instagram.py
"""

import os
import sys
import boto3
import requests

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_ssm_param(name: str) -> str:
    """Get parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name='us-east-2')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        return None


def test_instagram_oauth():
    """Test Instagram/Meta OAuth credentials."""
    print("\n" + "="*60)
    print("INSTAGRAM / META OAUTH TEST")
    print("="*60)

    # Required scopes for posting
    REQUIRED_SCOPES = [
        'instagram_basic',
        'instagram_content_publish',
        'pages_show_list',
        'pages_read_engagement'
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    # Check for credentials
    client_id = get_ssm_param('/noisemaker/instagram_client_id')
    client_secret = get_ssm_param('/noisemaker/instagram_client_secret')

    if not client_id:
        print("   [FAIL] /noisemaker/instagram_client_id NOT FOUND")
        print("   → Create Meta App at https://developers.facebook.com/")
        print("   → Store client_id in SSM Parameter Store")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:10]}...")

    if not client_secret:
        print("   [FAIL] /noisemaker/instagram_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. GENERATING TEST AUTH URL...")

    # Build authorization URL
    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/instagram"
    scopes = ','.join(REQUIRED_SCOPES)

    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
        f"&response_type=code"
    )

    print(f"   Auth URL: {auth_url[:80]}...")
    print("\n4. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n5. VERIFICATION CHECKLIST:")
    print("   [ ] Meta App approved for instagram_content_publish?")
    print("   [ ] Instagram Business/Creator account linked to Facebook Page?")
    print("   [ ] Redirect URI registered in Meta App settings?")
    print("   [ ] App in Live mode (not Development)?")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_instagram_oauth()
