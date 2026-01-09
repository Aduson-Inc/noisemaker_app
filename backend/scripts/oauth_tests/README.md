# NOiSEMaKER OAuth Test Scripts

Test OAuth credentials for all 8 social media platforms.

## Quick Start

```bash
cd backend/scripts/oauth_tests

# Test all platforms
python3 test_all_platforms.py

# Test individual platform
python3 test_instagram.py
python3 test_twitter.py
python3 test_facebook.py
python3 test_tiktok.py
python3 test_youtube.py
python3 test_reddit.py
python3 test_discord.py
python3 test_threads.py
```

## What These Scripts Do

1. **Check SSM Parameters** - Verify credentials exist in AWS Parameter Store
2. **Show Required Scopes** - List exact scopes needed for posting
3. **Generate Auth URL** - Create test authorization URL
4. **Show Verification Checklist** - Steps to verify platform setup

## SSM Parameter Names

| Platform | Parameters Needed |
|----------|-------------------|
| Instagram | `/noisemaker/instagram_client_id`, `/noisemaker/instagram_client_secret` |
| Twitter | `/noisemaker/twitter_client_id`, `/noisemaker/twitter_client_secret` |
| Facebook | `/noisemaker/facebook_client_id` (or use Instagram's) |
| TikTok | `/noisemaker/tiktok_client_id`, `/noisemaker/tiktok_client_secret` |
| YouTube | `/noisemaker/youtube_client_id`, `/noisemaker/youtube_client_secret` |
| Reddit | `/noisemaker/reddit_client_id`, `/noisemaker/reddit_client_secret` |
| Discord | `/noisemaker/discord_bot_token`, `/noisemaker/discord_client_id` |
| Threads | Uses Instagram's Meta App credentials |

## Platform Notes

### Meta Platforms (Instagram, Facebook, Threads)
- Use single Meta App for all three
- Requires App Review for publishing permissions
- Business/Creator Instagram accounts only

### Twitter/X
- Uses OAuth 2.0 with PKCE
- Tokens expire in 2 hours (use `offline.access` for refresh)
- App must have "Read and Write" permissions

### TikTok
- Requires Content Posting API approval
- Unaudited apps: 5 users/day, private posts only
- Must pass TikTok audit for public posting

### YouTube
- Community Posts NOT available via API
- Only video/Shorts uploads supported
- Requires Google OAuth consent screen verification

### Reddit
- Simple script/web app setup
- No formal app review
- 60 requests/minute rate limit

### Discord
- Uses BOT model (not user OAuth)
- Users add bot to their server
- Bot posts to designated channel

## Full Documentation

See `/docs/OAUTH_PERMISSIONS_GUIDE.md` for complete platform requirements.
