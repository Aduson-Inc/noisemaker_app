# NOiSEMaKER FULL APPLICATION AUDIT
## ADUSON Inc. — Current State Document
**Audit Date:** 2026-02-25
**Auditor:** Claude Code (Opus 4.6)
**Commit:** 197459e (main branch, clean working tree)

---

# PHASE 1 — BACKEND FILE INVENTORY

## 1.1 Entry Point: `backend/main.py`

**FastAPI app** with these components:
- **Rate Limiter:** slowapi (by client IP)
- **CORS Origins:** `localhost:3000`, `localhost:3001`, `https://noisemaker.doowopp.com`
- **Exception Handlers:** 404, 500
- **Mounted Routers:**
  - `routes.auth` → `auth.router`
  - `routes.songs` → `songs.router`
  - `routes.platforms` → `platforms.get_routers()` (returns 2 routers)
  - `routes.dashboard` → `dashboard.get_routers()` (returns 2 routers)
  - `routes.payment` → `payment.router`
  - `routes.frank_art` → `frank_art.router`
- **Endpoints defined here:** `GET /` (status), `GET /health`

---

## 1.2 backend/auth/

### `auth/environment_loader.py` — ACTIVE
**Purpose:** Centralized AWS Parameter Store client with caching for all secrets.
- **Imports:** boto3 only
- **DynamoDB:** None
- **S3:** None
- **Parameter Store keys:** `/noisemaker/stripe_secret_key`, `/noisemaker/stripe_publishable_key`, `/noisemaker/stripe_webhook_secret`, `/noisemaker/stripe_price_talent`, `/noisemaker/stripe_price_star`, `/noisemaker/stripe_price_legend`, `/noisemaker/stripe_price_artwork_single`, `/noisemaker/stripe_price_artwork_5pack`, `/noisemaker/stripe_price_artwork_15pack`, `/noisemaker/{platform}_client_id`, `/noisemaker/{platform}_client_secret`, `/noisemaker/grok_api_key`, `/noisemaker/huggingface_token`, `/noisemaker/jwt_secret_key`, `/noisemaker/discord_webhook_url`
- **Endpoints:** None
- **External APIs:** AWS SSM (us-east-2)
- **JWT:** Retrieves JWT secret via `get_jwt_secret()`
- **Hardcoded:** Region `us-east-2`, base path `/noisemaker`
- **Legacy refs:** None

### `auth/user_auth.py` — ACTIVE
**Purpose:** User auth with PBKDF2-SHA256 hashing, session tokens, rate limiting (5 failed attempts), atomic email uniqueness via reservation table.
- **Imports:** boto3 (no other backend imports)
- **DynamoDB:** `noisemaker-users` (R/W, GSI: `email-index`), `noisemaker-email-reservations` (R/W)
- **S3:** None
- **Parameter Store:** None
- **Endpoints:** None (library module)
- **External APIs:** DynamoDB
- **JWT:** None (creates session tokens, NOT JWTs — separate from middleware/auth.py)
- **Hardcoded:** Session duration 86400s, max login attempts 5, PBKDF2 iterations 100000, salt 32 bytes
- **Legacy refs:** None
- **NOTE:** Session token system appears ORPHANED — frontend uses JWT from middleware/auth.py, not sessions

### `auth/__init__.py` — Empty

---

## 1.3 backend/middleware/

### `middleware/auth.py` — ACTIVE
**Purpose:** JWT token creation, validation, and FastAPI dependency injection for route protection.
- **Imports:** `auth.environment_loader.env_loader`
- **DynamoDB:** None
- **S3:** None
- **Parameter Store:** `/noisemaker/jwt_secret_key` (loaded at module import time)
- **Endpoints:** None (dependency module)
- **External APIs:** None
- **JWT:** Creates HS256 tokens (`create_jwt_token(user_id)`), validates (`verify_jwt_token(token)`), extracts user_id (`get_current_user_id()` FastAPI dependency), optional auth (`get_current_user_optional()`)
- **Hardcoded:** Algorithm `HS256`, expiration 24 hours
- **Legacy refs:** None

### `middleware/__init__.py` — Re-exports: `get_current_user`, `get_current_user_id`, `create_jwt_token`, `verify_jwt_token`

---

## 1.4 backend/config/

### `config/platform_config.py` — ACTIVE
**Purpose:** Dataclass definitions for 8 platform configurations with capabilities, content types, credential requirements.
- **Imports:** None
- **DynamoDB/S3/SSM/Endpoints/External/JWT:** None
- **Platforms defined:** Instagram (2200 chars, image), Twitter/X (280, image), Facebook (63206, image), YouTube (5000, video), TikTok (150, video), Reddit (40000, image), Discord (2000, embed), Threads (500, image)
- **Legacy refs:** None

### `config/__init__.py` — Re-exports: `SUPPORTED_PLATFORMS`, `ALL_PLATFORMS`, `get_platform_list`, `get_platform_config`, `get_recommended_platforms`, `validate_platform_selection`

---

## 1.5 backend/data/

### `data/dynamodb_client.py` — ACTIVE
**Purpose:** Core DynamoDB client with CRUD operations, retry logic (exponential backoff), float-to-Decimal conversion.
- **Imports:** boto3 only
- **DynamoDB:** Generic client for any table. Pre-initializes `noisemaker-users` and `noisemaker-songs` table references.
- **S3/SSM:** None
- **Endpoints:** None
- **Hardcoded:** max_retries=3, base_delay=1s, waiter Delay=5/MaxAttempts=20
- **Legacy refs:** "Spotify Promo Engine" in docstring (line 52)

### `data/user_manager.py` — ACTIVE
**Purpose:** Comprehensive user management (profiles, subscriptions, onboarding, milestones, art tokens). 1398 lines.
- **Imports:** `data.dynamodb_client.dynamodb_client`, boto3
- **DynamoDB:** `noisemaker-users` (primary, R/W — ALL user data stored here, NOT in separate profile/subscription/onboarding tables), `noisemaker-milestones` (R/W for milestone tracking)
- **S3:** `noisemakerpromobydoowopp` — milestone videos at `Milestones/milestone_{type}/milestone_{type}.MP4`
- **SSM:** None directly
- **Endpoints:** None
- **External APIs:** S3 presigned URL generation
- **JWT:** None
- **Hardcoded:** Tier definitions (talent=$25/2 platforms, star=$40/5, legend=$60/8), max_active_songs=3, S3 bucket name, art token amounts (signup=3, per_song=3, max=12), platform list
- **Legacy refs:** "Spotify Promo Engine" docstring; **M1 BUG: deprecated `stream_count` fields** (lines 105-107)

### `data/song_manager.py` — ACTIVE
**Purpose:** Song lifecycle management for 42-day promotion cycles with max 3 active songs per user.
- **Imports:** `data.dynamodb_client.dynamodb_client`
- **DynamoDB:** `noisemaker-songs` (R/W, PK: user_id, SK: song_id)
- **S3/SSM:** None
- **Endpoints:** None
- **Hardcoded:** max_active_songs=3, promotion_cycle_days=42, stage/day mapping (best→14d, second→28d, upcoming→0d)
- **Legacy refs:** **M1 BUG: deprecated `stream_count`, `previous_stream_count`, `average_daily_stream_count`** (lines 105-107)

### `data/platform_oauth_manager.py` — ACTIVE (thin shim)
**Purpose:** 11-line re-export shim for backward compatibility.
- **Imports:** `data.oauth.*` (all functions)
- **Everything else:** Delegated to oauth/ subpackage

### `data/oauth/__init__.py` — ACTIVE
**Purpose:** Factory/dispatcher routing to platform-specific OAuth handlers.
- **Imports:** All 8 platform classes + `TokenEncryption`
- **Registry:** Maps platform names to handler classes

### `data/oauth/base.py` — ACTIVE
**Purpose:** Base class for all OAuth handlers with state management, PKCE, token storage/refresh, SSM credential loading.
- **Imports:** `data.dynamodb_client.dynamodb_client`, `data.oauth.encryption.TokenEncryption`
- **DynamoDB:** `noisemaker-platform-connections` (encrypted OAuth tokens), `noisemaker-oauth-states` (CSRF state, 10-min expiry)
- **SSM:** `/noisemaker/{platform}_client_id`, `/noisemaker/{platform}_client_secret`
- **Hardcoded:** Region `us-east-2`, state expiry 10 min, token refresh check 5 min before expiry
- **Fixes applied:** H5 (state deletion timing), M8 (single try/except for SSM)

### `data/oauth/encryption.py` — ACTIVE
**Purpose:** Fernet symmetric encryption for OAuth tokens.
- **SSM:** `/noisemaker/oauth_encryption_key`
- **Hardcoded:** Region `us-east-2`

