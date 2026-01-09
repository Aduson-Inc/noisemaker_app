# NOiSEMaKER DynamoDB Tables

**Last Verified:** December 21, 2025 (via AWS CLI)
**Region:** us-east-2 (Ohio)
**Billing:** PAY_PER_REQUEST (on-demand)
**Total Tables:** 24

---

## CORE TABLES (5)

### noisemaker-users
User accounts and profiles

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| email-index | email | — |

---

### noisemaker-auth
NextAuth.js sessions, accounts, verification tokens

| Key | Attribute | Type |
|-----|-----------|------|
| PK | pk | HASH |
| SK | sk | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| GSI1 | GSI1PK | GSI1SK |

---

### noisemaker-songs
User's songs in 42-day promotion cycle

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | song_id | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| spotify-track-index | spotify_track_id | — |
| cycle-status-index | cycle_status | cycle_end_date |

---

### noisemaker-oauth-states
Temporary OAuth state tokens for platform connections

| Key | Attribute | Type |
|-----|-----------|------|
| PK | state | HASH |

No GSIs.

---

### noisemaker-platform-connections
User's connected social media platforms

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | platform | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| platform-index | platform | user_id |

---

## CONTENT/POSTING TABLES (4)

### noisemaker-scheduled-posts
Posts scheduled for future publishing

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | scheduled_time_post_id | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| schedule-index | scheduled_date | scheduled_time |
| platform-index | platform | scheduled_time |

---

### noisemaker-posting-history
Record of all published posts

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | posted_at_post_id | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| song-index | song_id | posted_at |
| platform-index | platform | posted_at |

---

### noisemaker-content-generation
AI-generated captions and content

| Key | Attribute | Type |
|-----|-----------|------|
| PK | song_id | HASH |
| SK | content_id | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| user-index | user_id | created_at |

---

### noisemaker-content-tasks
Queue for content generation tasks

| Key | Attribute | Type |
|-----|-----------|------|
| PK | task_id | HASH |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| status-index | status | created_at |
| user-index | user_id | created_at |

---

## SPOTIFY TRACKING TABLES (2)

### noisemaker-baselines
Weekly baseline stream metrics for Fire Mode

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | calculated_at | RANGE |

No GSIs.

---

### noisemaker-track-metrics
Daily Spotify metrics for tracks

| Key | Attribute | Type |
|-----|-----------|------|
| PK | spotify_track_id | HASH |
| SK | date | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| user-index | user_id | date |

---

## MILESTONES TABLE (1)

### noisemaker-milestones
User milestone achievements

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | milestone_type | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| pending-index | played | achieved_at |

---

## MARKETPLACE TABLES (5)

### noisemaker-album-artwork
Available album artwork for purchase

| Key | Attribute | Type |
|-----|-----------|------|
| PK | artwork_id | HASH |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| status-index | status | created_at |
| style-index | style | created_at |

---

### noisemaker-artwork-holds
Temporary holds during checkout (TTL enabled)

| Key | Attribute | Type |
|-----|-----------|------|
| PK | artwork_id | HASH |

No GSIs.

---

### noisemaker-artwork-analytics
Artwork views, purchases, engagement

| Key | Attribute | Type |
|-----|-----------|------|
| PK | artwork_id | HASH |
| SK | date | RANGE |

No GSIs.

---

### noisemaker-artwork-cleanup
Queue for artwork cleanup tasks

| Key | Attribute | Type |
|-----|-----------|------|
| PK | task_id | HASH |

No GSIs.

---

### noisemaker-user-credits
User's purchased artwork credits

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | purchase_id | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| stripe-index | stripe_payment_id | — |

---

## COMMUNITY TABLES (5)

### noisemaker-discord-engagement
Discord server engagement tracking

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | server_id_timestamp | RANGE |

No GSIs.

---

### noisemaker-discord-servers
Discord servers configured for promotion

| Key | Attribute | Type |
|-----|-----------|------|
| PK | server_id | HASH |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| user-index | user_id | — |

---

### noisemaker-reddit-engagement
Reddit subreddit engagement tracking

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | subreddit_timestamp | RANGE |

No GSIs.

---

### noisemaker-engagement-history
Historical engagement across all platforms

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | platform_date | RANGE |

No GSIs.

---

### noisemaker-community-analytics
Aggregated community engagement analytics

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | period | RANGE |

No GSIs.

---

## SYSTEM TABLES (2)

### noisemaker-system-alerts
System-wide alerts and notifications

| Key | Attribute | Type |
|-----|-----------|------|
| PK | alert_id | HASH |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| status-index | status | created_at |
| severity-index | severity | created_at |

---

### noisemaker-user-behavior
User behavior tracking for analytics

| Key | Attribute | Type |
|-----|-----------|------|
| PK | user_id | HASH |
| SK | event_type_timestamp | RANGE |

| GSI | Partition Key | Sort Key |
|-----|---------------|----------|
| event-index | event_type | timestamp |

---

## SUMMARY

| Category | Count | Tables |
|----------|-------|--------|
| Core | 5 | users, auth, songs, oauth-states, platform-connections |
| Content/Posting | 4 | scheduled-posts, posting-history, content-generation, content-tasks |
| Spotify Tracking | 2 | baselines, track-metrics |
| Milestones | 1 | milestones |
| Marketplace | 5 | album-artwork, artwork-holds, artwork-analytics, artwork-cleanup, user-credits |
| Community | 5 | discord-engagement, discord-servers, reddit-engagement, engagement-history, community-analytics |
| System | 2 | system-alerts, user-behavior |
| **TOTAL** | **24** | |

---

## Quick Reference

```bash
# List all tables
aws dynamodb list-tables --region us-east-2 --query 'TableNames[?starts_with(@, `noisemaker-`)]'

# Describe a specific table
aws dynamodb describe-table --table-name noisemaker-users --region us-east-2
```
