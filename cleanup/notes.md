# Notes: Onboarding Flow Investigation

**Last Updated:** Phase 2 - Pricing Page Deep Dive Complete

---

## Page 1: Landing Page
**File:** `frontend/src/app/page-genz.tsx`
**Status:** ✅ REVIEWED

### Data Collected
- NONE - purely informational/marketing page

### Links/Navigation
- `/pricing` via "Choose Your Path" and "Pick Your Plan" CTAs
- `/auth/signin` via header button (DEAD/INCOMPLETE per Dre)

### Observations
- Clean Gen Z Bold design
- No backend calls
- No data collection
- Sign in button links to `/auth/signin` which Dre confirmed is dead

---

## Page 2: Pricing Page
**File:** `frontend/src/app/pricing/pricing-v2.tsx`
**Status:** ✅ REVIEWED

### Data Collected (Form Fields)
| Field | Type | Validation |
|-------|------|------------|
| spotifyUrl | text | Regex pattern, auto-validates on paste |
| email | email | Regex validation on blur |
| password | password | Strength checker (8+ chars, letters+numbers minimum) |
| confirmPassword | password | Must match password |
| selectedTier | select | talent/star/legend |

### Data Sent to Backend (Signup Payload)
```javascript
{
  email: string,
  password: string,
  name: string,                    // From validated artist name
  tier: "pending",                 // Always "pending" at signup
  spotify_artist_id: string,
  spotify_artist_name: string,
  spotify_artist_image_url: string,
  spotify_genres: string[],
  spotify_followers: number,
  spotify_external_url: string
}
```

### Backend Endpoints Called (In Order)
1. `POST /api/songs/validate-artist` - PUBLIC, no auth
   - Request: `{ url: string }`
   - Response: `ValidateArtistResponse` with artist data

2. `POST /api/auth/signup` - PUBLIC
   - Request: SignUpRequest schema (see payload above)
   - Response: `AuthResponseEnhanced` with user_id, token, redirect_to

3. `POST /api/payment/create-checkout` - REQUIRES AUTH
   - Request: `{ user_id: string, tier: "talent"|"star"|"legend" }`
   - Response: `{ session_id: string, checkout_url: string }`
   - Redirects to Stripe checkout

### DynamoDB Tables Involved
- `noisemaker-users` - User record created
- `noisemaker-email-reservations` - Email reserved atomically

### User State After Signup (Before Payment)
```json
{
  "subscription_tier": "pending",
  "account_status": "pending",
  "onboarding_status": "tier_pending",
  "art_tokens": 3
}
```

### Observations
- Form validation is solid (email regex, password strength, confirmation)
- Spotify artist validation happens before any account creation
- User created with tier="pending" even though they selected a tier
- Actual tier only applied after Stripe payment succeeds
- Token stored in localStorage after signup

---

## Page 3: Stripe Payment Success
**File:** `frontend/src/app/payment/success/page.tsx`
**Status:** ✅ REVIEWED

### URL Pattern
`/payment/success?session_id={CHECKOUT_SESSION_ID}&user_id={user_id}`

### Flow
1. Extract session_id from URL params
2. Call `POST /api/payment/confirm` with session_id
3. Backend verifies payment with Stripe
4. Backend updates user: tier, account_status='active', milestone, onboarding_status
5. Backend returns new JWT token
6. Frontend stores token in localStorage AND cookie
7. 5-second countdown, redirect to `/milestone/first_payment`

### Backend Endpoint
`POST /api/payment/confirm` - NO AUTH REQUIRED (uses Stripe session metadata)
- Request: `{ session_id: string }`
- Response: `{ success: bool, message: string, token: string }`

### User State After Payment Confirmed
```json
{
  "subscription_tier": "talent|star|legend",  // Actual tier from selection
  "account_status": "active",
  "onboarding_status": "platforms_pending",
  "pending_milestone": "first_payment"
}
```

### Observations
- No auth required on confirm endpoint - relies on Stripe session metadata
- New JWT token returned (handles lost token during Stripe redirect)
- Token stored in both localStorage and cookie
- Milestone triggered server-side

---

## Backend Endpoints Inventory

| Endpoint | Auth Required | Purpose | Request | Response |
|----------|---------------|---------|---------|----------|
| POST /api/songs/validate-artist | ❌ NO | Validate Spotify artist URL | `{url}` | Artist data |
| POST /api/auth/signup | ❌ NO | Create user account | SignUpRequest | AuthResponseEnhanced |
| POST /api/payment/create-checkout | ✅ YES | Create Stripe session | `{user_id, tier}` | `{session_id, checkout_url}` |
| POST /api/payment/confirm | ❌ NO | Confirm payment | `{session_id}` | `{success, token}` |

---

## DynamoDB Tables (Verified via AWS CLI)

**Total: 26 tables** (CLAUDE.md says 23, HANDOFF.md says 24 - both wrong)

