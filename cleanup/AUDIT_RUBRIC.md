# NOiSEMaKER Platform Audit Rubric

**Created:** January 6, 2026
**Purpose:** Systematic verification of platform connections, tier enforcement, and data storage
**Status:** IN PROGRESS
**Last Updated:** January 6, 2026

---

## Complete User Journey (Confirmed by Dre)

```
Landing Page → Pricing Page → Stripe Payment
                                    ↓
                         Payment Success Page
                         (Milestone video plays)
                                    ↓
                         How It Works #1 (static)
                                    ↓
                         Connect Platforms Page
                         (OAuth for each platform)
                                    ↓
                         How It Works #2 (static)
                                    ↓
                         Add Songs Page
                         (3 songs with staggered days)
                                    ↓
                              Dashboard
                                    ↓
                         Frank's Garage (Art marketplace)
```

**Pages to Audit:**
- [x] Landing Page (`page-genz.tsx`)
- [x] Pricing Page (`pricing-v2.tsx`)
- [x] Payment Success (`payment/success/page.tsx`)
- [x] How It Works #1 (`onboarding/how-it-works/page.tsx`) - **⚠️ LOREM IPSUM PLACEHOLDER**
- [?] Connect Platforms (`onboarding/platforms/platforms-v1-bands.tsx`)
- [x] How It Works #2 (`onboarding/how-it-works-2/page.tsx`) - **⚠️ LOREM IPSUM PLACEHOLDER**
- [?] Add Songs (`onboarding/add-songs/page.tsx`) - ✅ Working
- [?] Dashboard (`dashboard/page.tsx`) - ✅ Working (My Songs & Analytics coming soon)
- [?] Frank's Garage (`dashboard/garage/page.tsx`) - ✅ Complete

---

## Tier Structure (Confirmed by Dre)

| Tier | Price | Platforms Allowed | Songs Allowed |
|------|-------|-------------------|---------------|
| Talent | $25 | 2 | 3 |
| Star | $40 | 5 | 3 |
| Legend | $60 | 8 | 3 |

---

## Platform Status

| Platform | OAuth Status | Scopes OK? | Notes |
|----------|-------------|------------|-------|
| Facebook | Should work | ? | Meta ecosystem |
| Instagram | Should work | ? | Meta ecosystem |
| Threads | Should work | ? | Meta ecosystem |
| Twitter/X | Likely broken | NO | Needs different scopes |
| TikTok | Likely broken | NO | Needs different scopes |
| YouTube | Unknown | ? | |
| Discord | Unknown | ? | |
| Reddit | Unknown | ? | |

---

## Critical Questions to Answer

### Platform Connection Logic
- [ ] Can user connect MORE platforms than tier allows?
- [ ] Can user connect FEWER platforms than tier allows?
- [ ] Can user connect ZERO platforms and proceed?
- [ ] What happens if user downgrades tier with platforms connected?
- [ ] Where is platform selection enforced? (Frontend/Backend/Both?)

### Subscription Logic
- [ ] Where is subscription stored? (DynamoDB table name?)
- [ ] What fields track subscription status?
- [ ] When does subscription renew?
- [ ] How is Stripe subscription ID linked to user?
- [ ] What happens when payment fails?

### Song Limits
- [ ] How many songs per tier?
- [ ] Where is song count enforced?
- [ ] Can user exceed song limit?

---

## Files to Audit

### Backend
- [ ] `routes/platforms.py` - OAuth flows
- [ ] `routes/payment.py` - Stripe integration
- [ ] `data/user_manager.py` - User data storage
- [ ] `data/platform_oauth_manager.py` - Token storage
- [ ] `routes/songs.py` - Song management

### Frontend
- [ ] `src/app/onboarding/platforms/` - Platform selection UI
- [ ] `src/app/pricing/` - Tier selection
- [ ] `src/lib/api.ts` - API calls

---

## Findings Log

### Finding 1: Tier Configuration (user_manager.py lines 40-68)
| Tier | Price | Max Songs | Platforms Limit |
|------|-------|-----------|-----------------|
| Talent | $25 | **3** | 2 |
| Star | $40 | **3** | 5 |
| Legend | $60 | **3** | 8 |

**NOTE:** All tiers have max_active_songs = 3. This is SAME for all tiers!

---

### Finding 2: Platform Limit ENFORCEMENT (VERIFIED SECURE)

**Backend (user_manager.py lines 406-414):**
```python
if len(selected_platforms) > platform_limit:
    return {
        'success': False,
        'error': f'Platform limit exceeded. Tier allows {platform_limit} platforms...'
    }
```

