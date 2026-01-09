# NOiSEMaKER OAuth Permissions Guide

**Last Updated:** December 26, 2025

This document lists the exact OAuth scopes/permissions needed for each of the 8 platforms to post content on behalf of users.

---

## 1. Instagram (via Meta Graph API)

**Account Requirement:** Business or Creator account ONLY (Personal accounts not supported as of Dec 4, 2024)

### Required Scopes:
| Scope | Purpose |
|-------|---------|
| `instagram_basic` | Read user's profile info and media |
| `instagram_content_publish` | **CRITICAL** - Post photos, videos, carousels |
| `pages_show_list` | Find Facebook Page linked to Instagram |
| `business_management` | Additional access for business accounts |

### Notes:
- Short-lived tokens (1 hour) can be exchanged for long-lived tokens (60 days)
- Requires Meta App Review for `instagram_content_publish`
- Instagram Basic Display API was deprecated Dec 4, 2024

### Sources:
- [Instagram Graph API Guide 2025](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2025/)
- [How to Post to Instagram via API](https://getlate.dev/blog/api-to-post-to-instagram)

---

## 2. Twitter/X (API v2)

**Tier Requirement:** Free tier allows posting (limited), Basic tier recommended

### Required Scopes (OAuth 2.0):
| Scope | Purpose |
|-------|---------|
| `tweet.read` | Read tweets |
| `tweet.write` | **CRITICAL** - Post tweets |
| `users.read` | Read user profile |
| `offline.access` | Get refresh tokens (recommended) |
| `media.write` | Upload images/videos (if posting media) |

### App Permissions:
In Developer Portal → "User authentication settings" → Set to **"Read and Write"**

### Notes:
- OAuth 2.0 tokens expire after 2 hours unless `offline.access` is included
- For media uploads, OAuth 1.0a may still be required
- Consider requesting: `tweet.read tweet.write users.read offline.access`

### Sources:
- [X API v2 Authentication Mapping](https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping)
- [NextAuth Twitter OAuth Discussion](https://github.com/nextauthjs/next-auth/discussions/4251)

---

## 3. Facebook (Graph API)

**Account Type:** User accounts and Pages

### Required Permissions:
| Permission | Purpose |
|------------|---------|
| `pages_manage_posts` | **CRITICAL** - Create and manage Page posts |
| `pages_read_engagement` | Read Page engagement data |
| `pages_manage_engagement` | Manage comments, likes |
| `publish_video` | Post video content |
| `business_management` | Business account access |

### For Page Access Token:
1. Get user token with `manage_pages` permission
2. Call `/page-id?fields=name,access_token`
3. Exchange for long-lived page token

### Notes:
- Old `publish_stream` permission no longer exists
- Requires Meta App Review for posting permissions
- Personal profile posting is heavily restricted

### Sources:
- [Facebook OAuth Scopes Reference](https://oauth-scopes.netlify.app/facebook.html)
- [Facebook Graph API Changes - Auth0](https://auth0.com/docs/troubleshoot/product-lifecycle/past-migrations/facebook-graph-api-changes)

---

## 4. TikTok (Content Posting API)

**App Requirement:** Must pass TikTok audit for public posting

### Required Scopes:
| Scope | Purpose |
|-------|---------|
| `video.upload` | Upload videos (user must click to complete in TikTok app) |
| `video.publish` | **DIRECT POST** - Post directly without user interaction |

### Important Restrictions:
- **Unaudited apps:** Limited to 5 users/24hrs, private viewing only
- **Audited apps:** ~15 posts/day per creator account
- All content from unaudited clients = PRIVATE visibility

### Notes:
- Access tokens expire in 86400 seconds (24 hours)
- Must apply for and be approved for `video.publish` scope
- Each user must individually authorize your app

### Sources:
- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [TikTok Scopes Overview](https://developers.tiktok.com/doc/scopes-overview)

---

## 5. YouTube (Data API v3)

**Limitation:** Community Posts NOT supported via API

### Required Scopes:
| Scope | Purpose |
|-------|---------|
| `https://www.googleapis.com/auth/youtube.upload` | Upload videos/Shorts only |
| `https://www.googleapis.com/auth/youtube.force-ssl` | Full read/write access |
| `https://www.googleapis.com/auth/youtube` | Complete account management |

### Recommended Approach:
- For Shorts upload only: Use `youtube.upload` (minimal permissions)
- For full access: Use `youtube.force-ssl`

### Important Limitations:
- **Community Posts:** YouTube API does NOT support posting to Community tab
- Only video/Shorts uploads are available
- Requires Google Cloud Console project + OAuth consent screen verification

### Sources:
- [YouTube Data API OAuth](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps)
- [Upload a Video Guide](https://developers.google.com/youtube/v3/guides/uploading_a_video)

---

## 6. Reddit

**App Type:** Script app or Web app

### Required Scopes:
| Scope | Purpose |
|-------|---------|
| `identity` | Access username |
| `submit` | **CRITICAL** - Submit posts and links |
| `read` | Read subreddit content |

### Full Scope List:
`identity, edit, flair, history, modconfig, modflair, modlog, modposts, modwiki, mysubreddits, privatemessages, read, report, save, submit, subscribe, vote, wikiedit, wikiread`

### Notes:
- Access tokens expire after 1 hour
- Use refresh tokens for long-term access
- View all scopes at: https://www.reddit.com/api/v1/scopes

### Sources:
- [Reddit OAuth2 Wiki](https://github.com/reddit-archive/reddit/wiki/OAuth2)
- [PRAW OAuth Documentation](https://praw.readthedocs.io/en/v3.6.2/pages/oauth.html)

---

## 7. Discord

**Model:** BOT-based (not user OAuth for posting)

### Bot Scope:
| Scope | Purpose |
|-------|---------|
| `bot` | Add bot to server with permissions |
| `applications.commands` | Slash commands |

### Required Bot Permissions (Integer):
| Permission | Bit Value | Purpose |
|------------|-----------|---------|
| Send Messages | `2048` | Post in channels |
| Read Message History | `65536` | Read channel history |
| Embed Links | `16384` | Rich embeds |
| Attach Files | `32768` | Upload media |

### How It Works for NOiSEMaKER:
1. User adds NOiSEMaKER bot to their server
2. Bot posts announcements to designated channel
3. User does NOT OAuth their personal account

### Authorization URL Format:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=2048
```

### Notes:
- Discord does NOT support posting as a user via OAuth
- Must use bot approach - bot joins server and posts
- Calculate permissions at: https://giga.tools/discord/permission-calculator

### Sources:
- [Discord OAuth2 Documentation](https://discord.com/developers/docs/topics/oauth2)
- [Discord Bot Permissions 2025](https://friendify.net/blog/discord-bot-permissions-and-intents-explained-2025.html)

---

## 8. Threads (Meta API)

**Account Requirement:** Instagram Business/Creator account linked to Threads

### Required Scopes:
| Scope | Purpose |
|-------|---------|
| `threads_basic` | Read user profile and posts |
| `threads_content_publish` | **CRITICAL** - Post text, images, videos, carousels |

### Optional Additional Scopes:
| Scope | Purpose |
|-------|---------|
| `threads_read_replies` | Read replies |
| `threads_manage_replies` | Manage replies |
| `threads_manage_insights` | Analytics |

### Authorization URL:
```
https://threads.net/oauth/authorize?client_id=CLIENT_ID&redirect_uri=REDIRECT_URL&scope=threads_basic,threads_content_publish&response_type=code
```

### Notes:
- Uses same Meta App as Instagram/Facebook
- Must be approved by Meta for Threads API access
- Two-step posting: Create container → Publish

### Sources:
- [Threads API Guide](https://getlate.dev/blog/threads-api)
- [Threads Posting API](https://getlate.dev/blog/threads-posting-api)

---

## Summary Table

| Platform | Key Posting Scope | Token Expiry | Special Notes |
|----------|-------------------|--------------|---------------|
| Instagram | `instagram_content_publish` | 60 days (long-lived) | Business/Creator only |
| Twitter/X | `tweet.write` | 2 hours (use `offline.access`) | App must be Read+Write |
| Facebook | `pages_manage_posts` | 60 days (long-lived) | Page tokens only |
| TikTok | `video.publish` | 24 hours | Requires audit for public |
| YouTube | `youtube.upload` | Varies | NO community posts API |
| Reddit | `submit` | 1 hour | Use refresh tokens |
| Discord | Bot permissions | N/A | BOT model, not user OAuth |
| Threads | `threads_content_publish` | Long-lived | Meta review required |

---

## App Review Requirements

| Platform | Review Required? | Typical Timeline |
|----------|------------------|------------------|
| Instagram | Yes (Meta App Review) | 1-4 weeks |
| Twitter/X | Basic review | 1-3 days |
| Facebook | Yes (Meta App Review) | 1-4 weeks |
| TikTok | Yes (Content Audit) | 2-4 weeks |
| YouTube | Yes (OAuth consent verification) | 1-4 weeks |
| Reddit | No formal review | Instant |
| Discord | No formal review | Instant (bot verification at scale) |
| Threads | Yes (Meta App Review) | 1-4 weeks |

---

## Next Steps for NOiSEMaKER

1. **Meta Platforms (Instagram, Facebook, Threads):**
   - Single Meta App with all three platforms
   - Submit for App Review with use case justification

2. **Twitter/X:**
   - Ensure app has Read+Write permissions
   - Implement refresh token flow

3. **TikTok:**
   - Apply for Content Posting API access
   - Complete audit for public visibility

4. **YouTube:**
   - Set up OAuth consent screen
   - Note: Community posts NOT possible via API

5. **Reddit:**
   - Simple script app setup
   - No formal review needed

6. **Discord:**
   - Create bot application
   - Design channel selection UI for users
