# NOISEMAKER Project Handoff Document


---

## ⚠️ CRITICAL RULES FOR ALL AGENTS

1. **NEVER modify, edit, or delete ANY files without explicit approval**
2. **NEVER assume path names** — verify or ask
3. **NEVER create branches without permission**
4. **Show proposed changes BEFORE making them**
5. **One destructive action per confirmation** — don't bundle deletes
6. **If unsure, ASK — don't guess or lie**

---

## PROJECT OVERVIEW

### What is NOiSEMaKER?
Music promotion SaaS that automates social media posting across 8 platforms for indie artists with AI-powered content generation and Fire Mode viral detection.

### Subscription Tiers
| Tier | Price | Platform Limit |
|------|-------|----------------|
| Talent | $25/month | 2 platforms |
| Star | $40/month | 5 platforms |
| Legend | $60/month | 8 platforms |

---

## TECH STACK (LOCKED — NO UPGRADES WITHOUT AUTHORIZATION)

### Frontend
- **Framework:** Next.js 15
- **React:** 19.2.3
- **Styling:** Tailwind CSS + shadcn/ui
- **Hosting:** AWS Amplify (currently disabled)

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Hosting:** AWS Elastic Beanstalk (currently stopped)
- **Region:** us-east-2 (Ohio)

### Database & Storage
- **Database:** AWS DynamoDB (26 tables, all `noisemaker-*` prefix)
- **File Storage:** AWS S3
- **Secrets:** AWS Parameter Store (`/noisemaker/*`)

---

## ⚠️ INFRASTRUCTURE STATUS (Dec 31, 2025)

| Service | Status | Reason |
| DynamoDB | 🟢 RUNNING | Needed for local dev |
| S3 | 🟢 RUNNING | Needed for local dev |



### Local Development
```bash
# Frontend
cd ~/projects/frontend && npm run dev  # → localhost:3000

# Backend
cd ~/projects/backend && uvicorn main:app --reload  # → localhost:8000


---

## AWS CONFIGURATION

| Service | Resource | Details |
|---------|----------|---------|
| Account ID | 199689305330 | Region: us-east-2 |
| DynamoDB | noisemaker-* | 24 tables (PAY_PER_REQUEST) |
| Parameter Store | /noisemaker/* | All secrets |

### URLs (Production - Currently Offline)
- **Frontend:** https://noisemaker.doowopp.com
- **API:** https://api.noisemaker.doowopp.com

---

## BRAND GUIDELINES

### Color Palette (Gen Z Bold Theme)
| Name | Tailwind | Hex | Use |
|------|----------|-----|-----|
| Black | `black` | #000000 | Backgrounds |
| White | `white` | #FFFFFF | Text, borders |
| Fuchsia | `fuchsia-500` | #d946ef | Primary accent, CTAs, Star tier |
| Cyan | `cyan-400` | #22d3ee | Talent tier, highlights |
| Lime | `lime-400` | #a3e635 | Legend tier, success |
| Red | `red-500` | #ef4444 | Errors |
| Gray | `gray-400/500/600` | - | Muted text |

### Tier Colors
| Tier | Color | Tailwind |
|------|-------|----------|
| Talent | Cyan | `cyan-400` |
| Star | Fuchsia | `fuchsia-500` |
| Legend | Lime | `lime-400` |

### Typography
- **Font:** Anisette STD Bold (or system fallback)
- **Headings:** ALL CAPS, font-black, tight tracking

---

## CURRENT STATUS (Dec 31, 2025)

### Onboarding Flow - 85% Complete
```
ALL ONBOARDING NEED TO BE HARDENED AND TESTED LOCALLY 

1. Landing Page (/)                              ✅ DONE
2. Pricing Page (/pricing)                       ✅ DONE - Enhanced validation
3. Stripe Checkout                               ✅ DONE
4. Payment Success (/payment/success)            ✅ DONE
5. Milestone Video (/milestone/[type])           ✅ DONE
6. How It Works #1 (/onboarding/how-it-works)    ✅ DONE (placeholder content)
7. Platforms Page (/onboarding/platforms)         DONE - Unified select+connect
8. How It Works #2 (/onboarding/how-it-works-2)  DONE (placeholder content)
9. Add Songs Page (/onboarding/add-songs)        started (needs work and fixes)
10. Dashboard (/dashboard)                       started (barely started) 
11. Marketplace/Franks Garage Art                 Needs testing
```

### Meta OAuth Setup
- **Test App ID:** 875812625143370
- **Permissions:** All Instagram/Facebook permissions ready for testing
- **Credentials in Parameter Store:**
  - `/noisemaker/facebook_client_id`
  - `/noisemaker/facebook_client_secret`
  - `/noisemaker/threads_client_id`
  - `/noisemaker/threads_client_secret`

---

## SESSION: December 31, 2025

### ✅ COMPLETED

**Backend:**
| Change | File |
|--------|------|
| Email GSI query (replaces table scan) | `auth/user_auth.py` |
| GSI migration script | `scripts/add_email_gsi.py` |
| Updated table creation with GSI | `scripts/create_dynamodb_tables.py` |
| Rate limiting (10/min) on validate-artist | `routes/songs.py` |
| Enhanced SignUpRequest with Spotify fields | `models/schemas.py` |
| Secure cookie helper | `routes/auth.py` |

**Frontend:**
| Change | File |
|--------|------|
| Email regex validation | `pricing-v2.tsx` |
| Password confirmation field | `pricing-v2.tsx` |
| Password strength indicator | `pricing-v2.tsx` |

**Infrastructure:**
| Task | Status |
|------|--------|
| Removed deprecated /onboarding/select-platforms/ folder | ✅ |
| Meta OAuth test app configured | ✅ |
| EC2 stopped, Amplify disabled | ✅ |

### 🔴 MUST DO

| Priority | Task | Location |
|----------|------|----------|
| P0 | Run Email GSI migration | `python scripts/add_email_gsi.py` |
| P0 | Create Add Songs page | `/onboarding/add-songs` |
| P0 | Create Dashboard page | `/dashboard` |
| P1 | Fix race condition on duplicate email | `auth/user_auth.py` |
| P1 | Fix silent baseline init failure | `routes/auth.py` |
| P2 | Add real content to How It Works pages | Both pages |
| P2 | Add Terms & Privacy checkbox | pricing page |

### ⚠️ KNOWN ISSUES

| Priority | Issue | Location |
|----------|-------|----------|
| HIGH | Race condition on duplicate email signup | `auth/user_auth.py` |
| HIGH | Silent baseline init failure | `routes/auth.py` lines 182-185 |
| MEDIUM | S3 presigned URLs expire in 1 hour | milestone video flow |
| MEDIUM | Onboarding state transitions not validated | `data/user_manager.py` |
| LOW | No email verification | auth flow |

---

## QUICK COMMANDS
```bash
# Check AWS access
aws sts get-caller-identity

# List DynamoDB tables
aws dynamodb list-tables --region us-east-2 --query 'TableNames[?starts_with(@, `noisemaker-`)]'

# Check Parameter Store
aws ssm describe-parameters --region us-east-2 --query "Parameters[?starts_with(Name, '/noisemaker/')].Name"

# Frontend dev
cd ~/projects/frontend && npm run dev

# Backend dev
cd ~/projects/backend && uvicorn main:app --reload

# Git sync
cd ~/projects && git add -A && git status
```

---

**END OF HANDOFF**