**Frontend (platforms-v1-bands.tsx lines 145-148):**
```typescript
if (connectedCount >= platformLimit) {
    setError(`You've reached your ${tier.toUpperCase()} tier limit...`);
    return;
}
```

**STATUS:** DOUBLE ENFORCEMENT - User cannot connect more platforms than tier allows.

---

### Finding 3: Minimum Platform Requirement
- User MUST connect at least 1 platform to continue (`canContinue = connectedCount >= 1`)
- User CAN connect FEWER than their limit allows
- User CANNOT proceed with ZERO platforms

---

### Finding 4: Payment Flow Security (payment.py)

**Checkout Creation (line 95-98):**
```python
metadata={
    'user_id': request.user_id,
    'tier': request.tier
}
```

**Payment Confirmation (lines 152-158):**
```python
user_id = session.metadata.get('user_id')
tier = session.metadata.get('tier')
success = user_manager.update_subscription_tier(user_id, tier)
```

**SECURITY:** Tier is stored in Stripe metadata at checkout creation. User cannot modify this. Tier is retrieved from Stripe session, not from user input.

**After Payment:**
1. `subscription_tier` updated
2. `account_status` set to 'active'
3. `first_payment` milestone triggered
4. `onboarding_status` set to 'platforms_pending'

---

### Finding 5: Subscription Events (Stripe Webhooks)

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Set tier, set account_status='active' |
| `customer.subscription.deleted` | Deactivate account, reason='subscription_canceled' |
| `invoice.payment_failed` | Set account_status='pending' |

**NOTE:** No explicit subscription expiration date stored. Stripe manages billing cycle.

---

### Finding 6: Platform OAuth Scopes

| Platform | Scopes Configured | Status |
|----------|------------------|--------|
| Instagram | `instagram_content_publish`, `instagram_basic`, `pages_read_engagement` | Should work |
| Facebook | `pages_manage_posts`, `pages_read_engagement`, `pages_show_list` | Should work |
| Threads | `threads_basic`, `threads_content_publish` | Should work |
| Twitter | `tweet.write`, `tweet.read`, `users.read`, `offline.access` | **NEEDS PKCE** |
| TikTok | `video.upload`, `user.info.basic` | **May need more scopes** |
| YouTube | `youtube.upload`, `youtube` | Unknown |
| Reddit | `submit`, `read`, `identity` | Unknown |
| Discord | **Webhook only** | Different flow |

---

### Finding 7: Song Limit Enforcement (VERIFIED)

**Location:** `routes/songs.py` lines 449-455

```python
existing_songs = song_manager.get_user_active_songs(user_id, limit=10)
if len(existing_songs) >= 3:
    raise HTTPException(
        status_code=400,
        detail="You already have 3 songs in promotion..."
    )
