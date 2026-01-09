# NOiSEMaKER Naming Inventory

**Last Verified:** December 21, 2025 (via AWS CLI)

---

## AWS DynamoDB Tables (24)

All tables use `noisemaker-` prefix in region `us-east-2`.

| Table Name | Partition Key | Sort Key |
|------------|---------------|----------|
| noisemaker-album-artwork | artwork_id | — |
| noisemaker-artwork-analytics | artwork_id | date |
| noisemaker-artwork-cleanup | task_id | — |
| noisemaker-artwork-holds | artwork_id | — |
| noisemaker-auth | pk | sk |
| noisemaker-baselines | user_id | calculated_at |
| noisemaker-community-analytics | user_id | period |
| noisemaker-content-generation | song_id | content_id |
| noisemaker-content-tasks | task_id | — |
| noisemaker-discord-engagement | user_id | server_id_timestamp |
| noisemaker-discord-servers | server_id | — |
| noisemaker-engagement-history | user_id | platform_date |
| noisemaker-milestones | user_id | milestone_type |
| noisemaker-oauth-states | state | — |
| noisemaker-platform-connections | user_id | platform |
| noisemaker-posting-history | user_id | posted_at_post_id |
| noisemaker-reddit-engagement | user_id | subreddit_timestamp |
| noisemaker-scheduled-posts | user_id | scheduled_time_post_id |
| noisemaker-songs | user_id | song_id |
| noisemaker-system-alerts | alert_id | — |
| noisemaker-track-metrics | spotify_track_id | date |
| noisemaker-user-behavior | user_id | event_type_timestamp |
| noisemaker-user-credits | user_id | purchase_id |
| noisemaker-users | user_id | — |

---

## AWS S3 Buckets

### noisemakerpromobydoowopp (Main Bucket)

```
noisemakerpromobydoowopp/
├── ArtSellingONLY/
│   ├── mobile/
│   ├── original/
│   ├── sold-archive/
│   └── thumbnails/
├── Milestones/
│   ├── milestone_first_payment/
│   └── milestone_new_user_payment/
├── UserSpotifyArt/
├── content-colortemplates/
│   ├── blue/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── green/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── neutral/
│   │   ├── charcoal-black/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── off-white/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── orange/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── pink/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── purple/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   ├── red/
│   │   ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│   │   ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│   │   └── normal/{facebook,instagram,tiktok,twitter,youtube}/
│   └── yellow/
│       ├── dark/{facebook,instagram,tiktok,twitter,youtube}/
│       ├── light/{facebook,instagram,tiktok,twitter,youtube}/
│       └── normal/{facebook,instagram,tiktok,twitter,youtube}/
└── scheduled-content/
```

**Template Pattern:** `content-colortemplates/{color}/{shade}/{platform}/`
- **Colors (8):** blue, green, neutral, orange, pink, purple, red, yellow
- **Shades (3):** dark, light, normal (neutral uses: charcoal-black, off-white)
- **Platforms (5):** facebook, instagram, tiktok, twitter, youtube

### elasticbeanstalk-us-east-2-199689305330 (EB Bucket)

| Prefix | Purpose |
|--------|---------|
| .elasticbeanstalk/ | EB configuration |
| noisemaker-api/ | Application deployments |
| resources/ | Static resources |

---

## AWS Elastic Beanstalk

| Application | Environment | Stack |
|-------------|-------------|-------|
| noisemaker-api | noisemaker-api-prod | 64bit Amazon Linux 2023 v4.8.0 running Python 3.12 |

**Environment Details:**
- Environment ID: e-fr7dkavzhr
- CNAME: noisemaker-api-prod.eba-hepfiknp.us-east-2.elasticbeanstalk.com
- Status: Ready
- Health: Green

---

## AWS Amplify

| App Name | App ID | Branches |
|----------|--------|----------|
| noisemaker-frontend | dy72ta11223bp | main |

**App Details:**
- Repository: https://github.com/tretretretretre/Noi
- Default Domain: dy72ta11223bp.amplifyapp.com
- Platform: WEB_COMPUTE
- Framework: Next.js - SSR
- Monorepo App Root: frontend

---

## AWS Route 53

| Domain | Record | Type | Value |
|--------|--------|------|-------|
| doowopp.com | noisemaker.doowopp.com | A (Alias) | d14711qbyuxk1s.cloudfront.net |
| doowopp.com | api.noisemaker.doowopp.com | CNAME | noisemaker-api-prod.eba-hepfiknp.us-east-2.elasticbeanstalk.com |

**Hosted Zone:** Z0578313D3XA99Q8F7F0

---

## AWS Parameter Store (31)

All parameters use `/noisemaker/` prefix in region `us-east-2`.