### `data/oauth/instagram.py` — ACTIVE
**Purpose:** Instagram OAuth via Meta Graph API with long-lived 60-day token exchange.
- **External API:** `https://api.instagram.com/oauth/authorize`, `https://graph.instagram.com/me`
- **SSM:** `/noisemaker/instagram_client_id`, `/noisemaker/instagram_client_secret`
- **Scopes:** `instagram_content_publish`, `instagram_basic`, `pages_read_engagement`

### `data/oauth/facebook.py` — ACTIVE
**Purpose:** Facebook OAuth via Meta Graph API v18.0.
- **External API:** `https://www.facebook.com/v18.0/dialog/oauth`, `https://graph.facebook.com/v18.0/oauth/access_token`
- **SSM:** `/noisemaker/facebook_client_id`, `/noisemaker/facebook_client_secret`
- **Scopes:** `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`
- **BUG:** API version `v18.0` hardcoded — should be parameterized

### `data/oauth/threads.py` — ACTIVE
**Purpose:** Threads OAuth via Meta Threads API with 60-day token exchange.
- **External API:** `https://threads.net/oauth/authorize`, `https://graph.threads.net/oauth/access_token`
- **SSM:** `/noisemaker/threads_client_id`, `/noisemaker/threads_client_secret`
- **Scopes:** `threads_basic`, `threads_content_publish`

### `data/oauth/tiktok.py` — ACTIVE
**Purpose:** TikTok OAuth v2 with `client_key` mapping and comma-separated scopes.
- **External API:** `https://www.tiktok.com/v2/auth/authorize`, `https://open.tiktokapis.com/v2/oauth/token/`
- **SSM:** `/noisemaker/tiktok_client_id` (→ client_key), `/noisemaker/tiktok_client_secret`
- **Scopes:** `video.upload`, `user.info.basic`

### `data/oauth/discord.py` — ACTIVE
**Purpose:** Discord webhook handler (NOT OAuth — users provide webhook URL directly).
- **Imports:** `data.dynamodb_client`, `data.oauth.base`
- **DynamoDB:** `noisemaker-platform-connections` (stores encrypted webhook URLs)
- **Hardcoded:** Webhook URL prefix validation `https://discord.com/api/webhooks/`, fake expiry 3650 days

### `data/oauth/twitter.py` — ACTIVE
**Purpose:** Twitter/X OAuth 2.0 with PKCE (S256). Code_verifier stored in state record.
- **Imports:** `data.oauth.base`, `data.dynamodb_client`
- **External API:** `https://twitter.com/i/oauth2/authorize`, `https://api.twitter.com/2/oauth2/token`, `https://api.twitter.com/2/users/me`
- **SSM:** `/noisemaker/twitter_client_id`, `/noisemaker/twitter_client_secret`
- **Scopes:** `tweet.write`, `tweet.read`, `users.read`, `offline.access`
- **Fix applied:** H5 (state deletion after code_verifier consumed)

### `data/oauth/youtube.py` — ACTIVE
**Purpose:** YouTube OAuth via Google OAuth 2.0 with `access_type=offline` + `prompt=consent` for refresh tokens.
- **External API:** `https://accounts.google.com/o/oauth2/v2/auth`, `https://oauth2.googleapis.com/token`, YouTube API v3
- **SSM:** `/noisemaker/youtube_client_id`, `/noisemaker/youtube_client_secret`

### `data/oauth/reddit.py` — ACTIVE
**Purpose:** Reddit OAuth with HTTP Basic Auth for token exchange and `duration=permanent` for refresh tokens.
- **External API:** `https://www.reddit.com/api/v1/authorize`, `https://www.reddit.com/api/v1/access_token`, `https://oauth.reddit.com/api/v1/me`
- **SSM:** `/noisemaker/reddit_client_id`, `/noisemaker/reddit_client_secret`
- **Scopes:** `submit`, `read`, `identity`

### `data/__init__.py` — Empty

---

## 1.6 backend/routes/

### `routes/auth.py` — ACTIVE
**Purpose:** User signup, signin, OAuth token exchange with smart redirect routing based on onboarding state.
- **Imports:** `models.schemas`, `middleware.auth` (create_jwt_token, get_current_user_id), `auth.user_auth.UserAuth`, `data.user_manager`, `data.platform_oauth_manager`, `data.song_manager`
- **DynamoDB:** `noisemaker-users` (via managers)
- **Endpoints:**
  - `POST /api/auth/signup` — PUBLIC, no JWT. Creates user, profile, onboarding, milestones, art tokens. Returns JWT + redirect_to
  - `POST /api/auth/signin` — PUBLIC, no JWT. Authenticates, determines redirect based on onboarding state
  - `POST /api/auth/exchange-token` — PUBLIC, no JWT. OAuth provider exchange (Google/Facebook)
- **JWT:** Creates tokens on signup/signin/exchange
- **Rate limiting:** None
- **Hardcoded:** Cookie max_age 604800 (7 days), SameSite 'lax'

### `routes/platforms.py` — ACTIVE
**Purpose:** OAuth connections for 8 platforms and user platform selection.
- **Imports:** `models.schemas`, `middleware.auth.get_current_user_id`, `data.platform_oauth_manager`, `data.user_manager`
- **DynamoDB:** `noisemaker-platform-connections` (via oauth_manager), `noisemaker-oauth-states` (via oauth_manager)
- **Endpoints:**
  - `GET /api/oauth/{platform}/connect?user_id=X` — **NO JWT** (takes user_id as query param)
  - `POST /api/oauth/{platform}/callback` — **NO JWT** (body: code, user_id, state)
  - `GET /api/oauth/{platform}/status?user_id=X` — **NO JWT** (takes user_id as query param)
  - `POST /api/user/{user_id}/platforms` — JWT required
  - `GET /api/user/{user_id}/platforms/status` — JWT required
- **BUG M9:** First 3 endpoints have NO JWT auth — accept user_id as parameter, enabling impersonation
- **Rate limiting:** None

### `routes/dashboard.py` — ACTIVE
**Purpose:** Dashboard data (songs, posts, stats, milestones) and post management.
- **Imports:** `models.schemas`, `middleware.auth.get_current_user_id`, `data.song_manager`, `data.user_manager`, `data.dynamodb_client`
- **DynamoDB:** `noisemaker-songs`, `noisemaker-scheduled-posts` (direct), `noisemaker-users`, `noisemaker-milestones` (via managers)
- **Endpoints (ALL require JWT):**
  - `GET /api/user/{user_id}/songs`
  - `GET /api/user/{user_id}/songs/{song_id}/upcoming-post`
  - `GET /api/user/{user_id}/stats`
  - `GET /api/user/{user_id}/milestones`
  - `POST /api/user/{user_id}/milestones/{milestone_id}/claim`
  - `PATCH /api/posts/{post_id}/caption`
  - `POST /api/posts/{post_id}/approve`
  - `POST /api/posts/{post_id}/reject`
- **Rate limiting:** None

### `routes/payment.py` — ACTIVE
**Purpose:** Stripe payments for subscription tiers with webhook processing.
- **Imports:** `models.schemas`, `middleware.auth`, `data.user_manager`, `auth.environment_loader`, `spotify.baseline_calculator`
- **DynamoDB:** `noisemaker-users` (via user_manager)
- **SSM:** Stripe keys via env_loader (`stripe_secret_key`, `stripe_price_talent/star/legend`, `stripe_webhook_secret`)
- **Endpoints:**
  - `POST /api/payment/create-checkout` — JWT required. Creates Stripe checkout session
  - `POST /api/payment/confirm` — NO JWT (validates via Stripe session metadata). Confirms payment, returns new JWT
  - `POST /api/payment/webhooks/stripe` — NO JWT (webhook signature verification)
- **External APIs:** Stripe Checkout/Subscription/Webhook, Spotify (baseline calculation)
- **BUG M6:** Duplicate payment logic — confirm endpoint AND webhook both update subscription/milestone/onboarding. Could cause double updates
- **Rate limiting:** None

### `routes/frank_art.py` — ACTIVE
**Purpose:** Frank's Garage AI art marketplace API.
- **Imports:** `marketplace.frank_art_manager`, `marketplace.frank_art_integration`
- **DynamoDB:** `noisemaker-frank-art`, `noisemaker-artwork-holds`, `noisemaker-frank-art-purchases`, `noisemaker-artwork-analytics` (via managers)
- **S3:** `noisemakerpromobydoowopp/ArtSellingONLY/*`
- **Endpoints (ALL PUBLIC — NO JWT):**
  - `GET /api/frank-art/artwork?filter=X&user_id=X`
  - `GET /api/frank-art/tokens?user_id=X`
  - `POST /api/frank-art/hold` (body: user_id, artwork_id)
  - `POST /api/frank-art/download` (body: user_id, artwork_id)
  - `POST /api/frank-art/purchase` (body: user_id, artwork_ids, purchase_type)
  - `GET /api/frank-art/analytics` (admin)
  - `GET /api/frank-art/health`
