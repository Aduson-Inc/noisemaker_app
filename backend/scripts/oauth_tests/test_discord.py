#!/usr/bin/env python3
"""
Discord Bot Test Script
Tests Discord bot credentials and permissions

NOTE: Discord uses BOT model, not user OAuth for posting.
Users add the NOiSEMaKER bot to their server.

Run: python3 test_discord.py
"""

import os
import sys
import boto3
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


def test_discord_bot():
    """Test Discord bot credentials."""
    print("\n" + "="*60)
    print("DISCORD BOT TEST")
    print("="*60)

    print("\n⚠️  IMPORTANT: Discord uses BOT model, NOT user OAuth!")
    print("   Users add the NOiSEMaKER bot to their server.")
    print("   Bot posts announcements to designated channel.")

    # Required bot permissions
    REQUIRED_PERMISSIONS = {
        'Send Messages': 2048,
        'Embed Links': 16384,
        'Attach Files': 32768,
        'Read Message History': 65536
    }

    # Calculate total permissions integer
    total_permissions = sum(REQUIRED_PERMISSIONS.values())

    print("\n1. CHECKING SSM PARAMETERS...")

    bot_token = get_ssm_param('/noisemaker/discord_bot_token')
    client_id = get_ssm_param('/noisemaker/discord_client_id')

    if not bot_token:
        print("   [FAIL] /noisemaker/discord_bot_token NOT FOUND")
        print("   → Create bot at https://discord.com/developers/applications")
        print("   → Add bot to application")
        print("   → Copy bot token (reset if needed)")
        return False
    else:
        print(f"   [OK] Bot Token found: {bot_token[:10]}...{bot_token[-5:]}")

    if not client_id:
        print("   [WARN] /noisemaker/discord_client_id NOT FOUND")
        print("   → Needed for bot invite URL")
    else:
        print(f"   [OK] Client ID found: {client_id}")

    print("\n2. REQUIRED BOT PERMISSIONS:")
    for perm, value in REQUIRED_PERMISSIONS.items():
        print(f"   • {perm} ({value})")
    print(f"   → Total permissions integer: {total_permissions}")

    print("\n3. TESTING BOT TOKEN...")

    # Test bot token by fetching bot user info
    headers = {
        'Authorization': f'Bot {bot_token}'
    }

    try:
        response = requests.get(
            'https://discord.com/api/v10/users/@me',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            bot_info = response.json()
            print(f"   [OK] Bot authenticated successfully!")
            print(f"       Bot Username: {bot_info.get('username')}#{bot_info.get('discriminator', '0')}")
            print(f"       Bot ID: {bot_info.get('id')}")
        elif response.status_code == 401:
            print("   [FAIL] Invalid bot token!")
            print("   → Token may be expired or incorrect")
            print("   → Reset token in Discord Developer Portal")
            return False
        else:
            print(f"   [WARN] Unexpected response: {response.status_code}")
            print(f"   → {response.text}")

    except Exception as e:
        print(f"   [WARN] Could not verify token: {e}")

    print("\n4. BOT INVITE URL:")
    if client_id:
        invite_url = (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={client_id}"
            f"&scope=bot"
            f"&permissions={total_permissions}"
        )
        print(f"   {invite_url}")
    else:
        print("   → Need client_id to generate invite URL")

    print("\n5. VERIFICATION CHECKLIST:")
    print("   [ ] Discord application created?")
    print("   [ ] Bot added to application?")
    print("   [ ] Bot token stored in SSM?")
    print("   [ ] Bot has required permissions?")

    print("\n6. HOW IT WORKS FOR USERS:")
    print("   1. User clicks 'Connect Discord' in NOiSEMaKER")
    print("   2. User is redirected to bot invite URL")
    print("   3. User selects their server and adds bot")
    print("   4. User selects channel for announcements")
    print("   5. NOiSEMaKER posts to that channel as bot")

    print("\n" + "="*60)
    print("STATUS: Bot model - no user OAuth needed.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    test_discord_bot()
