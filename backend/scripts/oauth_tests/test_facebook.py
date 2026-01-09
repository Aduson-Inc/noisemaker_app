#!/usr/bin/env python3
"""
Facebook OAuth Test Script
Tests Meta/Facebook API credentials and permissions

Run: python3 test_facebook.py
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


def test_facebook_oauth():
    """Test Facebook/Meta OAuth credentials."""
    print("\n" + "="*60)
    print("FACEBOOK / META GRAPH API OAUTH TEST")
    print("="*60)

    # Required scopes for page posting
    REQUIRED_SCOPES = [
        'pages_manage_posts',      # Create/manage Page posts
        'pages_read_engagement',   # Read engagement data
        'pages_show_list',         # List user's Pages
        'publish_video'            # For video content (optional)
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    # Facebook uses same Meta App as Instagram
    client_id = get_ssm_param('/noisemaker/facebook_client_id')
    client_secret = get_ssm_param('/noisemaker/facebook_client_secret')

    # Fallback to instagram credentials (same Meta App)
    if not client_id:
        client_id = get_ssm_param('/noisemaker/instagram_client_id')
        if client_id:
            print("   [INFO] Using shared Meta App credentials from Instagram")

    if not client_id:
        print("   [FAIL] /noisemaker/facebook_client_id NOT FOUND")
        print("   → Use same Meta App as Instagram")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:10]}...")

    if not client_secret:
        client_secret = get_ssm_param('/noisemaker/instagram_client_secret')

    if not client_secret:
        print("   [FAIL] /noisemaker/facebook_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR PAGE POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/facebook"
    scopes = ','.join(REQUIRED_SCOPES)

    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
        f"&response_type=code"
    )

    print("\n4. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n5. VERIFICATION CHECKLIST:")
    print("   [ ] Meta App approved for pages_manage_posts?")
    print("   [ ] User has Facebook Page to post to?")
    print("   [ ] Redirect URI registered in Meta App?")
    print("   [ ] App in Live mode?")

    print("\n6. TOKEN FLOW:")
    print("   1. User authorizes → get auth code")
    print("   2. Exchange code for user token (short-lived)")
    print("   3. Exchange for long-lived token (60 days)")
    print("   4. Get Page token from user token")
    print("   5. Exchange Page token for long-lived Page token")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_facebook_oauth()