| Parameter Name |
|----------------|
| /noisemaker/discord_webhook_url |
| /noisemaker/facebook_app_id |
| /noisemaker/facebook_app_secret |
| /noisemaker/facebook_client_id |
| /noisemaker/facebook_client_secret |
| /noisemaker/google_client_id |
| /noisemaker/google_client_secret |
| /noisemaker/grok_api_key |
| /noisemaker/huggingface_token |
| /noisemaker/jwt_secret_key |
| /noisemaker/nextauth_secret |
| /noisemaker/nextauth_url |
| /noisemaker/reddit_client_id |
| /noisemaker/reddit_client_secret |
| /noisemaker/spotify_client_id |
| /noisemaker/spotify_client_secret |
| /noisemaker/stripe_price_artwork_15pack |
| /noisemaker/stripe_price_artwork_5pack |
| /noisemaker/stripe_price_artwork_single |
| /noisemaker/stripe_price_legend |
| /noisemaker/stripe_price_star |
| /noisemaker/stripe_price_talent |
| /noisemaker/stripe_publishable_key |
| /noisemaker/stripe_secret_key |
| /noisemaker/stripe_webhook_secret |
| /noisemaker/threads_client_id |
| /noisemaker/threads_client_secret |
| /noisemaker/tiktok_client_id |
| /noisemaker/tiktok_client_secret |
| /noisemaker/youtube_client_id |
| /noisemaker/youtube_client_secret |

---

## FastAPI Backend Structure

### Folders

| Folder Path | Files |
|-------------|-------|
| backend/auth/ | __init__.py, environment_loader.py, user_auth.py |
| backend/community/ | __init__.py, community_integration.py, discord_engagement.py, reddit_engagement.py |
| backend/config/ | __init__.py, platform_config.py |
| backend/content/ | __init__.py, caption_generator.py, content_integration.py, content_orchestrator.py, image_processor.py, multi_platform_poster.py, template_manager.py |
| backend/data/ | __init__.py, dynamodb_client.py, platform_oauth_manager.py, song_manager.py, user_manager.py |
| backend/examples/ | oauth_integration_examples.py |
| backend/marketplace/ | __init__.py, album_artwork_manager.py, artwork_analytics.py, artwork_generator.py, artwork_integration.py, daily_album_art_generator.py |
| backend/middleware/ | __init__.py, auth.py |
| backend/models/ | __init__.py, schemas.py |
| backend/notifications/ | __init__.py, milestone_tracker.py |
| backend/routes/ | __init__.py, auth.py, dashboard.py, marketplace.py, payment.py, platforms.py, songs.py |
| backend/scheduler/ | __init__.py, cron_manager.py, daily_processor.py, posting_schedule.py, weekly_baseline_recalculator.py |
| backend/scripts/ | create_dynamodb_tables.py, create_oauth_tables.py, create_test_user.py |
| backend/spotify/ | __init__.py, baseline_calculator.py, fire_mode_analyzer.py, popularity_tracker.py, spotipy_client.py, track_analyzer.py |
| backend/tests/ | __init__.py, test_auth_and_payment.py, test_fire_mode_integration.py, test_marketplace_routes.py, test_phase_1_and_2.py |

### Root Files

| File |
|------|
| backend/__init__.py |
| backend/compare_3_folders.py |
| backend/main.py |

---

## API Endpoints

| Method | Path | Function | File |
|--------|------|----------|------|
| POST | /api/auth/signup | signup | routes/auth.py |
| POST | /api/auth/signin | signin | routes/auth.py |
| GET | /api/user/{user_id}/songs | get_user_songs | routes/dashboard.py |
| GET | /api/user/{user_id}/songs/{song_id}/upcoming-post | get_upcoming_post | routes/dashboard.py |
| GET | /api/user/{user_id}/stats | get_user_stats | routes/dashboard.py |
| PATCH | /api/posts/{post_id}/caption | update_post_caption | routes/dashboard.py |
| POST | /api/posts/{post_id}/approve | approve_post | routes/dashboard.py |
| POST | /api/posts/{post_id}/reject | reject_post | routes/dashboard.py |
| GET | /api/marketplace/artwork | get_marketplace_artwork | routes/marketplace.py |
| GET | /api/marketplace/credits | get_user_credits | routes/marketplace.py |
| POST | /api/marketplace/hold | place_artwork_hold | routes/marketplace.py |
| POST | /api/marketplace/download | download_free_artwork | routes/marketplace.py |
| POST | /api/marketplace/purchase | purchase_exclusive_artwork | routes/marketplace.py |
| GET | /api/marketplace/analytics | get_marketplace_analytics | routes/marketplace.py |
| GET | /api/marketplace/health | marketplace_health_check | routes/marketplace.py |
| POST | /api/payment/create-checkout | create_checkout_session | routes/payment.py |
| POST | /api/payment/confirm | confirm_payment | routes/payment.py |
| POST | /api/payment/webhooks/stripe | stripe_webhook | routes/payment.py |
| GET | /api/oauth/{platform}/connect | get_platform_auth_url | routes/platforms.py |
| POST | /api/oauth/{platform}/callback | handle_platform_callback | routes/platforms.py |
| GET | /api/oauth/{platform}/status | check_platform_status | routes/platforms.py |
| POST | /api/user/{user_id}/platforms | save_user_platforms | routes/platforms.py |
| GET | /api/user/{user_id}/platforms/status | get_platforms_status | routes/platforms.py |
| POST | /api/songs/add-from-url | add_song_from_url | routes/songs.py |
| GET | /api/songs/user/{user_id} | get_user_songs | routes/songs.py |

---

## Quick Reference Commands

```bash
# List DynamoDB tables
aws dynamodb list-tables --region us-east-2 --query 'TableNames[?starts_with(@, `noisemaker-`)]'

# List Parameter Store params
aws ssm describe-parameters --region us-east-2 --query "Parameters[?starts_with(Name, '/noisemaker/')].Name"

# List S3 bucket contents
aws s3 ls s3://noisemakerpromobydoowopp/ --recursive
```
