# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (Next.js 15 — run from `frontend/`)
```bash
cd frontend
npm install          # install dependencies
npm run dev          # dev server on localhost:3000
npm run build        # production build
npm run lint         # ESLint
```

### Backend (FastAPI — run from `backend/`)
```bash
pip install fastapi uvicorn boto3 spotipy pydantic slowapi requests pillow huggingface_hub
python -m uvicorn main:app --reload --port 8000   # dev server on localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Database Setup Scripts
```bash
python backend/scripts/create_dynamodb_tables.py   # initialize DynamoDB tables
python backend/scripts/create_oauth_tables.py      # create OAuth tables
python backend/scripts/create_test_user.py         # generate a test user
```

### OAuth Tests (manual, per-platform)
```bash
python backend/scripts/oauth_tests/test_twitter.py
python backend/scripts/oauth_tests/test_all_platforms.py
```

### AWS Credentials
Both frontend and backend expect AWS credentials via `~/.aws/credentials` or `AWS_PROFILE=noisemaker-dev`. The frontend loads `JWT_SECRET` from AWS SSM Parameter Store at build time (`next.config.mjs`).

## Architecture

**Stack:** Python 3.12 FastAPI backend + TypeScript Next.js 15 (React 19) frontend, deployed on AWS (DynamoDB, Lambda, S3, SSM Parameter Store, EventBridge).

### Backend (`backend/`)
- **`main.py`** — FastAPI app init, CORS, route registration
- **`routes/`** — API routers: `auth`, `songs`, `platforms`, `dashboard`, `payment`, `frank_art`, `templates`
- **`data/`** — DynamoDB client (`dynamodb_client.py`), user/song managers, OAuth implementations per platform (`data/oauth/`)
- **`content/`** — Content generation pipeline: `model_router.py` routes to `caption_generator.py` (Grok AI primary, template fallback), `image_processor.py` (album art color extraction), `asset_pipeline.py`, `rag_pipeline.py` (Last.fm/Spotify context), `multi_platform_poster.py`
- **`scheduler/`** — `daily_orchestrator.py` (Lambda entry point, 9 PM UTC trigger), `schedule_engine.py` + `schedule_grids.py` (pre-calculated 14-day grid lookup by platform count × song count — no algorithm, pure lookup), `post_dispatcher.py`
- **`marketplace/`** — Frank's Garage AI artwork: SDXL via Hugging Face, daily generation, S3 storage (`noisemakerpromobydoowopp` bucket)
- **`auth/`** — JWT validation, password hashing, AWS SSM environment loading
- **`middleware/auth.py`** — `get_current_user_id()` dependency injection for routes

### Frontend (`frontend/src/`)
- **`app/`** — Next.js App Router: landing pages, `auth/`, `onboarding/` (multi-step), `dashboard/`, `pricing/`, `payment/`, `milestone/`
- **`components/`** — Shadcn UI (`components/ui/`), effects/animations, domain components (SongCard, PricingCard, PostReviewModal, etc.)
- **`middleware.ts`** — JWT auth guard for protected routes

### Deployment
- **`backend/template.yaml`** — AWS SAM config for Lambda deployment
- Lambda functions triggered daily at 9 PM UTC via EventBridge

## Key Domain Concepts

### Song Lifecycle (42-Day Conveyor Belt)
- **Position A (Day 1–14):** Upcoming — 20% of posts
- **Position B (Day 15–28):** Live — 50% of posts
- **Position C (Day 29–42):** Twilight — 30% of posts
- **Day 43+:** Retired (or Extended Promo at $10/month)
- **Slot Gate Rule:** A new song can only enter Position A when the current A-song reaches day 15.

### Platform Support (8 Platforms)
Twitter/X, Instagram, TikTok, YouTube, Facebook, Reddit, Discord, Threads. Each has its own OAuth implementation in `backend/data/oauth/`. Platforms are numbered P1–P8 by connection order.

### Authentication Flow
1. Frontend: NextAuth (Google/Facebook OAuth) creates session
2. Token exchange: NextAuth session → backend JWT via `/auth/exchange-token`
3. Backend: JWT validated by `middleware/auth.py`, user ID injected into route handlers

### Subscription Tiers
`pending` (onboarding incomplete), `talent` (starter), `star` (pro), `legend` (premium)

### Content Reuse
Generated content tracks `posted_to` (list of platforms already posted to). Content is reusable across platforms within a cycle. When all connected platforms have used the content, it regenerates.

## DynamoDB Tables
`noisemaker-users`, `noisemaker-songs`, `noisemaker-platform-connections`, `noisemaker-scheduled-posts`, `noisemaker-frank-art`, `noisemaker-templates`
