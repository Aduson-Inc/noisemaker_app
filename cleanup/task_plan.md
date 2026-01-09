# Task Plan: NOiSEMaKER Onboarding Cleanup

## Goal
Systematically audit, document, and fix the first 3 pages of the onboarding flow.

## Page Flow (Confirmed by Dre)
1. **Landing Page** → `frontend/src/app/page-genz.tsx`
2. **Pricing Page** → `frontend/src/app/pricing/pricing-v2.tsx`
3. **Stripe Payment Success** → `frontend/src/app/payment/success/page.tsx`

## Phases
- [x] Phase 1: Create tracking files ✓
- [x] Phase 2: Map Landing Page (`page-genz.tsx`) ✓
- [x] Phase 3: Deep dive Pricing Page - data collection, backend endpoints ✓
- [x] Phase 4: Verify DynamoDB tables via AWS CLI ✓ (26 tables found)
- [x] Phase 5: Map Stripe Payment flow ✓
- [x] Phase 6: Security audit (route protection) ✓
- [ ] Phase 7: Document all findings, update CLAUDE.md - PENDING

## Rubric (Must Answer YES to All)
- [x] Have I identified all backend ↔ frontend entry points? ✓
- [x] Have I confirmed with Dre all data collected and where stored? ✓
- [ ] Are pages secure? (Can't access page 3 before completing 1 & 2) - PENDING
- [ ] Is the user experience smooth and safe? - PENDING TESTING

## Constraints
- Python 3.12 only
- Email signup only (OAuth deferred)
- No file changes without explicit approval
- Verify everything against actual code (docs ~60-70% trustworthy)

## Decisions Made
- Spotify artist fields ARE correct and needed
- `name` and `spotify_artist_name` redundancy - consider cleanup
- Users always referred to by artist name, not real name
- Token storage: Both localStorage + cookie is OK for dev/prod compatibility
- Rate limiting on validate-artist: Needs more protection (CAPTCHA)
- Payment confirm endpoint: Current design is secure (Stripe metadata)

## Key Findings
- **DynamoDB Tables:** 26 (not 23 or 24 as docs claim)
- **Backend Routers:** 7 (not 6 as CLAUDE.md claims)
- **Redundancy:** `name` = `spotify_artist_name` (same value stored twice)

## Errors Encountered
- (none yet)

## Status
**Currently in Phase 6** - Need to audit route protection and test flow locally
