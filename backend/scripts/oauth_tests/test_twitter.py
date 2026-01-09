#!/usr/bin/env python3
"""
Twitter/X OAuth Test Script
Tests X API v2 credentials and permissions

Run: python3 test_twitter.py
"""

import os
import sys
import boto3
import base64
import hashlib
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


def test_twitter_oauth():
    """Test Twitter/X OAuth 2.0 credentials."""
    print("\n" + "="*60)
    print("TWITTER / X API v2 OAUTH TEST")
    print("="*60)

    # Required scopes for posting
    REQUIRED_SCOPES = [
        'tweet.read',
        'tweet.write',
        'users.read',
        'offline.access'  # For refresh tokens
    ]

    print("\n1. CHECKING SSM PARAMETERS...")

    # Check for credentials
    client_id = get_ssm_param('/noisemaker/twitter_client_id')
    client_secret = get_ssm_param('/noisemaker/twitter_client_secret')

    if not client_id:
        print("   [FAIL] /noisemaker/twitter_client_id NOT FOUND")
        print("   → Create X App at https://developer.twitter.com/")
        print("   → Enable OAuth 2.0 in app settings")
        return False
    else:
        print(f"   [OK] Client ID found: {client_id[:10]}...")

    if not client_secret:
        print("   [FAIL] /noisemaker/twitter_client_secret NOT FOUND")
        return False
    else:
        print(f"   [OK] Client Secret found: {client_secret[:10]}...")

    print("\n2. REQUIRED SCOPES FOR POSTING:")
    for scope in REQUIRED_SCOPES:
        print(f"   • {scope}")

    print("\n3. GENERATING PKCE CHALLENGE...")

    # PKCE challenge for OAuth 2.0
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')

    print(f"   Code Verifier: {code_verifier[:20]}...")
    print(f"   Code Challenge: {code_challenge[:20]}...")

    print("\n4. GENERATING TEST AUTH URL...")

    redirect_uri = "https://noisemaker.doowopp.com/onboarding/platforms/callback/twitter"
    scopes = '%20'.join(REQUIRED_SCOPES)  # Space-separated, URL encoded
    state = secrets.token_urlsafe(16)

    auth_url = (
        f"https://twitter.com/i/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )

    print("\n5. TEST AUTH URL IN BROWSER:")
    print(f"   {auth_url}")

    print("\n6. VERIFICATION CHECKLIST:")
    print("   [ ] X Developer App approved?")
    print("   [ ] OAuth 2.0 enabled with 'Read and Write' permissions?")
    print("   [ ] Redirect URI registered in app settings?")
    print("   [ ] Free/Basic/Pro tier active?")

    print("\n7. IMPORTANT NOTES:")
    print("   • Tokens expire after 2 hours (use offline.access for refresh)")
    print("   • Media uploads may require OAuth 1.0a")
    print("   • Free tier: 1,500 tweets/month")

    print("\n" + "="*60)
    print("STATUS: Credentials found. Manual browser test required.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_twitter_oauth()