| Table | Purpose |
|-------|---------|
| noisemaker-album-artwork | Album art storage |
| noisemaker-artwork-analytics | Art download/purchase tracking |
| noisemaker-artwork-cleanup | Cleanup task tracking |
| noisemaker-artwork-holds | 5-min hold system for Frank's Garage |
| noisemaker-auth | Auth tokens/sessions |
| noisemaker-baselines | Initial stream baselines |
| noisemaker-community-analytics | Community engagement metrics |
| noisemaker-content-generation | Generated content log |
| noisemaker-content-tasks | Content generation queue |
| noisemaker-discord-engagement | Discord activity |
| noisemaker-discord-servers | Discord server configs |
| noisemaker-email-reservations | Atomic email uniqueness |
| noisemaker-engagement-history | Historical engagement data |
| noisemaker-frank-art | Frank's Garage artwork pool |
| noisemaker-frank-art-purchases | Purchase records |
| noisemaker-milestones | User milestone tracking |
| noisemaker-oauth-states | OAuth state tokens |
| noisemaker-platform-connections | Platform OAuth tokens |
| noisemaker-posting-history | Post history log |
| noisemaker-reddit-engagement | Reddit activity |
| noisemaker-scheduled-posts | Scheduled post queue |
| noisemaker-songs | User songs |
| noisemaker-system-alerts | System notifications |
| noisemaker-track-metrics | Song performance metrics |
| noisemaker-user-behavior | User activity tracking |
| noisemaker-users | Main user table |

---

## Security Analysis

### ✅ Good Patterns
1. `create-checkout` requires JWT auth
2. Email uniqueness via atomic reservation table
3. Password hashing with PBKDF2-SHA256 (100k iterations)
4. HttpOnly/Secure cookies in production
5. Stripe session metadata used for user verification

### Route Protection (middleware.ts)
**Protected Routes:**
- `/dashboard/*` - requires auth
- `/onboarding/*` - requires auth
- `/milestone/*` - requires auth

**Public Routes (Intentionally):**
- `/` - Landing page
- `/pricing` - Signup happens here
- `/payment/success` - Validates via Stripe

### Token Flow (Payment Success → Milestone)
1. Payment confirmed via Stripe
2. Backend returns new JWT token
3. Frontend sets `auth_token` cookie (line 51 of success/page.tsx)
4. Redirect to `/milestone/first_payment`
5. Middleware sees cookie, allows access

### ⚠️ Addressed Concerns
1. `validate-artist` rate limiting: Dre says needs more protection → Add CAPTCHA
2. `confirm` endpoint no auth: RESOLVED - Stripe metadata is trusted
3. Token storage dual approach: RESOLVED - OK for dev/prod compatibility

### Remaining Items
1. Add CAPTCHA to validate-artist
2. Add debounce to PAY NOW button

---

## Questions for Dre

1. **validate-artist rate limiting**: HANDOFF.md mentions 10/min rate limit added - is this sufficient?

2. **Double submission protection**: What prevents a user from clicking "PAY NOW" twice rapidly?

3. **Stripe webhook vs confirm endpoint**: Both can update user status - is there conflict potential?

4. **Token storage**: Both localStorage AND cookie used - intentional redundancy?

---

## Verified Facts (Confirmed True)
- ✅ Landing page is `page-genz.tsx`
- ✅ Pricing page is `pricing-v2.tsx`
- ✅ Email signup only (OAuth deferred)
- ✅ Flow: Landing → Pricing → Stripe → /payment/success → /milestone/first_payment
- ✅ User starts with tier="pending", becomes actual tier after payment
- ✅ Account starts "pending", becomes "active" after payment
- ✅ 3 art tokens awarded at signup

## Contradictions Found (VERIFIED)
- CLAUDE.md says 6 routers - actually 7 (frank_art.py exists, not marketplace.py)
- CLAUDE.md says 23 DynamoDB tables - **ACTUAL: 26 tables** (verified via AWS CLI)

---

## RESOLVED: Spotify Artist Fields

**Status:** CONFIRMED CORRECT - Spotify artist data IS needed at signup.

**Redundancy Found:**
- `name` field = `validatedArtist.artist_name`
- `spotify_artist_name` = `validatedArtist.artist_name`
- **Same value stored twice** - potential cleanup opportunity

**Design Decision (Per Dre):**
- Users are ALWAYS referred to by their **artist name** (not real name)
- The `name` field should represent the artist/band name from Spotify validation
- Consider removing `spotify_artist_name` if `name` already holds this value

**Fields That ARE Needed:**
- `spotify_artist_id` - unique identifier for Spotify API calls
- `spotify_artist_image_url` - for display
- `spotify_genres` - for content generation
- `spotify_followers` - for analytics/baseline
- `spotify_external_url` - for linking

---

## Items to Address Later (Per Dre)
- [ ] Sign-in button on landing page (dead link to /auth/signin)
- [ ] Simplify data tables - remove `spotify_artist_name` redundancy
- [ ] Review exact data needed on pricing/payment pages
- [ ] Fix npm dependency conflict (eslint 8 vs eslint-config-next wanting eslint 9)

---

## DESIGN FEEDBACK (Visual Testing Jan 6, 2026)

### Landing Page Issues (page-genz.tsx)
**Overall:** Looks cheap/cheesy - needs more modern, professional, high-resolution design

**Specific Fixes Needed:**
| Element | Issue | Fix |
|---------|-------|-----|
| DooWopp logo (header) | Too small | Height 4x bigger, width: auto |
| NOiSEMaKER logo | Too small | Much bigger - main focal point |
| Marquee banner | Too slow | Speed 2.5x faster |
| "No fake streams" badge | Wrong size, looks off | Redesign or remove |
| Desktop layout | Too much blank space | Better use of space |

**Design Direction:**
- NOT the current Gen Z Bold (too cheesy)
- NO PURPLE (overused by AI agents)
- Modern, clean, professional
- High-resolution imagery
- Works well on both mobile and desktop
- Should look trustworthy for music promotion SaaS

### Action: Create 3 New Landing Page Concepts
Research modern SaaS landing pages, then present 3 different design directions for Dre to choose from.
