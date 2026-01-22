Hmm # NOiSEMaKER Systems & Connections TODO

**Last Updated:** December 26, 2025
**Status:** Onboarding 85% Complete - Moving to Dashboard

---

## TABLE OF CONTENTS
1. [Critical Issues - Immediate Action](#critical-issues---immediate-action)
2. [Smart Sign-In Flow](#smart-sign-in-flow)
3. [Milestone System](#milestone-system)
4. [Cost Optimization](#cost-optimization)
5. [Data Flow Gaps](#data-flow-gaps)
6. [Future Enhancements](#future-enhancements)

---

## CRITICAL ISSUES - IMMEDIATE ACTION

### 1. User Onboarding Status Tracking
**Priority:** P0 - CRITICAL
**Status:** ✅ COMPLETED (Dec 26, 2025)
**Estimated Savings:** Prevents lost signups

**Solution Implemented:**
- `_get_redirect_path()` in `backend/routes/auth.py` handles smart routing
- Checks: account status → tier → pending milestones → platform count → song count
- Returns `redirect_to` field in auth responses

**Files Modified:**
- [x] `backend/routes/auth.py` - Smart `_get_redirect_path()` function
- [x] `backend/data/user_manager.py` - `update_onboarding_status()` method
- [x] `frontend/src/types/index.ts` - `MilestoneCheckResponse` type fixed
- [x] Platform OAuth flow integrated with tier limits

---

### 2. Full Table Scan in get_all_active_users()
**Priority:** P0 - CRITICAL
**Status:** BUG
**Estimated Savings:** $500-2000+/month

**Location:** `backend/data/user_manager.py:859-881`

**Problem:**
Full table scan of `noisemaker-users` every time the function is called.

**Solution:**
Create GSI on `(account_status, created_at)` and query instead of scan.

**Files to Modify:**
- [ ] `backend/scripts/create_dynamodb_tables.py` - Add GSI
- [ ] `backend/data/user_manager.py` - Replace scan with query

---

### 3. Email Lookup Uses Table Scan
**Priority:** P1 - HIGH
**Status:** BUG
**Location:** `backend/auth/user_auth.py:157-207`

**Problem:**
`get_user_id_by_email()` scans entire table instead of using `email-index` GSI.

**Code Comment (line 165-177) says to upgrade but it wasn't done:**
```python
# TODO - PRODUCTION UPGRADE:
# For production scale (1000+ users), this should be upgraded to use a
# Global Secondary Index (GSI) on the email field
```

**Solution:**
Use the existing `email-index` GSI with query instead of scan.

---

## SMART SIGN-IN FLOW

### ✅ IMPLEMENTED (Dec 26, 2025)
Backend now returns `redirect_to` field based on user state.
```
/auth/signin → Backend checks state → Returns {user_id, token, redirect_to} → Frontend follows redirect
```

### Required Flow
```
Sign-In Success
      │
      ▼
┌─────────────────┐
│ account_status  │──── 'inactive' ────► /account-issue
│    check        │
└─────────────────┘
      │ 'active'
      ▼
┌─────────────────┐
│subscription_tier│──── 'pending' ─────► /pricing
│    check        │
└─────────────────┘
      │ has tier
      ▼
┌─────────────────┐
│ milestone_check │──── has_pending ───► /milestone/{type}
│  (first_payment │                      (play video once)
│   + streaming)  │
└─────────────────┘
      │ no pending
      ▼
┌─────────────────┐
│onboarding_status│──── incomplete ────► /onboarding/{step}
│    check        │
└─────────────────┘
      │ complete
      ▼
   /dashboard
```

### Enhanced Sign-In Response
**Current `AuthResponse`:**
```python
class AuthResponse(BaseModel):
    user_id: str
    token: str
    message: str
```

**Required `AuthResponseEnhanced`:**
```python
class AuthResponseEnhanced(BaseModel):
    user_id: str
    token: str
    message: str
    # User State
    subscription_tier: str      # 'pending', 'talent', 'star', 'legend'
    account_status: str         # 'active', 'inactive'
    onboarding_status: str      # See values above
    name: str
    # Milestone Check
    pending_milestone: Optional[str]  # 'first_payment', '1000_streams', etc.
    milestone_video_url: Optional[str]  # S3 presigned URL if milestone pending
```

### Files to Modify
- [ ] `backend/models/schemas.py` - Add `AuthResponseEnhanced`
- [ ] `backend/routes/auth.py` - Return enhanced response
- [ ] `frontend/src/app/auth/signin/page.tsx` - Smart routing logic
- [ ] `frontend/src/middleware.ts` - Check subscription status

---

## MILESTONE SYSTEM

### S3 Bucket Structure
```
s3://noisemakerpromobydoowopp/Milestones/
├── milestone_first_payment/
│   └── milestone_first_payment.mov
├── milestone_1000_streams/
│   └── (future)
├── milestone_10000_streams/
│   └── (future)
└── ...
```

### Milestone Types
| Milestone | Trigger | Video Location | One-Time? |
|-----------|---------|----------------|-----------|
| `first_payment` | Stripe payment success | `Milestones/milestone_first_payment/milestone_first_payment.mov` | Yes |

### Required Milestone Tracking Fields
**In `noisemaker-users`:**
```python
'milestones': {
    'first_payment': {
        'achieved_at': '2025-01-15T10:30:00Z',
        'video_played': True,
        'video_played_at': '2025-01-15T10:31:00Z'
    },
    '1000_streams': {
        'achieved_at': None,
        'video_played': False,
        'video_played_at': None
    }
    # ... more milestones
}
```

### Milestone Flow
```
1. User completes Stripe payment
   │
   ▼
2. Backend: POST /api/payment/confirm
   - Updates subscription_tier
   - Sets milestone.first_payment.achieved_at = now()
   - Returns { pending_milestone: 'first_payment', milestone_video_url: presigned_url }
   │
   ▼
3. Frontend: /payment/success
   - Receives pending_milestone
   - Redirects to /milestone/first_payment?video_url=...
   │
   ▼
4. Frontend: /milestone/[type]/page.tsx
   - Plays video from S3 (presigned URL)
   - On video end: POST /api/user/{id}/milestone/{type}/complete
   - Backend sets milestone.first_payment.video_played = true
   - Redirects to /onboarding/select-platforms
```

### Files to Create/Modify
- [ ] `frontend/src/app/milestone/[type]/page.tsx` - Milestone video player page
- [ ] `backend/routes/auth.py` - Check pending milestones on sign-in
- [ ] `backend/routes/payment.py` - Set first_payment milestone after Stripe success
- [ ] `backend/routes/user.py` - Add `POST /api/user/{id}/milestone/{type}/complete`
- [ ] `backend/data/user_manager.py` - Add milestone tracking methods

---

## COST OPTIMIZATION

### Immediate Savings: $1,000-3,000+/month

| Issue | Location | Cost | Fix |
|-------|----------|------|-----|
| Full table scan | `user_manager.py:859` | $500-2000 | Use GSI |
| Daily Spotify polling | `daily_processor.py:270` | 300 API calls/day | Poll on-demand |
| Email lookup scan | `user_auth.py:189` | $100-300 | Use email-index GSI |
| Over-fetching dashboard | `dashboard.py:37` | $200-400 | Lightweight DTO |
| Inefficient post query | `dashboard.py:112` | $50-100 | Add Limit=1 |

### Data Collection to Remove
| Field | Location | Reason |
|-------|----------|--------|
| `stream_count` | `song_manager.py:98` | Deprecated, replaced by popularity |
| `previous_stream_count` | `song_manager.py:99` | Never used |
| `average_daily_stream_count` | `song_manager.py:100` | Never displayed |
| `fire_mode_triggered` | `song_manager.py:114` | Never checked |
| `fire_mode_entered_at` | `song_manager.py:113` | Duplicate of start_date |

### Spotify API Calls to Eliminate
| Call | Location | Current Frequency | Should Be |
|------|----------|-------------------|-----------|
| `poll_track_popularity` | `daily_processor.py:287` | Every day for all songs | On-demand only |
| Weekly baseline recalc | `weekly_baseline_recalculator.py:69` | Every week for all users | On baseline request |

---

## DATA FLOW GAPS

### Gap 1: Onboarding Progress Not Persisted
**Current:** Uses localStorage (`selected_platforms`)
**Required:** Server-side `onboarding_status` field

### Gap 2: Baseline Status Not Exposed
**Current:** Calculated but not returned to frontend
**Required:** `GET /api/user/{id}/baseline-status` endpoint

### Gap 3: Platform Connection Not Verified Before Songs
**Current:** User can add songs without connected platforms
**Required:** Guard check in `/onboarding/add-songs`

### Gap 4: Fire Mode Activation Not Visible
**Current:** Activated silently in background
**Required:** Dashboard badge + notification

### Gap 5: Milestone Progress Not Shown
**Current:** No endpoint returns milestone data
**Required:** `GET /api/user/{id}/milestones` endpoint

---

## FUTURE ENHANCEMENTS

### Phase 2: Dashboard Stats
- [ ] Show Fire Mode status with badge
- [ ] Display milestone progress bars
- [ ] Show platform posting status

### Phase 3: Notifications
- [ ] Fire Mode activation push notification
- [ ] Milestone achieved notification
- [ ] Weekly performance summary email

### Phase 4: Analytics
- [ ] Replace daily polling with webhook-based updates
- [ ] Implement caching layer for frequently accessed data
- [ ] Add CloudWatch metrics for cost monitoring

---

## IMPLEMENTATION ORDER

### Sprint 1: Foundation (This Week)
1. Add `onboarding_status` field to users table
2. Fix table scan in `get_all_active_users()`
3. Fix email lookup to use GSI
4. Enhance sign-in response with user state

### Sprint 2: Smart Routing (Next Week)
1. Implement milestone tracking fields
2. Create milestone video page
3. Implement smart sign-in routing
4. Update middleware for subscription checks

### Sprint 3: Cost Optimization (Week 3)
1. Remove deprecated data fields
2. Eliminate unnecessary Spotify polling
3. Add GSI for scheduled posts queries
4. Create lightweight DTOs for dashboard

### Sprint 4: Polish (Week 4)
1. Add Fire Mode UI indicators
2. Create baseline status endpoint
3. Add platform connection guard
4. Expose milestone progress

---

## NOTES

### AWS Resources
- **S3 Bucket:** `noisemakerpromobydoowopp`
- **Milestone Videos:** `Milestones/milestone_{type}/milestone_{type}.mov`
- **Region:** us-east-2

### Milestone Video Playback Rules
1. Each milestone video plays **exactly once** per user
2. Video must complete before redirect (track with `video_played` flag)
3. Use S3 presigned URLs (expire in 1 hour) for secure access
4. If video fails to load, allow skip after 5 seconds

### Sign-In Redirect Priority
1. Account status check (inactive → error page)
2. Subscription tier check (pending → pricing)
3. Milestone check (pending → milestone video)
4. Onboarding check (incomplete → onboarding step)
5. Dashboard (all complete)

---

*This document should be updated as systems are implemented and new requirements emerge.*
