#!/usr/bin/env python3
"""
Threads OAuth Test Script
Tests Meta/Threads API credentials

Run: python3 test_threads.py
"""

import os
import sys
import boto3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_ssm_param(name: str) -> str:
    """Get parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name='us-east-2')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        return None


def test_threads_oauth():
    """Test Threads/Meta OAuth credentials."""
    print("\n" + "="*60)
    print("THREADS (META) API OAUTH TEST")
    print("="*60)

    # Required scopes for posting
    REQUIRED_SCOPES = [
        'threads_basic',           # Read user profile and posts
        'threads_content_publish'  # Post text, images, videos, carousels
    ]

    OPTIONAL_SCOPES = [
        'threads_read_replies',
        'threads_manage_replies',
        'threads_manage_insights'
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    # Threads uses same Meta App as Instagram/Facebook
    client_id = get_ssm_param('/noisemaker/threads_client_id')
    client_secret = get_ssm_param('/noisemaker/threads_client_secret')

    # Fallback to instagram credentials (same Meta App)
    if not client_id:
        client_id = get_ssm_param('/noisemaker/instagram_client_id')
        if client_id:
            print("   [INFO] Using shared Meta App credentials from Instagram")

    if not client_id:
        print("   [FAIL] /noisemaker/threads_client_id NOT FOUND")
        print("   → Use same Meta App as Instagram/Facebook")
        print("   → Enable Threads API in Meta App settings")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:10]}...")

    if not client_secret:
        client_secret = get_ssm_param('/noisemaker/instagram_client_secret')

    if not client_secret:
        print("   [FAIL] /noisemaker/threads_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. OPTIONAL SCOPES:")
    for scope in OPTIONAL_SCOPES:
        print(f"   • {scope}")

    print("\n4. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/threads"
    scopes = ','.join(REQUIRED_SCOPES)

    auth_url = (
        f"https://threads.net/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
        f"&response_type=code"
    )

    print("\n5. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n6. VERIFICATION CHECKLIST:")
    print("   [ ] Meta App has Threads API enabled?")
    print("   [ ] App approved for threads_content_publish?")
    print("   [ ] User has Threads account linked to Instagram?")
    print("   [ ] Redirect URI registered in Meta App?")
    print("   [ ] App in Live mode?")

    print("\n7. POSTING FLOW:")
    print("   1. Create container: POST /threads with media")
    print("   2. Publish: POST /threads_publish")
    print("   → Two-step process (draft then publish)")

    print("\n8. ACCOUNT REQUIREMENTS:")
    print("   • Instagram Business OR Creator account")
    print("   • Threads account linked to Instagram")
    print("   • Personal Instagram accounts NOT supported")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_threads_oauth()
