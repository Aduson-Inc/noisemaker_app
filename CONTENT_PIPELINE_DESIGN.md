# NOiSEMaKER Content Pipeline — Complete Design Spec

**Status:** PLANNING — Not yet implemented
**Created:** February 10, 2026
**Author:** Tre + Claude (Planning Session)

---

## 1. What This Pipeline Does (Plain English)

Every night at 9 PM UTC, for every paying user:
1. Look at the posting schedule → determine which song goes to which platform tomorrow
2. Check if we already have content for that song that hasn't been posted to that platform yet
3. If yes → reuse it. If no → generate new content.
4. Schedule each post for a random optimal time tomorrow
5. Show the user a preview on their dashboard

That's it. Everything below is the details of how.

---

## 2. The Content Reuse Rule

**A single piece of generated content can be posted ONCE per platform before it must be regenerated.**

Example: User has 5 platforms. We generate a static image post for Song A.
- Day 1: Posted to Instagram ✓
- Day 4: Same image posted to Twitter ✓ (new platform, content still fresh)
- Day 7: Same image posted to Facebook ✓
- Day 9: Same image posted to TikTok ✓
- Day 12: Same image posted to YouTube ✓
- Day 15: Song A needs to post to Instagram again → ALL platforms used → **regenerate**

This dramatically reduces generation load. For a 5-platform user over 14 days, we generate ~3 pieces of content per song instead of ~14.

**Tracking:** Each content record stores a `posted_to` list. When `posted_to` contains all of the user's connected platforms, that content is "exhausted" and the next post for that song triggers new generation.

---

## 3. Data Requirements

### What we need BEFORE content can be generated for a song:

| Data Point | Source | Where Stored |
|---|---|---|
| Song name | Spotify API (at upload) | noisemaker-songs |
| Artist name | Spotify API (at upload) | noisemaker-songs / noisemaker-users |
| Album artwork URL | Spotify API (at upload) | noisemaker-songs.art_url |
| Genre | Spotify API (at upload) | noisemaker-songs.genre |
| Dominant colors (extracted) | Color analysis of artwork | noisemaker-songs.color_palette |
| days_in_promotion | Incremented daily | noisemaker-songs |
| promotion_stage | Derived from days_in_promotion | upcoming/live/twilight |
| Connected platforms | User's OAuth connections | noisemaker-platform-connections |
| Platform posting order (P1-P8) | Assigned by connection order (first connected = P1) | noisemaker-platform-connections.platform_order |
| Schedule position (A/B/C) | Derived from days_in_promotion | Calculated at runtime |

### Platform Numbering Rule:
Platforms are numbered in the order the user connects them. First platform connected = P1, second = P2, etc. If a user disconnects a platform, remaining platforms renumber to fill the gap (no skipped numbers). The schedule grid adapts to the new platform count automatically.

### What's missing today:
- `color_palette` — never populated (image_processor.py exists but never called)
- `platform_order` — not tracked on platform connections (P1-P8 assignment by connection order)
- `schedule_day` — not tracked on users (which day 1-14 of the current posting cycle)
- Content records — no table exists for generated content
- Posting history — no table exists for completed posts

---

## 4. Song Lifecycle & Slot System

### Onboarding (First Time Only)

The system guides users to upload up to 3 songs in a specific order:

| Order | Instruction | initial_days | Position | Stage |
|---|---|---|---|---|
| 1st | "Paste a song releasing at least 2 weeks from now" | 0 | A | Upcoming |
| 2nd (optional) | "Paste your most popular song" | 14 | B | Live |
| 3rd (optional) | "Paste your second most popular song" | 28 | C | Twilight |

Users can upload 1, 2, or 3 songs. The schedule adapts accordingly.

### The Conveyor Belt

Songs move through the cycle automatically:

```
Day 1-14:   Position A (Upcoming)  — 20% of posts
Day 15-28:  Position B (Live)      — 50% of posts
Day 29-42:  Position C (Twilight)  — 30% of posts
Day 43:     Promotion retires — removed from main rotation
```

### Day 43: Retirement & Extended Promotion

When a song hits day 43, its promotion cycle ends. The user is offered the option to **extend promotion** for $10/month per song. Extended songs:
- Post every 3 days, rotating through the user's connected platforms
- Run on a completely separate schedule from the main A/B/C cycle
- Do NOT count toward the 3-song limit
- A user can extend as many songs as they want ($10/month each)
- Example: 3 songs in main cycle + 2 extended songs + 1 more extended = 6 songs being promoted