- **SECURITY ISSUE:** All endpoints accept user_id as parameter with NO JWT verification
- **Rate limiting:** None

### `routes/songs.py` — ACTIVE
**Purpose:** Song management — adding from Spotify URLs, validation, 42-day promotion cycle.
- **Imports:** `spotify.spotipy_client`, `data.song_manager`, `data.user_manager`, `auth.environment_loader`, `middleware.auth`
- **DynamoDB:** `noisemaker-songs`, `noisemaker-users` (via managers)
- **SSM:** `/noisemaker/spotify_client_id`, `/noisemaker/spotify_client_secret`
- **Endpoints:**
  - `POST /api/songs/validate-artist` — PUBLIC, **rate limited (10/min)**. Validates Spotify artist URL
  - `POST /api/songs/validate-track` — JWT required
  - `POST /api/songs/add-from-url` — JWT required (body: spotify_url, initial_days, release_date)
  - `GET /api/songs/user/{user_id}` — JWT required
- **External APIs:** Spotify Web API
- **Hardcoded:** initial_days validates [0, 14, 28], 3-song limit, art token reward 3/song max 12

### `routes/__init__.py` — Empty

---

## 1.7 backend/spotify/

### `spotify/spotipy_client.py` — ACTIVE
**Purpose:** Production Spotify API client with caching (1hr TTL), rate limiting (90/min, 900/hr), thread-safe credential management, retry logic.
- **Imports:** None (self-contained, uses Spotipy library)
- **DynamoDB/S3/SSM:** None (credentials passed as params)
- **External APIs:** Spotify Web API (tracks, artists, search)
- **Hardcoded:** Cache TTL 3600s, max retries 3, rate limits 90/min + 900/hr

### `spotify/baseline_calculator.py` — ACTIVE
**Purpose:** Calculates user baseline popularity from 5 most recent Spotify tracks. Determines tier (1-4). Stores baseline history with 90-day TTL.
- **Imports:** `auth.environment_loader.get_platform_credentials`, `data.dynamodb_client`, `data.user_manager`
- **DynamoDB:** `noisemaker-baselines` (R/W), `noisemaker-users` (updates baseline/tier via user_manager)
- **SSM:** Spotify credentials via `get_platform_credentials('spotify')`
- **External APIs:** Spotify API (artist profile, albums, tracks)
- **Hardcoded:** Spotify API base URL, baselines table name, default baseline 0, TTL 90 days, tier brackets (0-10=T1, 11-20=T2, 21-30=T3, 30+=T4)
- **BUG:** Uses FLOOR rounding (`int(raw_average)`) but spec says "ceiling"

### `spotify/fire_mode_analyzer.py` — ACTIVE
**Purpose:** Fire Mode eligibility/maintenance/exit detection. 5-day guaranteed window, 2-day exit rule, 4 informational levels.
- **Imports:** None (pure logic, no I/O)
- **DynamoDB/S3/SSM:** None
- **Hardcoded:** Guaranteed days 5, consecutive exit days 2, level brackets (Rising 0-3, Building 4-10, Established 11-25, Breaking Out 26+)

### `spotify/popularity_tracker.py` — ACTIVE
**Purpose:** Daily Spotify track popularity polling, stores snapshots in DynamoDB, maintains 30-day history on song records.
- **Imports:** `auth.environment_loader.get_platform_credentials`, `spotify.baseline_calculator`, `data.dynamodb_client`, `data.song_manager`
- **DynamoDB:** `noisemaker-track-metrics` (R/W, daily snapshots, TTL 365 days), `noisemaker-songs` (updates popularity/history via song_manager)
- **SSM:** Spotify credentials
- **External APIs:** Spotify API (track popularity)
- **Hardcoded:** Spotify API base URL, metrics table name, history retention 30 days, TTL 365 days

### `spotify/__init__.py` — Re-exports: `SpotifyClientManager`, `spotify_manager`, `get_track_information`, `get_artist_genre_info`

---

## 1.8 backend/scheduler/

### `scheduler/daily_orchestrator.py` — ACTIVE (CRITICAL Lambda)
**Purpose:** Lambda entry point running every 30 minutes via EventBridge. For each paying user at 9 PM local time, determines tomorrow's posts, generates content, schedules posts with randomized times.
- **Imports:** `scheduler.schedule_engine`, `content.content_generator`, `scheduler.posting_schedule`
- **DynamoDB:** `noisemaker-users` (scan, update schedule_day), `noisemaker-songs` (read active, update promotion status), `noisemaker-platform-connections` (read), `noisemaker-scheduled-posts` (write)
- **Hardcoded:** TRIGGER_HOUR=21, MAX_PROMO_DAYS=42, EXTENDED_POST_INTERVAL_DAYS=3, default timezone America/New_York

### `scheduler/post_dispatcher.py` — ACTIVE (CRITICAL Lambda)
**Purpose:** Lambda entry point running hourly. Queries pending posts, loads content, downloads images, posts to platforms, updates status.
- **Imports:** `content.multi_platform_poster`
- **DynamoDB:** `noisemaker-scheduled-posts` (read pending, update status), `noisemaker-content` (read, update posted_to), `noisemaker-posting-history` (write)
- **S3:** `noisemakerpromobydoowopp` (read content images)
- **Hardcoded:** S3 bucket, max retries 2

### `scheduler/daily_processor.py` — ACTIVE
**Purpose:** Orchestrates daily workflow per user — retrieves songs from Spotify, analyzes performance (Fire Mode), calculates daily posts, checks milestones.
- **Imports:** `auth.environment_loader`, `spotify.spotipy_client`, `spotify.track_analyzer` (**BROKEN — file missing**), `spotify.baseline_calculator`, `spotify.popularity_tracker`, `spotify.fire_mode_analyzer`, `data.song_manager`, `data.user_manager`, `notifications.milestone_tracker`, `scheduler.posting_schedule`
- **DynamoDB:** `noisemaker-songs`, `noisemaker-users` (via managers)
- **External APIs:** Spotify API
- **BROKEN IMPORT:** `spotify.track_analyzer` does NOT exist

### `scheduler/schedule_engine.py` — ACTIVE
**Purpose:** Pure scheduling logic — determines which (song, platform) pairs to post per day. 3 modes: 1-song, 2-song alternation, 3-song grid.
- **Imports:** `backend.scheduler.schedule_grids` (**IMPORT BUG** — uses full path instead of relative)
- **DynamoDB/S3/SSM:** None

### `scheduler/schedule_grids.py` — ACTIVE
**Purpose:** Pure data — 14-day posting schedule grids for 3-song mode across 2-8 platforms.
- No imports, no I/O

### `scheduler/posting_schedule.py` — ACTIVE
**Purpose:** Optimal posting time windows for each platform (4 random times per platform for anti-detection).
- No imports, no I/O
- **Hardcoded:** Per-platform posting times (e.g., Instagram 09:00/13:00/17:00/20:00)

### `scheduler/cron_manager.py` — LIKELY ORPHANED
**Purpose:** Per-user cron job generation (legacy approach replaced by daily_orchestrator Lambda).
- **Hardcoded:** Python paths, script paths for Linux deployment
- Not imported anywhere

### `scheduler/monthly_baseline_recalculator.py` — ORPHANED (no trigger)
**Purpose:** Recalculates baselines for all active users monthly.
- **Imports:** `spotify.baseline_calculator`, `data.user_manager.UserManager`
- **DynamoDB:** `noisemaker-baselines`, `noisemaker-users` (via managers)
- Has `main()` entry point but NO Lambda handler, NO EventBridge trigger, NOT imported by any route
- **ISSUE:** No scheduling mechanism — needs Lambda/EventBridge setup

### `scheduler/__init__.py` — Empty

---

## 1.9 backend/content/

### `content/caption_generator.py` — ACTIVE
**Purpose:** AI-powered caption generation using Grok AI with genre-appropriate, minimalist text.
- **Imports:** None
- **SSM:** `/noisemaker/grok_api_key`, `/noisemaker/grok_api_url` (default fallback to `https://api.grok.ai/v1/chat/completions`)
- **External APIs:** Grok AI (`/v1/chat/completions`)

### `content/content_generator.py` — ACTIVE
**Purpose:** Generates platform-specific promo images compositing HuggingFace backgrounds with Spotify artwork.
- **Imports:** `content.caption_generator.generate_caption`
- **DynamoDB:** `noisemaker-content` (write), `noisemaker-songs` (read/write color_palette, cached_artwork)
- **S3:** `noisemakerpromobydoowopp` — reads `artwork/{song_id}.jpg`, writes `content/{user_id}/{content_id}.jpg`
- **SSM:** `/noisemaker/huggingface_token`
- **External APIs:** HuggingFace InferenceClient (FLUX.1-schnell model), Spotify (artwork download)
- **Hardcoded:** S3 bucket, HuggingFace model name, platform image dimensions

