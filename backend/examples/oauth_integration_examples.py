"""
OAuth Integration Examples for Noisemaker SaaS
Demonstrates how to use the OAuth system in your application code.

CRITICAL: This is a SaaS application. All operations require user_id.
Users connect THEIR OWN social media accounts, not app-level accounts.

Author: Senior Python Backend Engineer
Version: 1.0
"""

from data.platform_oauth_manager import oauth_manager, get_platform_token, get_platform_connections
from content.multi_platform_poster import (
    PostContent,
    post_to_user_platforms,
    post_to_platform,
    post_to_all_platforms
)
from typing import Dict, Any


# ============================================================================
# EXAMPLE 1: Check if User Has Connected Platforms
# ============================================================================

def example_check_user_platforms(user_id: str) -> None:
    """
    Check which platforms a user has connected.

    Args:
        user_id: User identifier
    """
    print(f"📊 Checking platform connections for user {user_id}...\n")

    # Get all platform statuses
    connections = get_platform_connections(user_id)

    for platform, status in connections.items():
        if status.get('connected'):
            username = status.get('username', 'N/A')
            connected_at = status.get('connected_at', 'N/A')
            print(f"✅ {platform.title():15} - Connected as @{username} (since {connected_at[:10]})")
        else:
            print(f"❌ {platform.title():15} - Not connected")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 2: Get Platform Token (with Auto-Refresh)
# ============================================================================

def example_get_platform_token(user_id: str, platform: str) -> None:
    """
    Get user's OAuth token for a platform.
    Automatically refreshes if expired.

    Args:
        user_id: User identifier
        platform: Platform name (instagram, twitter, etc.)
    """
    print(f"🔑 Getting {platform} token for user {user_id}...\n")

    # Get token (auto-refreshes if expired)
    token_data = get_platform_token(user_id, platform)

    if token_data:
        print(f"✅ Token retrieved successfully!")
        print(f"   Platform Username: @{token_data.get('platform_username')}")
        print(f"   Account Type: {token_data.get('account_type')}")
        print(f"   Scopes: {', '.join(token_data.get('scopes', []))}")
        # Note: Don't print the actual token for security
    else:
        print(f"❌ User has not connected {platform}")
        print(f"   → Direct user to: /api/oauth/{platform}/connect")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 3: Post to User's Connected Platforms
# ============================================================================

def example_post_to_user_platforms(user_id: str) -> None:
    """
    Post content to all platforms the user has connected.

    This is the RECOMMENDED way to post - it automatically
    detects which platforms the user has connected.

    Args:
        user_id: User identifier
    """
    print(f"📤 Posting to all connected platforms for user {user_id}...\n")

    # Create post content
    content = PostContent(
        caption="🎵 Check out my new track! Fire emoji mode activated 🔥",
        image_path="/path/to/album_art.jpg",
        hashtags=["#NewMusic", "#IndieArtist", "#MusicPromotion"],
        streaming_links={
            'spotify': 'https://open.spotify.com/track/...',
            'apple_music': 'https://music.apple.com/...'
        },
        platform='all',  # Will be set per-platform automatically
        preview_url='https://p.scdn.co/mp3-preview/...'  # 30-second preview
    )

    # Post to all user's connected platforms
    results = post_to_user_platforms(user_id, content)

    # Show results
    if not results:
        print("⚠️  User has no platforms connected!")
        print("   → Direct user to: /platforms")
    else:
        for platform, result in results.items():
            if result.success:
                print(f"✅ {platform.title():15} - Posted successfully!")
                print(f"   Post ID: {result.post_id}")
                print(f"   Post URL: {result.post_url}")
            else:
                print(f"❌ {platform.title():15} - Failed")
                print(f"   Error: {result.error_message}")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 4: Post to Specific Platform
# ============================================================================

def example_post_to_specific_platform(user_id: str, platform: str) -> None:
    """
    Post to a specific platform only.

    Args:
        user_id: User identifier
        platform: Platform name
    """
    print(f"📤 Posting to {platform} for user {user_id}...\n")

    # Create content
    content = PostContent(
        caption="New music alert! 🎶",
        image_path="/path/to/image.jpg",
        hashtags=["#Music"],
        streaming_links={'spotify': 'https://open.spotify.com/track/...'},
        platform=platform
    )

    # Post to specific platform
    result = post_to_platform(user_id, content, platform)

    if result.success:
        print(f"✅ Posted to {platform} successfully!")
        print(f"   Post ID: {result.post_id}")
        print(f"   URL: {result.post_url}")
    else:
        print(f"❌ Failed to post to {platform}")
        print(f"   Error: {result.error_message}")

        # Check if user has connected the platform
        token_data = get_platform_token(user_id, platform)
        if not token_data:
            print(f"\n   → User needs to connect {platform}")
            print(f"   → URL: /api/oauth/{platform}/connect")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 5: Disconnect Platform