This is recurring billing through Stripe — cancellation stops the extended promotion immediately.

### The Slot Gate Rule

**A new song can ONLY enter Position A when the current A-position song reaches day 15.**

When Song A hits day 15:
- Song A moves to Position B
- Song B (if exists) moves to Position C
- Song C (if exists) retires at day 43 or continues if still in cycle
- Position A opens → user gets notified "Your next song slot opens now"

The system tracks `a_slot_available_date` on the user record — calculated from when the current A-song started day 1 + 14 days.

### Pre-Release Timeline (Dashboard Scheduler)

The release date is the anchor — it becomes Day 15. The system works backwards to show the user a complete preparation timeline:

```
RELEASE DATE minus 30 days:  "Upload your song to your distributor (DistroKid, TuneCore, etc.)"
RELEASE DATE minus 21 days:  "Pitch your song to Spotify editorial playlists for playlist consideration"
RELEASE DATE minus 14 days:  DAY 1 — NOiSEMaKER begins promoting (Position A / Upcoming)
RELEASE DATE:                DAY 15 — Song goes live on Spotify (moves to Position B / Live)
RELEASE DATE plus 14 days:   DAY 29 — Song enters Twilight (Position C)
RELEASE DATE plus 28 days:   DAY 42 — Promotion cycle ends
RELEASE DATE plus 29 days:   DAY 43 — Promotion retires (or extend for $10/month)
```

When a user uploads an unreleased song with a release date, the dashboard shows this timeline with checkmarks for completed milestones and countdown timers for upcoming ones. This educates users on the full release strategy — not just the promotion part.

### Dashboard Display

Users see:
- Their active songs with current stage and day count
- "Next song slot opens: [date]" countdown
- Preview of tomorrow's scheduled posts
- Calendar view of the 14-day posting schedule

---

## 5. The Posting Schedule Engine

### Schedule Grids (Defined in POST_SCHEDULES_TODO.md)

The exact 14-day grids for every platform count (2-8) and song count (1/2/3) are already defined in `docs/POST_SCHEDULES_TODO.md`. These grids are used as-is — no recalculation, no algorithm. The schedule engine is a pure lookup: given a platform count, song count, and schedule day (1-14), return the grid row.

Each grid cell contains A, B, or C indicating which song position gets posted to that platform slot.

Example — 5 platforms, Week 1:
```
     P1  P2  P3  P4  P5
MON   A   B   B   C   B
TUE   B   A   B   B   C
WED   B   B   A   B   C
THU   C   B   B   A   B
FRI   B   C   B   B   A
SAT   C   B   C   B   B
SUN   B   C   A   C   B
```

### How the engine works:

```
Input:
  - user.connected_platforms (list, e.g. ["instagram", "twitter", "facebook", "youtube", "tiktok"])
  - user.platform_order (P1=instagram, P2=twitter, etc.)
  - user.active_songs (up to 3, each with days_in_promotion)
  - user.schedule_day (1-14, cycles)

Process:
  1. Count connected platforms → select correct grid (2-8)
  2. Count active songs → select song mode (1-song, 2-song, 3-song)
  3. Look up today's row in the grid
  4. Map A/B/C → actual songs based on days_in_promotion
  5. Map P1-P8 → actual platform names from user.platform_order
  6. Output: list of (song, platform) pairs for today

Output:
  [
    { song_id: "abc", platform: "instagram", position: "B" },
    { song_id: "def", platform: "twitter", position: "A" },
    { song_id: "abc", platform: "facebook", position: "B" },
    ...
  ]
```

### Song-to-Position Mapping

Position is NOT stored — it's derived at runtime:

```python
def get_position(days_in_promotion: int) -> str:
    if days_in_promotion <= 14:
        return "A"  # Upcoming
    elif days_in_promotion <= 28:
        return "B"  # Live
    elif days_in_promotion <= 42:
        return "C"  # Twilight
    else:
        return None  # Retired
```

### Schedule Day Tracking

Each user has a `schedule_day` (1-14) that increments daily and resets to 1 after 14. This determines which row of the grid to read. It starts at 1 on the user's first active promotion day.