### `content/content_orchestrator.py` — ACTIVE but PROBLEMATIC
**Purpose:** Main orchestrator for image processing, caption generation, multi-platform posting.
- **Imports:** `content.image_processor`, `content.template_manager`, `content.caption_generator`, `content.multi_platform_poster`, `spotify.spotify_client` (**BROKEN — file missing**), `data.promo_data_manager` (**BROKEN — file missing**)
- **DynamoDB:** `noisemaker-content-generation`
- **S3:** `spotify-promo-generated-content` — **LEGACY BUCKET NAME**
- **BUGS:** Duplicate code block (lines 1-136 appear twice); 2 broken imports; legacy S3 bucket name

### `content/content_integration.py` — ORPHANED
**Purpose:** Bridge between Stage A (promotion) and Stage B (content generation).
- **ALL 4 imports are BROKEN:** `scheduler.promotion_scheduler`, `data.promo_data_manager`, `spotify.spotify_client`, `notifications.notification_manager` — NONE of these files exist
- **DynamoDB:** `noisemaker-content-tasks`
- Not called by any other file

### `content/image_processor.py` — ACTIVE
**Purpose:** Color analysis of album artwork and promo image composition.
- No backend imports
- **Hardcoded:** Font path `/content/fonts/Arial.ttf` (may not exist in Lambda)

### `content/multi_platform_poster.py` — ACTIVE
**Purpose:** Posts to all 8 platforms via their APIs.
- **Imports:** `data.platform_oauth_manager.oauth_manager`
- **DynamoDB:** `noisemaker-posting-history` (write), reads platform tokens via oauth_manager
- **External APIs:** Instagram Graph, Twitter v2, Facebook Graph, YouTube, TikTok, Reddit, Discord webhooks, Threads

### `content/template_manager.py` — ACTIVE but LEGACY
**Purpose:** Manages promo card templates in S3 with color-based selection and 3-day rotation.
- **S3:** `spotify-promo-templates` — **LEGACY BUCKET NAME** (should be `noisemakerpromobydoowopp` or parameterized)
- **Hardcoded:** S3 bucket, color families, rotation pattern

### `content/__init__.py` — Docstring only

---

## 1.10 backend/marketplace/

### `marketplace/frank_art_manager.py` — ACTIVE
**Purpose:** 250-image art pool management — queries, holds (5-min), free downloads (1 token), paid purchases ($2.99-$19.99).
- **Imports:** `data.user_manager`
- **DynamoDB:** `noisemaker-frank-art` (R/W), `noisemaker-artwork-holds` (R/W), `noisemaker-frank-art-purchases` (W), `noisemaker-artwork-analytics` (W)
- **S3:** `noisemakerpromobydoowopp/ArtSellingONLY/original|mobile|thumbnails/`, `users/{user_id}/purchased-art/`, `sold-archive/sold-thumbnails/`
- **External APIs:** Stripe PaymentIntent
- **BUG M7:** Stripe price IDs hardcoded: `price_1SbCJRHIG2GktxbO3sR6LDGs`, `price_1SbCJbHIG2GktxbOxbAlLbLK`, `price_1SbCJwHIG2GktxbOQQaXWhVm`

### `marketplace/frank_art_generator.py` — ACTIVE (Lambda)
**Purpose:** Lambda function triggered daily at 9 PM UTC by EventBridge. Generates 4 FLUX.1-schnell artworks per run using rotating lists (7 art styles, 11 artist styles, 58 color combos).
- **DynamoDB:** `noisemaker-frank-art` (W)
- **S3:** `noisemakerpromobydoowopp/ArtSellingONLY/original|mobile|thumbnails/`, `ArtSellingONLY/state.json` (rotation state)
- **SSM:** `/noisemaker/huggingface_token`
- **External APIs:** HuggingFace InferenceClient (FLUX.1-schnell)
- **Lambda handler:** `lambda_handler(event, context)` — SAM template in `backend/template.yaml`

### `marketplace/frank_art_integration.py` — ACTIVE
**Purpose:** Bridges marketplace to user system. Awards signup tokens (3), song upload tokens (3/song, max 12).
- **Imports:** `marketplace.frank_art_manager`, `marketplace.artwork_analytics`, `data.user_manager`

### `marketplace/frank_art_cleanup.py` — ACTIVE (Lambda)
**Purpose:** Weekly cleanup (EventBridge Mondays). Marks purchased art >3 days as cleaned, recycles unpurchased to `content-colortemplates/{color}/{shade}/`.
- **DynamoDB:** `noisemaker-frank-art` (R/W)
- **S3:** `noisemakerpromobydoowopp/ArtSellingONLY/*`, `content-colortemplates/{color}/{shade}/`
- **Hardcoded:** CLEANUP_DAYS=3, MAX_POOL_SIZE=250

### `marketplace/artwork_analytics.py` — ACTIVE
**Purpose:** Analytics tracking for downloads/purchases and pool monitoring.
- **DynamoDB:** `noisemaker-frank-art` (R/W), `noisemaker-user-behavior` (W)
- **Hardcoded:** CRITICAL_POOL_THRESHOLD=50, MAX_POOL_SIZE=250

### `marketplace/__init__.py` — Empty

---

## 1.11 backend/models/

### `models/schemas.py` — ACTIVE
**Purpose:** Pydantic models for all API request/response validation.
**Key models:**
- **Auth:** SignUpRequest, SignInRequest, AuthResponse, AuthResponseEnhanced, MilestoneCheckResponse, ExchangeTokenRequest/Response
- **OAuth:** OAuthResponse, OAuthCallbackRequest, OAuthCallbackResponse, OAuthStatusResponse
- **Platforms:** PlatformSelectionRequest, PlatformConnectionStatus
- **Songs:** SongInfo, AddSongRequest, AddSongResponse, ValidateArtistRequest, ValidateTrackRequest, AddSongFromUrlRequest
- **Posts:** PostInfo, UpdateCaptionRequest, PostActionResponse
- **Dashboard:** DashboardStats, DashboardResponse, UserStatsResponse, PlatformStats
- **Payment:** CreateCheckoutRequest, PaymentCheckoutResponse, PaymentConfirmRequest, PaymentConfirmResponse
- **Users:** UserProfile, UserPreferences
- **Errors:** ErrorResponse, SuccessResponse

### `models/__init__.py` — Re-exports all schemas

---

## 1.12 backend/notifications/

### `notifications/milestone_tracker.py` — ACTIVE
**Purpose:** Milestone detection (checks metrics against thresholds). Does NOT record — delegates to user_manager.
- **Hardcoded thresholds:**
  - Followers: [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000, 25000, 50000, 100000]
  - Song Popularity: [5, 10, 15, 20, 25, 30]
  - Fire Mode Counts: [1, 3, 10]
  - Post Counts: [100, 500, 1000]
  - Longevity Days: [90, 180, 365]

### `notifications/__init__.py` — Empty

---

## 1.13 backend/scripts/

### `scripts/create_dynamodb_tables.py` — ACTIVE (one-time setup)
**Purpose:** Creates all 21 DynamoDB tables. See Phase 6 for full schema.

### `scripts/create_test_user.py` — ACTIVE (dev tool)
**Purpose:** Creates hardcoded test user (treschmusic@gmail.com / noise1Scotian, tier: legend)

### `scripts/create_oauth_tables.py` — ACTIVE (one-time setup)
**Purpose:** Creates `noisemaker-oauth-states` and `noisemaker-platform-connections`

### `scripts/add_email_gsi.py` — ACTIVE (one-time setup)
**Purpose:** Adds `email-index` GSI to `noisemaker-users`

### `scripts/oauth_tests/` — 9 test files for platform OAuth testing

---

## 1.14 backend/examples/

### `examples/oauth_integration_examples.py` — DOCUMENTATION
**Purpose:** 8 code examples showing how to use the OAuth system.

---

## 1.15 backend/tests/

### `tests/test_auth_and_payment.py` — TEST (partial coverage: signup, signin)
### `tests/test_phase_1_and_2.py` — TEST (song staging logic)
### `tests/test_marketplace_routes.py` — TEST (marketplace endpoints)
### `tests/test_fire_mode_integration.py` — TEST (Fire Mode detection)

---

## 1.16 Standalone Files

### `backend/scan_user.py` — DEV TOOL (ORPHANED)
**Purpose:** Debug script that scans all noisemaker-* tables for a hardcoded user_id.
- **Hardcoded:** user_id `NjEtnuD9dx5ywxLWwmVOqw`

---

# PHASE 2 — FRONTEND INVENTORY

## 2.1 Pages and Routes