# ============================================================================

def example_disconnect_platform(user_id: str, platform: str) -> None:
    """
    Disconnect a user's platform connection.

    Args:
        user_id: User identifier
        platform: Platform to disconnect
    """
    print(f"🔌 Disconnecting {platform} for user {user_id}...\n")

    # Disconnect platform
    success = oauth_manager.revoke_connection(user_id, platform)

    if success:
        print(f"✅ Successfully disconnected {platform}")
    else:
        print(f"❌ Failed to disconnect {platform}")
        print(f"   (Platform may not have been connected)")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 6: Check Subscription Limits
# ============================================================================

def example_check_subscription_limits(user_id: str) -> None:
    """
    Check how many platforms a user can connect based on subscription.

    Args:
        user_id: User identifier
    """
    print(f"📊 Checking subscription limits for user {user_id}...\n")

    from data.user_manager import user_manager

    # Get subscription info
    subscription_info = user_manager.get_user_subscription_info(user_id)

    if not subscription_info:
        print("❌ User not found")
        return

    # Get platform selection
    platform_selection = user_manager.get_user_platform_selection(user_id)

    if platform_selection.get('success'):
        print(f"Subscription Tier: {subscription_info['subscription_tier'].upper()}")
        print(f"Platform Limit: {platform_selection['platform_limit']}")
        print(f"Platforms Connected: {platform_selection['platform_count']}")
        print(f"Remaining Slots: {platform_selection['remaining_slots']}")
        print(f"\nEnabled Platforms:")
        for platform in platform_selection['platforms_enabled']:
            print(f"  • {platform.title()}")

        # Check which are actually connected via OAuth
        print(f"\nOAuth Connection Status:")
        connections = get_platform_connections(user_id)
        for platform in platform_selection['platforms_enabled']:
            status = connections.get(platform, {})
            if status.get('connected'):
                print(f"  ✅ {platform.title()} - Connected")
            else:
                print(f"  ⚠️  {platform.title()} - Enabled but not connected")
                print(f"     → User needs to: /api/oauth/{platform}/connect")

    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 7: Handle OAuth Callback (Backend Integration)
# ============================================================================

def example_flask_integration():
    """
    Example Flask route integration for OAuth.

    This shows how to integrate OAuth routes into your Flask app.
    """
    code_example = '''
    from flask import Flask, session
    from api import oauth_bp

    app = Flask(__name__)
    app.secret_key = "your-secret-key"  # Use environment variable in production

    # Register OAuth blueprint
    app.register_blueprint(oauth_bp)

    # User needs to be logged in before connecting platforms
    @app.before_request
    def check_authentication():
        """Ensure user is authenticated for OAuth routes."""
        if request.path.startswith('/api/oauth'):
            if 'user_id' not in session:
                return redirect('/login')

    # Platform connections page
    @app.route('/platforms')
    def platforms_page():
        """Show platform connection management page."""
        user_id = session.get('user_id')

        # Get connection status
        connections = get_platform_connections(user_id)

        # Get subscription info
        from data.user_manager import user_manager
        platform_selection = user_manager.get_user_platform_selection(user_id)

        return render_template(
            'platforms.html',
            platforms=connections,
            platforms_limit=platform_selection.get('platform_limit', 3),
            platforms_connected=sum(1 for p in connections.values() if p.get('connected')),
            subscription_tier=platform_selection.get('subscription_tier', 'basic')
        )
    '''

    print("📝 Flask Integration Example:\n")
    print(code_example)
    print("\n" + "="*70 + "\n")


# ============================================================================
# EXAMPLE 8: Automated Daily Posting with OAuth
# ============================================================================