---

## 6. Content Generation (Static Image — Phase 1)

### What gets created:

A single static image (2000×2000 PNG) containing:
1. **Background** — generated using the song's dominant color palette
2. **Song artwork** — the actual Spotify album art, layered on top
3. **Text overlay** — AI-generated caption (song name, artist, genre-appropriate messaging)

### Generation steps:

```
1. FETCH song data from noisemaker-songs
   → art_url, song_name, artist_name, genre, color_palette

2. IF color_palette is empty:
   → Download artwork from art_url
   → Run ColorAnalyzer.analyze_album_art() → extract 3 dominant colors
   → Save color_palette back to noisemaker-songs (one-time operation)

3. GENERATE background image
   → Use color_palette to create a styled background (2000×2000)
   → Gradient, geometric patterns, or abstract shapes using the palette
   → This is where the art style lives — NOiSEMaKER's visual identity

4. LAYER song artwork on background
   → Download artwork from art_url (or use cached)
   → Resize to fit composition (e.g. centered, 60% of canvas)
   → Composite onto background

5. ADD text overlay
   → Song name, artist name
   → Genre-appropriate styling (font, placement, effects)
   → Platform-specific sizing if needed

6. GENERATE caption text
   → Call Grok AI (or fallback templates)
   → Platform-specific character limits and hashtag counts
   → Returns caption string per platform

7. SAVE to S3 + DynamoDB
   → Upload image to S3: s3://noisemakerpromobydoowopp/content/{user_id}/{content_id}.png
   → Create record in noisemaker-content table
   → Record includes: image_s3_key, caption, song_id, user_id, created_at, posted_to: []
```

### Caption per platform:

The image is the same across platforms. The caption varies:

| Platform | Max Chars | Hashtags | Notes |
|---|---|---|---|
| Instagram | 2,200 | Up to 30 | Hashtag-heavy |
| Twitter/X | 280 | 2-3 | Short and punchy |
| Facebook | 63,206 | 3-5 | Conversational |
| YouTube | 5,000 | 5-10 | Description-style |
| TikTok | 2,200 | 5-8 | Trending tags |
| Reddit | 40,000 | 0 | No hashtags, authentic tone |
| Discord | 2,000 | 0 | Casual, community tone |
| Threads | 500 | 3-5 | Short, personal |

Captions are generated once per content piece and stored as a dict keyed by platform.

---

## 7. The Daily Orchestrator (Lambda)

### Trigger: EventBridge cron — 9 PM UTC daily

### Flow:

```
┌──────────────────────────────────────────────────────────┐
│                   DAILY ORCHESTRATOR                      │
│              EventBridge → Lambda (9 PM UTC)              │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 1. Get all active    │
              │    paying users      │
              │    (noisemaker-users)│
              └──────────┬──────────┘
                         │
                         ▼ (for each user)
              ┌─────────────────────┐
              │ 2. Get user's songs  │
              │    + platforms       │
              │    + schedule_day    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 3. Increment each    │
              │    song's            │
              │    days_in_promotion │
              │    (+1 daily)        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 4. Run schedule      │
              │    engine → get      │
              │    tomorrow's        │
              │    (song, platform)  │
              │    pairs             │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 5. For each pair:    │
              │    Check if reusable │
              │    content exists    │
              │    for this song     │
              │    that hasn't been  │
              │    posted to this    │
              │    platform yet      │
              └──────────┬──────────┘
                         │
                    ┌─────┴─────┐
                    │           │
              EXISTS ▼     DOESN'T EXIST ▼
         ┌──────────────┐  ┌──────────────┐
         │ 6a. Reuse    │  │ 6b. Generate │
         │ existing     │  │ new content  │
         │ content      │  │ (image +     │
         │              │  │  captions)   │
         └──────┬───────┘  └──────┬───────┘
                │                 │
                └────────┬────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 7. Create scheduled  │
              │    post record       │
              │    Pick random       │
              │    optimal time      │
              │    for this platform │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 8. Increment         │
              │    schedule_day      │
              │    (1-14 cycle)      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 9. Update Spotify    │
              │    popularity data   │
              │    Check Fire Mode   │
              │    Check milestones  │
              └─────────────────────┘
```

### Step 7 detail — Posting time selection:

Each platform has 4 optimal posting windows for music content. The system randomly picks one per post to avoid looking automated.

**CONSTRAINT:** Latest posting time is 8:00 PM. The daily cron runs at 9:00 PM to prepare the NEXT day's content. All of today's posts must complete before tomorrow's content creation begins.

**Research sources:** Sprout Social (2.7B engagements, 463K profiles, May-Sep 2025), Hootsuite/Critical Truth (1M+ posts, 118 countries), Buffer (9.6M Instagram posts, 1M+ TikToks). Times are localized — they apply in any timezone.

```python
OPTIMAL_TIMES = {
    "instagram": ["8:00 AM", "12:00 PM", "5:00 PM", "8:00 PM"],
    "twitter":   ["9:00 AM", "12:00 PM", "5:00 PM", "8:00 PM"],
    "facebook":  ["9:00 AM", "1:00 PM", "4:00 PM", "8:00 PM"],
    "youtube":   ["12:00 PM", "3:00 PM", "5:00 PM", "8:00 PM"],
    "tiktok":    ["12:00 PM", "4:00 PM", "6:00 PM", "8:00 PM"],
    "reddit":    ["7:00 AM", "10:00 AM", "12:00 PM", "5:00 PM"],
    "discord":   ["10:00 AM", "2:00 PM", "5:00 PM", "8:00 PM"],
    "threads":   ["8:00 AM", "11:00 AM", "1:00 PM", "5:00 PM"],
}
```

**Research justification:**
- **Instagram:** Engagement peaks 11AM-6PM (Sprout), evenings 6-8PM strong (Buffer 9.6M posts). Morning slot catches pre-work scroll.
- **Twitter/X:** Broad 9AM-8PM engagement (Sprout), midday strongest on Tuesdays. Fast-moving feed rewards spread timing.
- **Facebook:** 9AM-6PM weekdays dominant (Sprout). Steady all-day engagement, mornings particularly strong.
- **YouTube:** Noon + 3-8PM (Sprout). Afternoon/evening viewing when users have time for longer content.
- **TikTok:** 5-9PM peak (Sprout), 4-6PM strong (Hootsuite). Entertainment platform = after-work hours dominate.
- **Reddit:** Early morning (6-8AM) and lunch (12PM) peaks. Community browses during work breaks. No evening slot — Reddit music subs are daytime active.
- **Discord:** Community platform — midday through evening when servers are active. No early morning (servers are quiet).
- **Threads:** 9AM-1PM Tue-Fri peak (QuickFrame/Plann 2025 study). Short-form discussion platform = daytime activity.

Times are in the user's timezone. All scheduled times land on the top of an hour (no :15, :30, :45 times).

---

## 8. The Posting Lambda (Post Dispatcher)

### Trigger: EventBridge cron — hourly at :55, active window only

Since all scheduled posting times land on the top of an hour, and the earliest any platform posts is 7:00 AM (Reddit) and the latest is 8:00 PM, the dispatcher runs from **6:55 AM to 7:55 PM** in the user's local timezone — 14 checks per day, not 24.

**Schedule:** `cron(55 6-19 * * ? *)` — runs at 6:55 AM, 7:55 AM, 8:55 AM, ... 7:55 PM.

**Timezone note:** Since users span multiple timezones, the EventBridge schedule runs in UTC covering the full range needed. The query filters by `scheduled_time` which is stored as UTC, so only posts actually due in the current window are returned regardless of the user's local timezone. Hours where no user has a pending post return zero results and the Lambda exits immediately (~100ms).

**Why :55 and not :00?** Gives 5 minutes of buffer for the Lambda to cold-start, query DynamoDB, download images, and make API calls. Posts land on-platform right around the scheduled hour.

### Flow:

```
1. Query noisemaker-scheduled-posts for:
   - status = "pending"
   - scheduled_time between now and (now + 1 hour)
2. For each post:
   a. Load content from noisemaker-content (image S3 key + caption for this platform)
   b. Download image from S3
   c. Load user's OAuth token for this platform from noisemaker-platform-connections
   d. Call platform API to post (multi_platform_poster.py logic)
   e. On success:
      - Update scheduled post status → "posted"
      - Add platform to content.posted_to list
      - If all user platforms now in posted_to → mark content status = "exhausted"
   f. On failure:
      - Update post status → "failed", log error
      - Retry logic: re-queue for next available time slot (max 2 retries)
3. Write results to noisemaker-posting-history
```