```

**STATUS:** Song limit is HARDCODED to 3 for ALL tiers. This matches `user_manager.py` where all tiers have `max_active_songs: 3`.

**Additional Song Protections:**
- Duplicate song check (lines 458-463)
- Artist ownership verification (lines 507-515)
- Rate limiting on validate-artist (10/minute per IP)

---

### Finding 8: Artist Ownership Verification

When adding a song, the system:
1. Gets user's `spotify_artist_id` from profile
2. Fetches track info from Spotify
3. Compares track's artist IDs with user's linked artist
4. **REJECTS if mismatch** - User can only add their OWN songs

This prevents users from promoting songs they don't own.

---

## Onboarding Redirect Rules (CORRECTED - Jan 6 2026)

**Location:** `backend/routes/auth.py` function `_get_redirect_path()` (lines 72-142)

### The Logic (FINAL):
```
1. Account inactive → /account-inactive
2. Tier = pending → /pricing
3. Pending milestone video → /milestone/{type}
4. onboarding_status == 'complete' → /dashboard (ALWAYS)
5. First-time: platforms == 0 → /onboarding/how-it-works
6. First-time: songs == 0 → /onboarding/how-it-works-2
7. First-time: has 1+ platform AND 1+ song → mark complete, → /dashboard
```

### Rule Summary:

**First-time onboarding (never reached dashboard):**
| Platforms | Songs | Redirect To |
|-----------|-------|-------------|
| 0 | any | How It Works #1 → Platforms |
| 1+ | 0 | How It Works #2 → Songs |
| 1+ | 1+ | Dashboard (marks onboarding complete) |

**After reaching dashboard once (onboarding_status = 'complete'):**
- ALWAYS goes to Dashboard
- Add more platforms/songs FROM dashboard (up to limits)
- NEVER redirected back to onboarding pages

### Key Points:
- Minimum to complete onboarding: **1 platform + 1 song**
- Maximum platforms: Tier-based (Talent=2, Star=5, Legend=8)
- Maximum songs: 3 for all tiers
- Once dashboard reached, user is "graduated" from onboarding

---

## Fixes Applied This Session

| Issue | File | Line | Fix |
|-------|------|------|-----|
| Onboarding redirect logic | `auth.py` | 72-142 | Complete rewrite - check onboarding_status first |
| Sign Out not clearing auth | `dashboard/page.tsx` | 60-72 | Added proper logout (clear localStorage + cookie) |

---

## Questions Still Outstanding

1. ~~**Song limit enforcement:** Where is max_active_songs=3 checked?~~ **ANSWERED: songs.py:451**
2. **Subscription renewal:** Stripe manages billing cycle. No explicit expiration date stored.
3. **Downgrade handling:** Not explicitly handled - platforms remain connected even if exceeds new limit.

---

## SUMMARY: Security Status

| Area | Status | Notes |
|------|--------|-------|
| Tier Cheating (Pay low, get high) | **SECURE** | Tier from Stripe metadata only |
| Platform Limit Bypass | **SECURE** | Double-checked (frontend + backend) |
| Song Limit Bypass | **SECURE** | Hardcoded check before add |
| Song Ownership | **SECURE** | Artist ID verification |
| Payment Verification | **SECURE** | Stripe session validation |
| Rate Limiting | **PARTIAL** | validate-artist only (need CAPTCHA) |

---

## ACTION ITEMS - Issues Found

### CRITICAL - Content Missing
| Issue | File | Line | Action |
|-------|------|------|--------|
| Lorem ipsum placeholder | `how-it-works/page.tsx` | 68-76 | Replace with actual content |
| Lorem ipsum placeholder | `how-it-works-2/page.tsx` | 68-76 | Replace with actual content |

### HIGH PRIORITY - Functionality
| Issue | File | Line | Action |
|-------|------|------|--------|
| Sign Out not working | `dashboard/page.tsx` | 60-65 | Links to "/" instead of clearing auth |
| Dashboard stats placeholders | `dashboard/page.tsx` | 150-165 | Show "--" - need API integration |
| My Songs "Coming Soon" | `dashboard/page.tsx` | 109-122 | Needs implementation |
| Analytics "Coming Soon" | `dashboard/page.tsx` | 124-138 | Needs implementation |

### MEDIUM - Security Improvements
| Issue | File | Action |
|-------|------|--------|
| Add CAPTCHA | `validate-artist` endpoint | Prevent automated abuse |
| Add debounce | PAY NOW button | Prevent double-click |
| Tier downgrade handling | Payment flow | Decide what happens to extra platforms |

### LOW - Documentation
| Issue | Action |
|-------|--------|
| CLAUDE.md says 6 routers | Update to 7 (frank_art.py exists) |
| CLAUDE.md says 23 tables | Update to 26 (verified via AWS CLI) |
| HANDOFF.md has WSL paths | Update to Windows paths |

---

## Add Songs Page Analysis

### Song Stagger System (42-Day Cycle)
| Song | Label | Initial Days | Stage |
|------|-------|-------------|-------|
| Song 1 | UPCOMING RELEASE | 0 | Upcoming (requires release date 14+ days out) |
| Song 2 | YOUR BEST TRACK | 14 | Live |
| Song 3 | SECOND HOTTEST | 28 | Twilight |

### Rules
- Minimum 1 song to proceed
- Maximum 3 songs (all tiers)
- Song 1 MUST have release date 14+ days in future
- Songs validated against user's spotify_artist_id

---

## Frank's Garage Analysis

### Token System
- Users earn **3 tokens per song** added (max 12 from songs)
- Free download costs **1 token** (art stays in pool)
- Tokens are NOT used for purchases (real money only)

### Pricing
| Type | Price | Art Count |
|------|-------|-----------|
| Single | $2.99 | 1 |
| Bundle 5 | $9.99 | 5 |
| Bundle 15 | $19.99 | 15 |

### Features
- 5-minute hold system for previewing
- Selection mode for bulk purchases
- Gallery filters: All, New (7d), Popular (5+), Exclusive (0)
- User collection tracking (free vs purchased)

---
