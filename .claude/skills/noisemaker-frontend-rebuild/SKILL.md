# NOiSEMaKER Frontend Rebuild Skill

## Description
Tracks the systematic rebuild of the NOiSEMaKER frontend. Pages are built ONE AT A TIME.

**Last Updated:** December 26, 2025

---

## CURRENT PHASE: Phase 2 - Onboarding (85% Complete)

### Public Pages - ✅ COMPLETE
| Page | Route | Status |
|------|-------|--------|
| Landing | `/` | ✅ Done (page-genz.tsx) |
| Pricing | `/pricing` | ✅ Done (pricing-v2.tsx) |

### Payment Flow - ✅ COMPLETE
| Page | Route | Status |
|------|-------|--------|
| Payment Success | `/payment/success` | ✅ Done |
| Milestone Video | `/milestone/[type]` | ✅ Done |

### Onboarding Flow - 🔶 IN PROGRESS
| Page | Route | Status |
|------|-------|--------|
| How It Works #1 | `/onboarding/how-it-works` | ✅ Done (placeholder text) |
| Platform Selection | `/onboarding/platforms` | ✅ Done (platforms-v1-bands.tsx) |
| How It Works #2 | `/onboarding/how-it-works-2` | ✅ Done (placeholder text) |
| Add Songs | `/onboarding/add-songs` | 🔴 Needs Discussion |

### Dashboard - 🔴 NOT STARTED
| Page | Route | Status |
|------|-------|--------|
| Dashboard | `/dashboard` | 🔴 Not Started |

---

## DESIGN SYSTEM: Gen Z Bold

- **Background:** `bg-black`
- **Text:** `text-white`, `font-black`, `uppercase`
- **Tier Colors:**
  - Talent: `cyan-400`
  - Star: `fuchsia-500`
  - Legend: `lime-400`
- **Buttons:** Brutalist offset shadow effect
- **Cards:** Thick white borders, `-mt-10` label overlaps

---

## KEY FILES

### Landing Page
- `frontend/src/app/page-genz.tsx` (primary)
- `frontend/src/app/page.tsx` (entry)

### Pricing Page
- `frontend/src/app/pricing/pricing-v2.tsx` (primary)
- `frontend/src/app/pricing/page.tsx` (entry)

### Onboarding
- `frontend/src/app/onboarding/how-it-works/page.tsx`
- `frontend/src/app/onboarding/platforms/platforms-v1-bands.tsx`
- `frontend/src/app/onboarding/how-it-works-2/page.tsx`

### Types
- `frontend/src/types/index.ts`

### API Client
- `frontend/src/lib/api.ts`