### Cost efficiency:

The dispatcher runs 14 times per day (6:55 AM through 7:55 PM UTC-adjusted). During hours when no users have pending posts, invocations exit in ~100ms at 128MB — fractions of a penny. Total monthly cost: well under $1.

---

## 9. DynamoDB Tables (New + Modified)

### NEW: noisemaker-content
Stores generated content pieces.

| Field | Type | Description |
|---|---|---|
| user_id (PK) | String | User who owns this content |
| content_id (SK) | String | Unique content identifier |
| song_id | String | Which song this content is for |
| image_s3_key | String | S3 path to the generated image |
| captions | Map | `{ "instagram": "...", "twitter": "...", ... }` |
| color_palette | List | 3 dominant colors used for this generation |
| posted_to | List | Platforms this content has been posted to |
| created_at | String | ISO timestamp |
| status | String | "active" / "exhausted" (all platforms used) |

### NEW: noisemaker-scheduled-posts
Queue of posts scheduled for future delivery.

| Field | Type | Description |
|---|---|---|
| user_id (PK) | String | User |
| post_id (SK) | String | Unique post identifier |
| content_id | String | Reference to noisemaker-content |
| song_id | String | Which song |
| platform | String | Target platform |
| scheduled_time | String | ISO timestamp — when to post |
| status | String | "pending" / "posted" / "failed" |
| schedule_day | Number | Which day (1-14) of the cycle |
| schedule_position | String | A, B, or C |
| created_at | String | ISO timestamp |

### NEW: noisemaker-posting-history
Audit trail of completed posts.

| Field | Type | Description |
|---|---|---|
| user_id (PK) | String | User |
| post_id (SK) | String | Same as scheduled-posts |
| content_id | String | What was posted |
| song_id | String | Which song |
| platform | String | Where it was posted |
| posted_at | String | Actual post timestamp |
| platform_post_id | String | ID returned by the platform API |
| status | String | "success" / "failed" |
| error_message | String | If failed, why |

### MODIFIED: noisemaker-songs (add fields)

| New Field | Type | Description |
|---|---|---|
| color_palette | List | 3 dominant colors extracted from artwork `["#FF5733", "#C70039", "#900C3F"]` |
| schedule_position | String | A, B, or C (derived, but cached for dashboard) |
| a_slot_start_date | String | When this song started as Position A (for slot gate calc) |

### MODIFIED: noisemaker-users (add fields)

| New Field | Type | Description |
|---|---|---|
| schedule_day | Number | Current day in the 14-day cycle (1-14) |
| a_slot_available_date | String | When the next Position A slot opens |
| timezone | String | User's timezone for posting time conversion |

### MODIFIED: noisemaker-platform-connections (add field)

| New Field | Type | Description |
|---|---|---|
| platform_order | Number | P1, P2, P3... assigned by connection order. Renumbers on disconnect. |

---

## 10. S3 Storage Structure

```
s3://noisemakerpromobydoowopp/
├── ArtSellingONLY/              ← Frank's Garage (existing, 32+ images)
│   └── original/
├── content/                     ← NEW: Generated promotion content
│   └── {user_id}/
│       ├── {content_id}.png     ← Generated static images
│       └── {content_id}_thumb.png  ← Dashboard preview thumbnail
├── artwork/                     ← NEW: Cached song artwork from Spotify
│   └── {song_id}.jpg           ← Downloaded once, reused for all generations
└── templates/                   ← FUTURE: Background style templates
```

---

## 11. Files To Create (Simplified Pipeline)

### DELETE these broken files:
- `backend/content/content_orchestrator.py` — full rewrite
- `backend/content/content_integration.py` — full rewrite
- `backend/scheduler/cron_manager.py` — dead code (Linux crontab)
- `backend/content/template_manager.py` — references nonexistent S3 bucket/templates

### KEEP and FIX:
- `backend/content/image_processor.py` — fix font paths, keep ColorAnalyzer
- `backend/content/caption_generator.py` — add 5 missing platforms to limits dict
- `backend/content/multi_platform_poster.py` — fix table reference, keep posting logic
- `backend/config/platform_config.py` — already working
- `backend/scheduler/posting_schedule.py` — already working