| URL Path | File | Auth | Description |
|----------|------|------|-------------|
| `/` | `page.tsx` → `page-genz.tsx` | Public | Landing page (Gen Z Bold design) |
| `/pricing` | `pricing/page.tsx` → `pricing-v2.tsx` | Public | Pricing + embedded signup form |
| `/auth/signin` | `auth/signin/page.tsx` | Public | Sign-in for returning users |
| `/payment/success` | `payment/success/page.tsx` | Public | Payment confirmation + countdown redirect |
| `/milestone/[type]` | `milestone/[type]/page.tsx` | **Protected** | Celebration video page |
| `/onboarding/how-it-works` | `onboarding/how-it-works/page.tsx` | **Protected** | Onboarding info (LOREM IPSUM placeholder) |
| `/onboarding/how-it-works-2` | `onboarding/how-it-works-2/page.tsx` | **Protected** | Onboarding info (LOREM IPSUM placeholder) |
| `/onboarding/platforms` | `onboarding/platforms/page.tsx` → `platforms-v1-bands.tsx` | **Protected** | Platform OAuth connections |
| `/onboarding/platforms/callback/[platform]` | `callback/[platform]/page.tsx` | **Protected** | OAuth callback handler |
| `/onboarding/add-songs` | `onboarding/add-songs/page.tsx` | **Protected** | Song upload (1-3 Spotify tracks) |
| `/dashboard` | `dashboard/page.tsx` | **Protected** | Main dashboard hub |
| `/dashboard/garage` | `dashboard/garage/page.tsx` | **Protected** | Frank's Garage AI art marketplace |
| `/test-designs/aurora` | `test-designs/aurora/page.tsx` → `landing-aurora.tsx` | Public | Test landing variant |
| `/test-designs/monolith` | `test-designs/monolith/page.tsx` → `landing-monolith.tsx` | Public | Test landing variant |
| `/test-designs/noir-luxe` | `test-designs/noir-luxe/page.tsx` → `landing-noir-luxe.tsx` | Public | Test landing variant |

## 2.2 API Client (`frontend/src/lib/api.ts`)

**Base URL:** `NEXT_PUBLIC_API_URL` (default: `https://api.noisemaker.doowopp.com`)
**Auth:** Axios interceptor adds `Authorization: Bearer {token}` from localStorage

| Category | Function | Endpoint |
|----------|----------|----------|
| Auth | `signUp(email, password, name, tier, spotifyData?)` | `POST /api/auth/signup` |
| Auth | `signIn(email, password)` | `POST /api/auth/signin` |
| Auth | `checkMilestones(userId)` | `GET /api/user/{userId}/milestones` |
| Auth | `claimMilestone(userId, milestoneId)` | `POST /api/user/{userId}/milestones/{milestoneId}/claim` |
| Spotify | `validateArtist(url)` | `POST /api/songs/validate-artist` |
| Songs | `validateTrack(spotifyUrl)` | `POST /api/songs/validate-track` |
| Songs | `addSongFromUrl(spotifyUrl, initialDays, releaseDate?)` | `POST /api/songs/add-from-url` |
| Songs | `getUserSongs(userId)` | `GET /api/songs/user/{userId}` |
| Platforms | `getAuthUrl(platform, userId)` | `GET /api/oauth/{platform}/connect?user_id={userId}` |
| Platforms | `handleCallback(platform, code, userId, state)` | `POST /api/oauth/{platform}/callback` |
| Platforms | `savePlatforms(userId, platforms[])` | `POST /api/user/{userId}/platforms` |
| Platforms | `getConnectionsStatus(userId)` | `GET /api/user/{userId}/platforms/status` |
| Payment | `createCheckoutSession(userId, tier)` | `POST /api/payment/create-checkout` |
| Payment | `confirmPayment(sessionId)` | `POST /api/payment/confirm` |
| Frank's | `getArtwork(filter, userId?)` | `GET /api/frank-art/artwork` |
| Frank's | `getTokens(userId)` | `GET /api/frank-art/tokens?user_id={userId}` |
| Frank's | `placeHold(userId, artworkId)` | `POST /api/frank-art/hold` |
| Frank's | `releaseHold(artworkId)` | `POST /api/frank-art/release-hold` |
| Frank's | `downloadFree(userId, artworkId)` | `POST /api/frank-art/download` |
| Frank's | `createPaymentIntent(userId, artworkIds[], type)` | `POST /api/frank-art/create-payment-intent` |
| Frank's | `confirmPurchase(paymentIntentId)` | `POST /api/frank-art/confirm-purchase` |
| Frank's | `getMyCollection(userId)` | `GET /api/frank-art/my-collection?user_id={userId}` |
| Frank's | `getAnalytics()` | `GET /api/frank-art/analytics` |
| Dashboard | `getSongs(userId)` | `GET /api/user/{userId}/songs` |
| Dashboard | `getUpcomingPost(userId, songId)` | `GET /api/user/{userId}/songs/{songId}/upcoming-post` |
| Dashboard | `updateCaption(postId, caption)` | `PATCH /api/posts/{postId}/caption` |
| Dashboard | `approvePost(postId)` | `POST /api/posts/{postId}/approve` |
| Dashboard | `rejectPost(postId)` | `POST /api/posts/{postId}/reject` |
| Dashboard | `getUserStats(userId)` | `GET /api/user/{userId}/stats` |

## 2.3 Middleware (`frontend/src/middleware.ts`)

**Protected routes:** `/dashboard/*`, `/onboarding/*`, `/milestone/*`
**Method:** Reads `auth_token` cookie → verifies HS256 JWT signature via Web Crypto API → checks expiry → clears cookie + redirects to `/` on failure
**Requirement:** `JWT_SECRET` env var must match backend's `/noisemaker/jwt_secret_key`

## 2.4 Types (`frontend/src/types/index.ts`)

Key interfaces: `User`, `Song`, `Milestone`, `PlatformConnection`, `Post`, `AuthResponse`, `MilestoneCheckResponse`, `OAuthResponse`, `OAuthCallbackResponse`, `PaymentCheckoutResponse`, `PaymentConfirmResponse`, `PlatformStatusResponse`, `ValidateArtistResponse`, `ValidateTrackResponse`, `FrankArtwork`, plus all Frank's Garage response types.
- **Legacy ref:** `baseline_streams_per_day` in User type (should be `baseline_popularity`)

## 2.5 Other Lib Files

- `frontend/src/lib/auth-options.ts` — NextAuth config for Google/Facebook OAuth. Uses `noisemaker-auth` DynamoDB table. **APPEARS ORPHANED** — current signup flow uses custom JWT, not NextAuth
- `frontend/src/lib/ssm-loader.ts` — SSM Parameter Store loader for frontend OAuth credentials
- `frontend/src/lib/auth.ts` — Auth utilities
- `frontend/src/lib/constants.ts` — Application constants
- `frontend/src/lib/utils.ts` — Utility functions

---

# PHASE 3 — USER SIGNUP FLOW WALKTHROUGH

## Step 1: Landing Page (`/`)
- Renders `page-genz.tsx` — Gen Z Bold design with massive "NOISE MAKER" headline
- Sign In → `/auth/signin`, CTA → `/pricing`
- **No API calls**, purely static

## Step 2: Pricing + Signup (`/pricing`)
- Renders `pricing-v2.tsx` — shows 3 tier bands (Talent $25, Star $40, Legend $60)
- User pastes Spotify artist URL → calls `POST /api/songs/validate-artist` (public, rate limited 10/min)
- On valid artist: enters email + password, selects tier
- Password validation: 8+ chars + letters + numbers = medium (minimum)
- On submit:
  1. `POST /api/auth/signup` — Creates user with `tier: 'pending'`, Spotify data, hashed password
  2. Backend writes to `noisemaker-users` (user_id, email, hashed_password, subscription_tier='pending', onboarding_status, art_tokens=3, spotify_artist_id)
  3. Backend writes to `noisemaker-email-reservations` (atomic email uniqueness)
  4. Backend writes to `noisemaker-milestones` (first_payment milestone queued)
  5. Returns JWT token + user_id
  6. `POST /api/payment/create-checkout` — Creates Stripe checkout session for selected tier
  7. Redirects to Stripe hosted checkout URL
- **Password hashing:** PBKDF2-SHA256, 100000 iterations, 32-byte hex salt
- **JWT creation:** HS256 with user_id, exp (24h), iat claims

## Step 3: Payment Success (`/payment/success?session_id=cs_xxx`)
- Calls `POST /api/payment/confirm` with session_id
- Backend validates Stripe session, extracts user_id from metadata
- Backend updates `noisemaker-users`: subscription_tier, account_status='active', payment_verified=true
- Backend achieves `first_payment` milestone in `noisemaker-milestones`
- Backend calculates Spotify baseline via `baseline_calculator`
- Returns new JWT token
- Frontend stores token, redirects to `/milestone/first_payment` after 5s countdown
- **Webhook (`POST /api/payment/webhooks/stripe`)** handles same events → **M6 duplicate logic bug**

