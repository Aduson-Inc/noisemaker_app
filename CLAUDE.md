# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NOISEMAKER is a music promotion SaaS platform for independent artists. It automates social media posting across 8 platforms (Instagram, Twitter/X, Facebook, TikTok, YouTube, Reddit, Discord, Threads) with AI-generated content and Spotify-driven "Fire Mode" viral detection.

## Repository Structure

Monorepo with two main components:
- **frontend/** — Next.js 15 (App Router), TypeScript, React 19, Tailwind CSS, shadcn/ui
- **backend/** — FastAPI (Python 3.12), DynamoDB (26 tables, `noisemaker-*` prefix), AWS Lambda

Infrastructure is AWS-native: DynamoDB, S3 (`noisemakerpromobydoowopp`), Lambda, EventBridge, Parameter Store. Region: `us-east-2`.

## Commands

### Frontend
```bash
cd frontend
npm run dev          # Dev server on port 3000
npm run build        # Production build (run before committing)
npm run lint         # ESLint
```

### Backend
```bash
cd backend
pip install -r requirements.txt    # Install deps
python -m uvicorn main:app --reload  # Dev server on port 8000
```

### Database Setup
```bash
python backend/scripts/create_dynamodb_tables.py   # Create all DynamoDB tables
python backend/scripts/create_test_user.py          # Seed test user
```

### Lambda (Frank Art Generator)
Deployed via AWS SAM (`backend/template.yaml`) and GitHub Actions (`.github/workflows/deploy-frank-art.yml`). Triggered daily at 9 PM UTC by EventBridge.

## Architecture

```
Frontend (Next.js 15) → HTTP/REST → Backend (FastAPI)
                                        ↓
                              AWS (DynamoDB, S3, SSM)
                              Lambda (art generation)
                              Stripe (payments)
                              Spotify (track data)
```

- **Authentication:** JWT tokens. Backend routes in `backend/routes/auth.py`, frontend auth via NextAuth (`frontend/src/lib/auth-options.ts`), route protection in `frontend/src/middleware.ts`.
- **API client:** `frontend/src/lib/api.ts` (Axios) connects to backend at `NEXT_PUBLIC_API_URL`.
- **Data layer:** `backend/data/dynamodb_client.py` is the core DynamoDB client. Domain managers (`user_manager.py`, `song_manager.py`, `platform_oauth_manager.py`) handle specific tables.
- **Content pipeline:** `backend/content/content_orchestrator.py` coordinates caption generation, image processing, and multi-platform posting (`multi_platform_poster.py`).
- **Fire Mode:** `backend/spotify/fire_mode_analyzer.py` detects viral tracks using baselines from `baseline_calculator.py`.
- **Frank's Garage (marketplace):** AI art via HuggingFace SDXL in Lambda (`backend/marketplace/frank_art_generator.py`), managed by `frank_art_manager.py`.
- **Scheduling:** `backend/scheduler/daily_processor.py` runs daily post scheduling.

## Key Conventions

- **Secrets** live in AWS Parameter Store under `/noisemaker/*`, never in code.
- **Pydantic models** for all request/response schemas in `backend/models/schemas.py`.
- **TypeScript types** in `frontend/src/types/index.ts`.
- Always stage `package-lock.json` alongside `package.json` changes.
- Run `npm run build` locally before committing frontend changes.
- Subscription tiers: Talent ($25, 2 platforms), Star ($40, 5 platforms), Legend ($60, 8 platforms).

## Development Rules

### ABSOLUTE RULES — NEVER VIOLATE
1. NEVER modify files without showing the change and getting explicit approval first
2. NEVER assume file paths — verify with find/grep or ASK
3. NEVER create workarounds, temp copies, or new branches without permission
4. NEVER run commands that modify data without showing them first
5. ONE step at a time — pause and wait for confirmation between steps
6. If a command's output is needed before deciding next steps, STOP and wait

### Auditor Reference
Before ANY work on backend, frontend, database, or infrastructure, consult the NOiSEMaKER Auditor skill files in docs/skills/ for current documented state.

### Workflow Context
- Planning/brainstorming happens in Claude.ai — Claude Code receives specific tasks
- Do not freelance or expand scope beyond what was asked
- Questions over assumptions, always