### CREATE NEW:
| File | Purpose | Lines (est.) |
|---|---|---|
| `backend/scheduler/schedule_engine.py` | Reads the 14-day grids, maps songs to platforms for any given day | ~200 |
| `backend/scheduler/schedule_grids.py` | Pure data: exact grids from POST_SCHEDULES_TODO.md transcribed as Python dicts for 2-8 platforms × 1/2/3 songs | ~200 |
| `backend/content/content_generator.py` | The simplified pipeline: colors → background → layer art → add text → save | ~250 |
| `backend/scheduler/daily_orchestrator.py` | Lambda entry point: for each user, run schedule + generate/reuse + schedule posts | ~300 |
| `backend/scheduler/post_dispatcher.py` | Lambda entry point: every 15 min, fire pending posts | ~150 |

**Total new code: ~1,050 lines across 5 files** (vs. the current 3,400+ lines across 11 broken files)

### FIX in existing file:
| File | What to fix |
|---|---|
| `backend/scheduler/daily_processor.py` | Remove MilestoneTracker import (line 30), remove instance (line 60), remove call (line 596). Fix has_been_on_fire_before → previous_fire_peak. Delete dead _update_fire_mode_status(). This file handles Spotify data updates + fire mode — it runs BEFORE the content pipeline. |
| `backend/routes/songs.py` | Add slot gate check: reject day-0 songs if current A-song < day 15. Add color_palette extraction after song upload. |

---

## 12. Execution Order

### Phase 1: Foundation (do first)
1. Create DynamoDB tables (noisemaker-content, noisemaker-scheduled-posts, noisemaker-posting-history)
2. Fix daily_processor.py (broken import crash)
3. Fix image_processor.py (font paths)
4. Fix caption_generator.py (missing platforms)
5. Fix songs.py (slot gate + color extraction)

### Phase 2: Schedule Engine
6. Create schedule_grids.py (pure data)
7. Create schedule_engine.py (grid lookup + song-to-platform mapping)
8. Add platform_order and schedule_day to user records
9. Test: given a user with 3 songs and 5 platforms, verify correct output for all 14 days

### Phase 3: Content Generation
10. Create content_generator.py (the actual image creation pipeline)
11. Test: generate a real static image from a real song's artwork + colors
12. Verify S3 upload and DynamoDB record creation

### Phase 4: Orchestration
13. Create daily_orchestrator.py (Lambda)
14. Create post_dispatcher.py (Lambda)
15. Create EventBridge schedules for both
16. Delete broken files (content_orchestrator.py, content_integration.py, cron_manager.py, template_manager.py)

### Phase 5: Dashboard Integration
17. API endpoint: GET /api/dashboard/preview — tomorrow's scheduled posts
18. API endpoint: GET /api/dashboard/schedule — 14-day calendar view
19. API endpoint: GET /api/songs/next-slot — when the A-slot opens
20. Frontend: preview cards, schedule calendar, slot countdown

---

## 13. Fire Mode Override (Future — After Phase 5)

When Fire Mode activates on a song, the schedule changes:
- Fire song gets 70% of all posts
- A (Upcoming): drops to 10%
- B (Live): drops to 20%
- C (Twilight): drops to 0%

Separate Fire Mode grids need to be created for each platform count.

---

## 14. Extended Promotion (Future — After Fire Mode)

$10/month add-on for songs that had Fire Mode during their 42-day cycle:
- 1 post every 3 days, rotating through platforms
- Does NOT count toward 3-song limit
- Separate Stripe billing integration required

---

## 15. Phase 2 Preview: Animated Video Posts (Future)

After static posts are running perfectly:
1. User uploads full song (MP3/WAV)
2. Frontend slider lets user select best 10-second clip
3. Backend trims + stores only the 10-second clip in S3
4. Image animation API (Runway ML / Stability AI / Luma AI) creates subtle motion from song artwork
5. FFmpeg Lambda layer composites: animated image + caption overlay + 10-second audio = video
6. Same posting pipeline, different content type flag

This uses the same schedule engine, content reuse rules, and posting infrastructure.
The only new pieces are: audio upload/trim, image animation API call, FFmpeg video composition.

---

## Document Version: 1.0 FINAL
## Last Updated: February 10, 2026
## Status: APPROVED — Ready for implementation planning