## Step 4: Milestone (`/milestone/first_payment`)
- Decodes JWT from localStorage to get userId (simple base64, no verification)
- Calls `GET /api/user/{userId}/milestones`
- Displays celebration video from S3 (`noisemakerpromobydoowopp/Milestones/milestone_first_payment/milestone_first_payment.MP4`)
- On video end or skip: calls `POST /api/user/{userId}/milestones/{milestoneId}/claim`
- Redirects to `/onboarding/how-it-works`

## Step 5: How It Works (`/onboarding/how-it-works`)
- **LOREM IPSUM placeholder** — no real content yet
- CTA "LET'S GO" → `/onboarding/platforms`

## Step 6: Platform Connections (`/onboarding/platforms`)
- Fetches `GET /api/user/{userId}/platforms/status` for tier limit and connection state
- Tier enforcement: Talent=2, Star=5, Legend=8 platform limit
- User clicks platform → `GET /api/oauth/{platform}/connect?user_id={userId}` → gets auth_url → redirects to platform OAuth
- Platform redirects to `/onboarding/platforms/callback/{platform}?code=xxx&state=xxx`
- Callback page calls `POST /api/oauth/{platform}/callback` with code + state + user_id
- Backend validates state, exchanges code for tokens, encrypts with Fernet, stores in `noisemaker-platform-connections`
- Token storage shape: `{user_id, platform, encrypted_access_token, encrypted_refresh_token, token_expires_at, platform_user_id, platform_username, connected_at}`
- Minimum 1 platform required to continue → `/onboarding/how-it-works-2`
- **MOCK_OAUTH:** NOT found in current codebase — no mock support exists
- **M9 BUG:** OAuth connect/callback/status endpoints have NO JWT auth

## Step 7: How It Works 2 (`/onboarding/how-it-works-2`)
- **LOREM IPSUM placeholder** — no real content yet
- CTA "ADD MY SONGS" → `/onboarding/add-songs`

## Step 8: Song Upload (`/onboarding/add-songs`)
- 3 song slots: Upcoming Release (initial_days=0, needs release_date 14+ days future), Best Track (initial_days=14), Second Hottest (initial_days=28)
- User pastes Spotify URL → `POST /api/songs/validate-track` (JWT required)
- On valid: shows album art, track name, artist, popularity bar
- Submit: `POST /api/songs/add-from-url` for each valid song
- Backend writes to `noisemaker-songs`: user_id, song_id (UUID), spotify_track_id, song (title), artist_title, art_url, spotify_popularity, days_in_promotion=initial_days, promotion_status (pending if initial_days=0, else active), stage_of_promotion (upcoming/best/second)
- Color extraction: referenced in `content_generator.py` but NOT triggered during song upload — happens during content generation
- S3 artwork caching: happens during content generation, NOT during upload
- Minimum 1 song required → redirects to `/dashboard`
- **The 422 error:** Likely from Pydantic validation if required fields are missing or wrong types in AddSongFromUrlRequest

## Step 9: Dashboard (`/dashboard`)
- Shows welcome banner with user name (from JWT)
- Tool cards: Frank's Garage (active), My Songs (coming soon), Analytics (coming soon)
- Quick Stats: ALL HARDCODED to "--" — not wired to API
- Sign Out: clears localStorage + cookie → `/`

---

# PHASE 4 — AUTOMATION PIPELINE STATUS

## Scheduled Lambdas (via SAM/EventBridge)

| Lambda | Trigger | Purpose | Connected? |
|--------|---------|---------|------------|
| `frank_art_generator.lambda_handler` | EventBridge cron `0 21 * * ? *` (9 PM UTC daily) | Generate 4 artworks | YES — SAM template `backend/template.yaml` |
| `frank_art_cleanup.lambda_handler` | EventBridge (Mondays, implied) | Clean purchased art, recycle | Unclear — no SAM template found for this |
| `daily_orchestrator.lambda_handler` | EventBridge (every 30 min, implied) | Schedule posts for users at 9 PM local | Unclear — no SAM template found |
| `post_dispatcher.lambda_handler` | EventBridge (hourly, implied) | Dispatch pending posts | Unclear — no SAM template found |

**CRITICAL FINDING:** Only `frank_art_generator` has a SAM template. The other 3 Lambda functions (`daily_orchestrator`, `post_dispatcher`, `frank_art_cleanup`) have no visible deployment configuration. They may be deployed manually or not yet deployed.

## Content Generation Pipeline

| File | Callable? | Status |
|------|-----------|--------|
| `content_generator.py` | Yes — called by `daily_orchestrator.py` | ACTIVE |
| `content_orchestrator.py` | Broken — 2 missing imports, duplicate code | BROKEN |
| `content_integration.py` | Broken — 4 missing imports, no callers | ORPHANED |
| `multi_platform_poster.py` | Yes — called by `post_dispatcher.py` | ACTIVE |
| `caption_generator.py` | Yes — called by `content_generator.py` | ACTIVE |
| `template_manager.py` | Referenced by `content_orchestrator.py` | ACTIVE but legacy S3 bucket |
| `image_processor.py` | Referenced by `content_orchestrator.py` | ACTIVE |

## Broken Import Chain

These files are referenced in imports but **DO NOT EXIST**:
1. `spotify/track_analyzer.py` — imported by `daily_processor.py`, `test_phase_1_and_2.py`
2. `data/promo_data_manager.py` — imported by `content_integration.py`, `content_orchestrator.py`
3. `spotify/spotify_client.py` — imported by `content_integration.py`, `content_orchestrator.py`
4. `notifications/notification_manager.py` — imported by `content_integration.py`
5. `scheduler/promotion_scheduler.py` — imported by `content_integration.py`

---

# PHASE 5 — SECURITY AUDIT

## 5.1 Endpoints Accepting user_id from Client (NOT from JWT)

| Endpoint | File | Risk |
|----------|------|------|
| `GET /api/oauth/{platform}/connect?user_id=X` | platforms.py | HIGH — impersonation |
| `POST /api/oauth/{platform}/callback` (body: user_id) | platforms.py | HIGH — impersonation |
| `GET /api/oauth/{platform}/status?user_id=X` | platforms.py | MEDIUM — info disclosure |
| `GET /api/frank-art/artwork?user_id=X` | frank_art.py | LOW |
| `GET /api/frank-art/tokens?user_id=X` | frank_art.py | MEDIUM — token balance disclosure |
| `POST /api/frank-art/hold` (body: user_id) | frank_art.py | MEDIUM |
| `POST /api/frank-art/download` (body: user_id) | frank_art.py | HIGH — token theft |
| `POST /api/frank-art/purchase` (body: user_id) | frank_art.py | HIGH — charge to wrong user |
| `GET /api/frank-art/analytics` | frank_art.py | LOW — admin endpoint |

## 5.2 Endpoints with NO Authentication

| Endpoint | File | Justified? |
|----------|------|-----------|
| `POST /api/auth/signup` | auth.py | YES — registration |
| `POST /api/auth/signin` | auth.py | YES — login |
| `POST /api/auth/exchange-token` | auth.py | YES — OAuth callback |
| `POST /api/songs/validate-artist` | songs.py | YES — pricing page (rate limited) |
| `POST /api/payment/confirm` | payment.py | PARTIAL — verified via Stripe session, but should also validate user |
| `POST /api/payment/webhooks/stripe` | payment.py | YES — webhook signature verification |
| `GET /api/oauth/{platform}/connect` | platforms.py | **NO — needs JWT** |
| `POST /api/oauth/{platform}/callback` | platforms.py | **NO — needs JWT** |
| `GET /api/oauth/{platform}/status` | platforms.py | **NO — needs JWT** |
| ALL frank_art.py endpoints (7) | frank_art.py | **NO — all need JWT** |

## 5.3 Stripe Webhook Signature Verification

In `routes/payment.py`, the webhook handler calls `stripe.Webhook.construct_event()` with the webhook secret from SSM. If construction fails, it returns 400. **Verification is mandatory, not skippable.**

## 5.4 JWT Fallback Secret

The JWT secret is loaded from Parameter Store (`/noisemaker/jwt_secret_key`). If SSM is unavailable, `env_loader.get_jwt_secret()` raises `RuntimeError` — **no fallback exists** (this is secure behavior). The old audit finding about a fallback secret appears to have been fixed.

## 5.5 Rate Limiting

| Endpoint | Rate Limit | File |
|----------|-----------|------|
| `POST /api/songs/validate-artist` | 10/minute | songs.py |
| **ALL other endpoints** | **NONE** | — |

**Missing rate limiting on:**
- `POST /api/auth/signup` — signup abuse
- `POST /api/auth/signin` — brute force (user_auth has 5-attempt lock but no HTTP rate limit)
- `POST /api/payment/create-checkout` — Stripe API abuse
- All OAuth endpoints — enumeration
- All Frank's Garage endpoints — abuse

---

# PHASE 6 — DATABASE MAP

## Tables Defined in `create_dynamodb_tables.py` (21 tables)