def example_daily_posting_workflow(user_id: str) -> None:
    """
    Example of how to integrate OAuth into daily posting workflow.

    This is how the scheduler would work with user OAuth tokens.

    Args:
        user_id: User identifier
    """
    print(f"📅 Daily posting workflow for user {user_id}...\n")

    # Step 1: Check if user has active subscription
    from data.user_manager import user_manager

    subscription_info = user_manager.get_user_subscription_info(user_id)

    if not subscription_info or subscription_info['account_status'] != 'active':
        print("❌ User account not active. Skipping posts.")
        return

    # Step 2: Get user's enabled platforms
    platform_selection = user_manager.get_user_platform_selection(user_id)
    enabled_platforms = platform_selection.get('platforms_enabled', [])

    if not enabled_platforms:
        print("⚠️  User has no platforms enabled.")
        return

    print(f"✓ User has {len(enabled_platforms)} platforms enabled")

    # Step 3: Check which platforms are actually connected via OAuth
    connections = get_platform_connections(user_id)
    connected_platforms = [
        p for p in enabled_platforms
        if connections.get(p, {}).get('connected')
    ]

    if not connected_platforms:
        print("❌ User has not connected any OAuth platforms!")
        print("   → Send notification to user to connect platforms")
        return

    print(f"✓ User has {len(connected_platforms)} platforms connected:")
    for p in connected_platforms:
        print(f"  • {p.title()}")

    # Step 4: Get song content
    # (In real implementation, this would come from song_manager)
    content = PostContent(
        caption="🎵 Daily promo post",
        image_path="/path/to/album_art.jpg",
        hashtags=["#Music"],
        streaming_links={'spotify': 'https://...'},
        platform='all'
    )

    # Step 5: Post to connected platforms only
    print(f"\n📤 Posting to {len(connected_platforms)} connected platforms...")
    results = post_to_user_platforms(user_id, content)

    # Step 6: Handle results
    success_count = sum(1 for r in results.values() if r.success)
    fail_count = len(results) - success_count

    print(f"\n✅ Posted successfully to {success_count} platforms")
    if fail_count > 0:
        print(f"❌ Failed on {fail_count} platforms:")
        for platform, result in results.items():
            if not result.success:
                print(f"   • {platform}: {result.error_message}")

    print("\n" + "="*70 + "\n")


# ============================================================================
# MAIN: Run All Examples
# ============================================================================

if __name__ == '__main__':
    # Test user
    test_user_id = "user123"

    print("\n" + "="*70)
    print(" " * 15 + "NOISEMAKER OAUTH INTEGRATION EXAMPLES")
    print("="*70 + "\n")

    # Run examples
    print("1️⃣  Checking User Platform Connections")
    print("-" * 70)
    example_check_user_platforms(test_user_id)

    print("2️⃣  Getting Platform Token")
    print("-" * 70)
    example_get_platform_token(test_user_id, 'instagram')

    print("3️⃣  Posting to User's Connected Platforms")
    print("-" * 70)
    # example_post_to_user_platforms(test_user_id)  # Commented - requires real tokens

    print("4️⃣  Posting to Specific Platform")
    print("-" * 70)
    # example_post_to_specific_platform(test_user_id, 'instagram')  # Commented - requires real tokens

    print("5️⃣  Disconnecting Platform")
    print("-" * 70)
    # example_disconnect_platform(test_user_id, 'instagram')  # Commented - destructive

    print("6️⃣  Checking Subscription Limits")
    print("-" * 70)
    example_check_subscription_limits(test_user_id)

    print("7️⃣  Flask Integration Example")
    print("-" * 70)
    example_flask_integration()

    print("8️⃣  Daily Posting Workflow")
    print("-" * 70)
    # example_daily_posting_workflow(test_user_id)  # Commented - requires real setup

    print("\n✅ Examples complete! Check the code above for integration patterns.\n")


# ============================================================================
# CRITICAL REMINDERS
# ============================================================================

"""
🚨 CRITICAL REMINDERS FOR DEVELOPERS:

1. ALWAYS pass user_id parameter
   ❌ Bad:  post_to_platform(content, 'instagram')
   ✅ Good: post_to_platform(user_id, content, 'instagram')

2. NEVER use app-level tokens for user actions
   ❌ Bad:  Get token from Parameter Store for posting
   ✅ Good: Get user token from oauth_manager

3. ALWAYS check if user has connected platform
   ❌ Bad:  Assume platform is connected
   ✅ Good: Use get_platform_token() to check first

4. TOKENS auto-refresh automatically
   ✅ Good: Just call get_user_token() - it handles refresh

5. HANDLE "not connected" gracefully
   ✅ Good: Show friendly message with connect link

6. SUBSCRIPTION limits are enforced
   ✅ Good: Check platform_limit before allowing connections

7. CSRF protection is built-in
   ✅ Good: OAuth manager handles state validation

8. TOKENS are encrypted at rest
   ✅ Good: oauth_manager encrypts before storing in DynamoDB

Remember: This is a SaaS application! Each user has their own tokens!
"""
