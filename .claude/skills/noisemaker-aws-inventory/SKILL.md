# NOiSEMaKER AWS Inventory Skill

## Description
Authoritative reference for all AWS resources used by NOiSEMaKER. Use this skill to ensure code references correct resource names, paths, and configurations.

## VERIFIED: December 21, 2025

---

## DynamoDB Tables (24 total)

All tables use `noisemaker-` prefix. Region: `us-east-2`

### Core Tables
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-users | user_id (S) | - |
| noisemaker-auth | pk (S) | sk (S) |
| noisemaker-songs | user_id (S) | song_id (S) |
| noisemaker-oauth-states | state (S) | - |
| noisemaker-platform-connections | user_id (S) | platform (S) |

### Content/Posting Tables
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-scheduled-posts | user_id (S) | scheduled_time#post_id (S) |
| noisemaker-posting-history | user_id (S) | posted_at#post_id (S) |
| noisemaker-content-generation | song_id (S) | content_id (S) |
| noisemaker-content-tasks | task_id (S) | - |

### Spotify Tracking Tables
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-baselines | user_id (S) | calculated_at (S) |
| noisemaker-track-metrics | spotify_track_id (S) | date (S) |

### Milestone Table
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-milestones | user_id (S) | milestone_type (S) |

### Marketplace Tables (Franks Garage)
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-album-artwork | artwork_id (S) | - |
| noisemaker-artwork-holds | artwork_id (S) | - |
| noisemaker-artwork-analytics | artwork_id (S) | date (S) |
| noisemaker-artwork-cleanup | task_id (S) | - |
| noisemaker-user-credits | user_id (S) | purchase_id (S) |

### Community Tables
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-discord-engagement | user_id (S) | server_id#timestamp (S) |
| noisemaker-discord-servers | server_id (S) | - |
| noisemaker-reddit-engagement | user_id (S) | subreddit#timestamp (S) |
| noisemaker-engagement-history | user_id (S) | platform#date (S) |
| noisemaker-community-analytics | user_id (S) | period (S) |

### System Tables
| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-system-alerts | alert_id (S) | - |
| noisemaker-user-behavior | user_id (S) | event_type#timestamp (S) |

---

## S3 Buckets (2 total)

### Main App Bucket: `noisemakerpromobydoowopp`

| Path | Purpose | Contents |
|------|---------|----------|
| `ArtSellingONLY/mobile/` | Mobile-sized marketplace artwork | 23 PNG files |
| `ArtSellingONLY/original/` | Full-resolution marketplace artwork | 16 PNG files |
| `ArtSellingONLY/sold-archive/` | Purchased artwork archive | Empty |
| `ArtSellingONLY/thumbnails/` | Thumbnail previews | 23 PNG files |
| `ArtSellingONLY/state.json` | Marketplace state | JSON file |
| `Milestones/milestone_first_payment/` | First payment video | milestone_first_payment.mov |
| `Milestones/milestone_new_user_payment/` | New user payment video | milestone_first_payment.mov |
| `UserSpotifyArt/` | User-uploaded Spotify art | Empty |
| `content-colortemplates/` | Post templates | 120 PNG files |
| `scheduled-content/` | Scheduled post content | Empty |

#### Content Templates Structure
```
content-colortemplates/{color}/{shade}/{platform}/template_{color}_{shade}_{platform}.png

Colors: blue, green, neutral, orange, pink, purple, red, yellow
Shades: dark, light, normal (neutral uses: charcoal-black, off-white)
Platforms: facebook, instagram, tiktok, twitter, youtube
```

### EB Deployment Bucket: `elasticbeanstalk-us-east-2-199689305330`
- Used by Elastic Beanstalk for deployments
- DO NOT modify manually

---

## Parameter Store (31 parameters)

All use `/noisemaker/` prefix. Region: `us-east-2`

### Authentication
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/jwt_secret_key | JWT signing |
| /noisemaker/nextauth_secret | NextAuth encryption |
| /noisemaker/nextauth_url | NextAuth callback URL |
| /noisemaker/google_client_id | Google OAuth |
| /noisemaker/google_client_secret | Google OAuth |

### Social Platform OAuth
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/facebook_app_id | Facebook App ID |
| /noisemaker/facebook_app_secret | Facebook App Secret |
| /noisemaker/facebook_client_id | Facebook OAuth |
| /noisemaker/facebook_client_secret | Facebook OAuth |
| /noisemaker/tiktok_client_id | TikTok OAuth |
| /noisemaker/tiktok_client_secret | TikTok OAuth |
| /noisemaker/youtube_client_id | YouTube OAuth |
| /noisemaker/youtube_client_secret | YouTube OAuth |
| /noisemaker/reddit_client_id | Reddit OAuth |
| /noisemaker/reddit_client_secret | Reddit OAuth |
| /noisemaker/threads_client_id | Threads OAuth |
| /noisemaker/threads_client_secret | Threads OAuth |
| /noisemaker/discord_webhook_url | Discord notifications |

### MISSING (need to add later)
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/instagram_client_id | Instagram OAuth |
| /noisemaker/instagram_client_secret | Instagram OAuth |
| /noisemaker/twitter_client_id | Twitter/X OAuth |
| /noisemaker/twitter_client_secret | Twitter/X OAuth |

### Spotify
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/spotify_client_id | Spotify API |
| /noisemaker/spotify_client_secret | Spotify API |

### Stripe Payments
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/stripe_publishable_key | Stripe public key |
| /noisemaker/stripe_secret_key | Stripe secret key |
| /noisemaker/stripe_webhook_secret | Stripe webhooks |
| /noisemaker/stripe_price_talent | Talent tier price ID |
| /noisemaker/stripe_price_star | Star tier price ID |
| /noisemaker/stripe_price_legend | Legend tier price ID |
| /noisemaker/stripe_price_artwork_single | Single artwork price |
| /noisemaker/stripe_price_artwork_5pack | 5-pack artwork price |
| /noisemaker/stripe_price_artwork_15pack | 15-pack artwork price |

### AI Services
| Parameter | Purpose |
|-----------|---------|
| /noisemaker/grok_api_key | Grok AI API |
| /noisemaker/huggingface_token | HuggingFace API |

---

## Elastic Beanstalk

| Property | Value |
|----------|-------|
| Application | noisemaker-api |
| Environment | noisemaker-api-prod |
| Environment ID | e-fr7dkavzhr |
| Platform | Python 3.12 on Amazon Linux 2023 |
| CNAME | noisemaker-api-prod.eba-hepfiknp.us-east-2.elasticbeanstalk.com |

---

## Amplify (Frontend)

| Property | Value |
|----------|-------|
| App Name | noisemaker-frontend |
| App ID | dy72ta11223bp |
| Repository | https://github.com/tretretretretre/Noi |
| Branch | main |
| Monorepo Root | frontend |
| Domain | dy72ta11223bp.amplifyapp.com |

---

## Route 53 / Domains

| Domain | Type | Target |
|--------|------|--------|
| noisemaker.doowopp.com | A (Alias) | CloudFront |
| api.noisemaker.doowopp.com | CNAME | EB prod environment |

---

## CRITICAL RULES

### NEVER reference these (OLD/WRONG):
- `spotify-promo-*` (any table or bucket name)
- `/spotify-promo/*` (any parameter path)
- `/users/tresch/*` (old personal parameters)

### ALWAYS use:
- `noisemaker-*` for DynamoDB tables
- `noisemakerpromobydoowopp` for S3 bucket
- `/noisemaker/*` for Parameter Store paths