| Table | PK | SK | GSI | Read By | Write By |
|-------|----|----|-----|---------|----------|
| `noisemaker-email-reservations` | email | — | — | user_auth.py | user_auth.py |
| `noisemaker-users` | user_id | — | email-index | user_manager, user_auth, baseline_calculator, daily_orchestrator, monthly_recalculator | user_manager, user_auth, baseline_calculator |
| `noisemaker-songs` | user_id | song_id | — | song_manager, daily_orchestrator, content_generator | song_manager, daily_orchestrator, content_generator, popularity_tracker |
| `noisemaker-posting-history` | user_id | post_id | — | — | post_dispatcher, multi_platform_poster |
| `noisemaker-content-generation` | user_id | content_id | — | — | content_orchestrator |
| `noisemaker-content-tasks` | user_id | task_id | — | — | content_integration (ORPHANED) |
| `noisemaker-scheduled-posts` | user_id | scheduled_time | — | dashboard.py, post_dispatcher | daily_orchestrator, dashboard.py |
| `noisemaker-artwork-analytics` | user_id | artwork_id | — | — | frank_art_manager, artwork_analytics |
| `noisemaker-user-behavior` | user_id | timestamp | — | — | artwork_analytics |
| `noisemaker-milestones` | user_id | milestone_id | — | user_manager, dashboard.py | user_manager |
| `noisemaker-reddit-engagement` | user_id | post_id | — | — | — (UNUSED) |
| `noisemaker-discord-engagement` | user_id | message_id | — | — | — (UNUSED) |
| `noisemaker-discord-servers` | user_id | server_id | — | — | — (UNUSED) |
| `noisemaker-engagement-history` | user_id | engagement_id | — | — | — (UNUSED) |
| `noisemaker-community-analytics` | user_id | metric_id | — | — | — (UNUSED) |
| `noisemaker-oauth-tokens` | user_id | — | — | — | — (UNUSED — superseded by platform-connections) |
| `noisemaker-baselines` | user_id | calculation_date | — | — | baseline_calculator |
| `noisemaker-track-metrics` | track_id | poll_date | — | popularity_tracker | popularity_tracker |
| `noisemaker-artwork-cleanup` | cleanup_id | — | — | — | frank_art_cleanup (implied) |
| `noisemaker-system-alerts` | alert_id | — | — | — | — (UNUSED) |
| `noisemaker-platform-connections` | user_id | platform | — | oauth/base.py, daily_orchestrator, multi_platform_poster | oauth/base.py |

## Tables Created by `create_oauth_tables.py` (2 tables, NOT in main script)

| Table | PK | SK | Read By | Write By |
|-------|----|----|---------|----------|
| `noisemaker-oauth-states` | state | — | oauth/base.py | oauth/base.py |
| `noisemaker-platform-connections` | user_id | platform | (duplicate of above) | — |

## Additional Tables Referenced in Code but NOT in Creation Scripts

| Table | Referenced By | Status |
|-------|-------------|--------|
| `noisemaker-content` | content_generator.py, post_dispatcher.py | **MISSING from create script** |
| `noisemaker-artwork-holds` | frank_art_manager.py | **MISSING from create script** |
| `noisemaker-frank-art` | frank_art_manager.py, frank_art_generator.py, frank_art_cleanup.py, artwork_analytics.py | **MISSING from create script** |
| `noisemaker-frank-art-purchases` | frank_art_manager.py | **MISSING from create script** |
| `noisemaker-auth` | frontend auth-options.ts (NextAuth) | **MISSING from create script** (may be NextAuth-managed) |

## Unused Tables (created but never read or written)

1. `noisemaker-reddit-engagement`
2. `noisemaker-discord-engagement`
3. `noisemaker-discord-servers`
4. `noisemaker-engagement-history`
5. `noisemaker-community-analytics`
6. `noisemaker-oauth-tokens` (superseded by `noisemaker-platform-connections`)
7. `noisemaker-system-alerts`

---

# PHASE 7 — ORPHAN AND LEGACY FILE DETECTION

## 7.1 Orphaned Files (not imported or called by any other file)

| File | Reason |
|------|--------|
| `backend/scan_user.py` | Dev debug script, hardcoded user_id |
| `backend/scheduler/cron_manager.py` | Legacy cron approach, replaced by daily_orchestrator Lambda |
| `backend/scheduler/monthly_baseline_recalculator.py` | Has main() but no Lambda handler, no trigger, not imported |
| `backend/content/content_integration.py` | All 4 imports are broken (missing files), no callers |
| `backend/content/content_orchestrator.py` | Has 2 broken imports, duplicate code; still referenced but non-functional |
| `frontend/src/lib/auth-options.ts` | NextAuth config, not used by current JWT-based auth flow |
| `frontend/src/lib/ssm-loader.ts` | Only imported by auth-options.ts (which is itself orphaned) |

## 7.2 Legacy Naming References

### "streams" references:
| File | Line | Content |
|------|------|---------|
| `backend/data/song_manager.py` | 105-107 | `stream_count`, `previous_stream_count`, `average_daily_stream_count` (deprecated fields still written) |
| `backend/tests/test_phase_1_and_2.py` | 142, 358, 363, 368, 389 | `stream_count` in test data |
| `frontend/src/types/index.ts` | 10 | `baseline_streams_per_day` in User type |

### "spotify-promo-" references:
| File | Line | Content |
|------|------|---------|
| `backend/content/content_orchestrator.py` | 165 | S3 bucket `spotify-promo-generated-content` |
| `backend/content/template_manager.py` | 34 | S3 bucket `spotify-promo-templates` |
| `backend/data/dynamodb_client.py` | 52 | "Spotify Promo Engine" in docstring |
| `backend/data/user_manager.py` | 23 | "Spotify Promo Engine" in docstring |

## 7.3 Copyright Year Issues (2025 → 2026)

