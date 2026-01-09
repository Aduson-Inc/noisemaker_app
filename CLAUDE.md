# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (Next.js 15)
```bash
cd frontend
npm run dev          # Dev server on port 3000
npm run build        # Production build
npm run lint         # ESLint check
```

### Backend (FastAPI Python 3.12)
```bash
cd backend
uvicorn main:app --reload                    # Local dev server
pytest tests/                                # Run test suite
eb deploy noisemaker-api-prod                # Deploy to AWS Elastic Beanstalk
```

## Architecture Overview

**Full-stack music promotion SaaS** - automates social media posting across 8 platforms (Instagram, Twitter/X, Facebook, YouTube, TikTok, Reddit, Discord, Threads) with AI-powered content generation.

### Frontend (`frontend/`)
- **App Router pattern**: Pages in `src/app/`, components in `src/components/`
- **Protected routes**: Middleware guards `/dashboard`, `/onboarding`, `/milestone`
- **API client** (`src/lib/api.ts`): Organized by domain - `authAPI`, `songsAPI`, `platformAPI`, `paymentAPI`, `dashboardAPI`, `marketplaceAPI`
- **Auth flow**: NextAuth for OAuth + custom JWT tokens stored in localStorage

### Backend (`backend/`)
- **6 routers**: `auth.py`, `platforms.py`, `dashboard.py`, `payment.py`, `marketplace.py`, `songs.py`
- **Data layer** (`data/`): DynamoDB with manager classes (`UserManager`, `SongManager`, `PlatformOAuthManager`)
- **Auth dependency**: `get_current_user_id` for protected endpoints
- **Spotify integration** (`spotify/`): App-level credentials, baseline tracking, fire mode detection

### Database & Infrastructure
- **DynamoDB**: 23 tables in us-east-2
- **Secrets**: AWS Parameter Store (SSM) for JWT, Stripe, OAuth credentials
- **Frontend deployment**: AWS Amplify (auto-deploys on push to main)
- **Backend deployment**: AWS Elastic Beanstalk (manual via `eb deploy`)
- **Domain**: noisemaker.doowopp.com (API at api.noisemaker.doowopp.com)

### Key Integration Patterns
- Backend returns `redirect_to` field to guide onboarding flow
- Stripe checkout sessions with confirmation redirect to `/payment/success`
- Platform OAuth handled per-platform with callback to `/api/oauth/{platform}/callback`

### OAuth Model - IMPORTANT
**Users do NOT need their own OAuth credentials.** NOiSEMaKER uses app-level OAuth credentials for all 8 platforms. Users simply grant permission for the app to post AI-generated content to their personal social media accounts during onboarding. The OAuth flow is:
1. User selects platforms during onboarding
2. User clicks "Connect" for each platform
3. User is redirected to platform's OAuth consent screen
4. User grants NOiSEMaKER permission to post on their behalf
5. App stores tokens to post content automatically

---

# NOISEMAKER Development Rules - MANDATORY

## ABSOLUTE RULES - VIOLATION = IMMEDIATE STOP

### 1. NO UNAUTHORIZED CHANGES
- ❌ NEVER upgrade package versions (Next.js, React, etc.)
- ❌ NEVER delete existing files without explicit approval
- ❌ NEVER commit without explicit approval
- ❌ NEVER run npm install/update without explicit approval
- ❌ NEVER modify files outside the scope of the current task

### 2. APPROVAL REQUIRED BEFORE ACTION
- State EXACTLY what you will do
- List EVERY file you will create/modify/delete
- Wait for explicit "yes" or "approved" before proceeding
- If unsure, ASK - do not assume

### 3. ONE TASK AT A TIME
- Complete current task fully before starting another
- Verify each change works before moving on
- Show your work after each step

### 4. TECH STACK - DO NOT CHANGE
- Next.js 15 (App Router)
- React 19.2.3
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- DO NOT add new dependencies without approval

## PROJECT STRUCTURE
```
~/projects/
├── frontend/          # Next.js 15 app
│   ├── src/app/       # Pages (App Router)
│   ├── src/components/# React components
│   └── public/        # Static assets
├── backend/           # FastAPI Python backend
```

## CURRENT DESIGN DIRECTION - GEN Z BOLD (V2)
**Official page variants: V2** (page.tsx exports from page-genz.tsx, pricing uses pricing-v2.tsx, onboarding uses platforms-v2.tsx)

- Gen Z Bold aesthetic with high contrast black/white backgrounds
- Full-width horizontal bands for tier/platform selection
- Magazine/editorial typography feel
- **Official V2 Tier Colors:**
  - Talent: cyan-400 (#22d3ee)
  - Star: fuchsia-500 (#d946ef)
  - Legend: lime-400 (#a3e635)
- Particle/waveform background effects (WaveformVisualizer, ParticleBackground)
- TikTok-native energy vibe


## GIT RULES
- NEVER commit without explicit approval
- NEVER push without explicit approval
- Always show `git status` before any git operation
- Always show `git diff` before committing

## WHEN IN DOUBT
ASK. Do not guess. Do not assume. Do not "help" by doing extra work.

## ⛔ DEPLOYMENT - DO NOT DEPLOY
Production infrastructure is INTENTIONALLY OFFLINE:
- EC2 Backend: STOPPED
- Amplify Auto-Build: DISABLED

DO NOT run:
- `eb deploy`
- `git push` to trigger Amplify

Test LOCALLY ONLY until explicitly told otherwise.