| File | Line | Content |
|------|------|---------|
| `frontend/src/app/auth/signin/page.tsx` | 180 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/landing-monolith.tsx` | 383 | `by DooWopp © 2025` |
| `frontend/src/app/landing-noir-luxe.tsx` | 286 | `by DooWopp © 2025` |
| `frontend/src/app/landing-aurora.tsx` | 442 | `by DooWopp © 2025` |
| `frontend/src/app/page-genz.tsx` | 245 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/pricing/pricing-v2.tsx` | 653 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/onboarding/how-it-works/page.tsx` | 96 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/onboarding/how-it-works-2/page.tsx` | 96 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/onboarding/platforms/platforms-v1-bands.tsx` | 361 | `© 2025 NOiSEMaKER by DooWopp` |
| `frontend/src/app/onboarding/add-songs/page.tsx` | 615 | `© 2025 NOiSEMaKER by DooWopp` |
| (Only callback page has correct 2026) | | |

---

# APPENDIX A — COMPLETE ENDPOINT MAP

## Public Endpoints (no auth)

| Method | Path | Rate Limit | File |
|--------|------|-----------|------|
| GET | `/` | No | main.py |
| GET | `/health` | No | main.py |
| POST | `/api/auth/signup` | No | auth.py |
| POST | `/api/auth/signin` | No | auth.py |
| POST | `/api/auth/exchange-token` | No | auth.py |
| POST | `/api/songs/validate-artist` | 10/min | songs.py |
| POST | `/api/payment/confirm` | No | payment.py |
| POST | `/api/payment/webhooks/stripe` | No | payment.py |

## Unprotected Endpoints (SHOULD have auth — BUGS)

| Method | Path | File | Bug ID |
|--------|------|------|--------|
| GET | `/api/oauth/{platform}/connect` | platforms.py | M9 |
| POST | `/api/oauth/{platform}/callback` | platforms.py | M9 |
| GET | `/api/oauth/{platform}/status` | platforms.py | M9 |
| GET | `/api/frank-art/artwork` | frank_art.py | NEW |
| GET | `/api/frank-art/tokens` | frank_art.py | NEW |
| POST | `/api/frank-art/hold` | frank_art.py | NEW |
| POST | `/api/frank-art/download` | frank_art.py | NEW |
| POST | `/api/frank-art/purchase` | frank_art.py | NEW |
| GET | `/api/frank-art/analytics` | frank_art.py | NEW |
| GET | `/api/frank-art/health` | frank_art.py | LOW |

## JWT-Protected Endpoints

| Method | Path | File |
|--------|------|------|
| POST | `/api/payment/create-checkout` | payment.py |
| POST | `/api/songs/validate-track` | songs.py |
| POST | `/api/songs/add-from-url` | songs.py |
| GET | `/api/songs/user/{user_id}` | songs.py |
| POST | `/api/user/{user_id}/platforms` | platforms.py |
| GET | `/api/user/{user_id}/platforms/status` | platforms.py |
| GET | `/api/user/{user_id}/songs` | dashboard.py |
| GET | `/api/user/{user_id}/songs/{song_id}/upcoming-post` | dashboard.py |
| GET | `/api/user/{user_id}/stats` | dashboard.py |
| GET | `/api/user/{user_id}/milestones` | dashboard.py |
| POST | `/api/user/{user_id}/milestones/{milestone_id}/claim` | dashboard.py |
| PATCH | `/api/posts/{post_id}/caption` | dashboard.py |
| POST | `/api/posts/{post_id}/approve` | dashboard.py |
| POST | `/api/posts/{post_id}/reject` | dashboard.py |

---

# APPENDIX B — PARAMETER STORE KEY MAP

All keys under `/noisemaker/` prefix in AWS SSM (us-east-2):

| Key | Used By | Purpose |
|-----|---------|---------|
| `jwt_secret_key` | middleware/auth.py, frontend middleware | JWT signing |
| `stripe_secret_key` | payment.py via env_loader | Stripe API |
| `stripe_publishable_key` | env_loader | Stripe frontend |
| `stripe_webhook_secret` | payment.py via env_loader | Webhook verification |
| `stripe_price_talent` | payment.py via env_loader | $25 tier |
| `stripe_price_star` | payment.py via env_loader | $40 tier |
| `stripe_price_legend` | payment.py via env_loader | $60 tier |
| `stripe_price_artwork_single` | env_loader (UNUSED — frank_art_manager hardcodes) | $2.99 |
| `stripe_price_artwork_5pack` | env_loader (UNUSED) | $9.99 |
| `stripe_price_artwork_15pack` | env_loader (UNUSED) | $19.99 |
| `{platform}_client_id` | oauth/base.py per platform | OAuth app ID |
| `{platform}_client_secret` | oauth/base.py per platform | OAuth secret |
| `oauth_encryption_key` | oauth/encryption.py | Fernet encryption |
| `grok_api_key` | caption_generator.py | AI captions |
| `huggingface_token` | content_generator.py, frank_art_generator.py | Image generation |
| `discord_webhook_url` | env_loader | System notifications |
| `spotify_client_id` | songs.py via env_loader | Spotify API |
| `spotify_client_secret` | songs.py via env_loader | Spotify API |

---

# APPENDIX C — S3 BUCKET MAP

**Primary bucket:** `noisemakerpromobydoowopp`

| Path Pattern | Used By | Purpose |
|-------------|---------|---------|
| `ArtSellingONLY/original/{filename}` | frank_art_generator, frank_art_manager | Full-size art (2000x2000) |
| `ArtSellingONLY/mobile/{filename}` | frank_art_generator, frank_art_manager | Mobile art (600x600) |
| `ArtSellingONLY/thumbnails/{filename}` | frank_art_generator, frank_art_manager | Thumbnail art (200x200) |
| `ArtSellingONLY/state.json` | frank_art_generator | Rotation state |
| `sold-archive/sold-thumbnails/` | frank_art_manager | Sold art archive |
| `users/{user_id}/purchased-art/` | frank_art_manager | User purchases |
| `content-colortemplates/{color}/{shade}/` | frank_art_cleanup | Recycled art templates |
| `Milestones/milestone_{type}/milestone_{type}.MP4` | user_manager | Celebration videos |
| `artwork/{song_id}.jpg` | content_generator | Cached Spotify artwork |
| `content/{user_id}/{content_id}.jpg` | content_generator | Generated promo images |

**Legacy buckets (SHOULD NOT BE USED):**

| Bucket | File | Should Be |
|--------|------|-----------|
| `spotify-promo-generated-content` | content_orchestrator.py:165 | `noisemakerpromobydoowopp` or SSM |
| `spotify-promo-templates` | template_manager.py:34 | `noisemakerpromobydoowopp` or SSM |

---

# APPENDIX D — BUG REGISTRY

## Critical

| ID | Description | File | Line |
|----|-------------|------|------|
| M9 | OAuth connect/callback/status endpoints have NO JWT auth | routes/platforms.py | 35-178 |
| BROKEN-1 | `spotify/track_analyzer.py` does not exist but is imported | scheduler/daily_processor.py | 24 |
| BROKEN-2 | `data/promo_data_manager.py` does not exist but is imported | content/content_orchestrator.py | 37,105 |
| BROKEN-3 | `spotify/spotify_client.py` does not exist but is imported | content/content_orchestrator.py | 36,104 |
| BROKEN-4 | `notifications/notification_manager.py` does not exist | content/content_integration.py | 27 |
| BROKEN-5 | `scheduler/promotion_scheduler.py` does not exist | content/content_integration.py | 24 |
| MISSING-LAMBDA | daily_orchestrator, post_dispatcher, frank_art_cleanup have no SAM templates | scheduler/, marketplace/ | — |

## High

| ID | Description | File | Line |
|----|-------------|------|------|
| M6 | Payment confirm + webhook duplicate logic | routes/payment.py | 131-217, 250-286 |
| M7 | Stripe price IDs hardcoded (artwork) | marketplace/frank_art_manager.py | 81-85 |
| SEC-1 | All Frank's Garage endpoints accept user_id without JWT | routes/frank_art.py | all |
| IMPORT-1 | schedule_engine.py uses `backend.scheduler.schedule_grids` instead of relative import | scheduler/schedule_engine.py | 26 |
| DUP-1 | content_orchestrator.py has duplicate code block (lines 1-136) | content/content_orchestrator.py | 1-136 |

## Medium

| ID | Description | File | Line |
|----|-------------|------|------|
| M1 | Deprecated stream_count fields still written | data/song_manager.py | 105-107 |
| LEGACY-1 | S3 bucket `spotify-promo-generated-content` | content/content_orchestrator.py | 165 |
| LEGACY-2 | S3 bucket `spotify-promo-templates` | content/template_manager.py | 34 |
| LEGACY-3 | `baseline_streams_per_day` in frontend User type | frontend/src/types/index.ts | 10 |
| FB-API | Facebook API version v18.0 hardcoded | data/oauth/facebook.py | 19-20 |
| BASELINE | Baseline uses FLOOR rounding, spec says ceiling | spotify/baseline_calculator.py | 192 |
| TABLES-1 | 4 tables used in code but missing from create script | scripts/create_dynamodb_tables.py | — |
| YEAR | Copyright 2025 on 10 pages (should be 2026) | See Phase 7.3 | — |

## Low

| ID | Description | File | Line |
|----|-------------|------|------|
| LOREM | how-it-works and how-it-works-2 have placeholder content | onboarding pages | — |
| STATS | Dashboard stats all hardcoded to "--" | dashboard/page.tsx | — |
| UNUSED-TABLES | 7 DynamoDB tables created but never used | create_dynamodb_tables.py | — |
| ORPHAN-1 | auth/user_auth.py session system not used (JWT used instead) | auth/user_auth.py | — |
| ORPHAN-2 | auth-options.ts NextAuth config not used | frontend/src/lib/auth-options.ts | — |
| RATE | Only 1 of 30+ endpoints has rate limiting | — | — |

---

# APPENDIX E — FILE COUNT SUMMARY

| Directory | Active Files | Orphaned/Broken | Test/Example | Total |
|-----------|-------------|-----------------|-------------|-------|
| backend/auth/ | 2 | 0 | 0 | 2 (+init) |
| backend/middleware/ | 1 | 0 | 0 | 1 (+init) |
| backend/config/ | 1 | 0 | 0 | 1 (+init) |
| backend/data/ | 3 | 0 | 0 | 3 (+init) |
| backend/data/oauth/ | 10 | 0 | 0 | 10 (+init) |
| backend/routes/ | 6 | 0 | 0 | 6 (+init) |
| backend/spotify/ | 4 | 0 | 0 | 4 (+init) |
| backend/scheduler/ | 5 | 2 | 0 | 7 (+init) |
| backend/content/ | 5 | 2 | 0 | 7 (+init) |
| backend/marketplace/ | 5 | 0 | 0 | 5 (+init) |
| backend/models/ | 1 | 0 | 0 | 1 (+init) |
| backend/notifications/ | 1 | 0 | 0 | 1 (+init) |
| backend/scripts/ | 4 | 0 | 9 | 13 |
| backend/examples/ | 0 | 0 | 1 | 1 |
| backend/tests/ | 0 | 0 | 4 | 4 (+init) |
| backend/ (root) | 1 (main.py) | 1 (scan_user.py) | 0 | 2 (+init) |
| **BACKEND TOTAL** | **49** | **5** | **14** | **68** |
| frontend/src/app/ | 18 pages | 3 test-designs | 0 | 21 |
| frontend/src/lib/ | 3 | 2 (auth-options, ssm-loader) | 0 | 5 |
| frontend/src/ (other) | 2 (middleware, types) | 0 | 0 | 2 |
| **FRONTEND TOTAL** | **23** | **5** | **0** | **28** |

---

*End of audit. This document reflects the exact state of the codebase at commit 197459e on 2026-02-25.*
