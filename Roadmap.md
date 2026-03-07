# NOiSEMaKER Development Roadmap & To-Do List

**Date:** March 6, 2026 | **Owner:** Tre (ADUSON Inc.) | **Version:** 1.0

## Current State

Both frontend (Next.js 15, localhost:3000) and backend (FastAPI, localhost:8000) are running locally with zero import errors. All route groups registered in Swagger UI. Repo cleaned and committed to GitHub (Aduson-Inc/noisemaker_app). Content pipeline refactor merged: model router, asset pipeline, template engine, RAG context, and video support modules all import cleanly.

## Phase 0: Repo Cleanup (Completed)

| Status | Task | Notes |
|--------|------|-------|
| **REVERTED** | CLAUDE.md removed from repo | Had wrong info: Spotify refs, wrong stage names, React 19 |
| **REVERTED** | .claude/launch.json removed | Claude Code config, not needed in repo |
| **REVERTED** | Backend spec .md removed from repo | Planning doc, saved to Desktop instead |
| **DONE** | staged_diff.txt / unstaged_diff.txt removed | Review artifacts, not code |
| **DONE** | Content pipeline refactor committed + pushed | 12 files, clean commit to main |

## Phase 1: Critical Fixes Before Testing

| Status | Task | Notes |
|--------|------|-------|
| **FIX** | rag_pipeline.py: Replace Spotify popularity references with Last.fm playcount/listeners | Line ~1660 area, build_caption_context() |
| **FIX** | routes/templates.py: ADMIN_USER_IDS is empty set | Add your user ID or implement role-based auth |
| **FIX** | routes/templates.py: depends on noisemaker-templates DynamoDB table | Table does not exist yet. Create it or add fallback |
| **FIX** | Frontend JWT_SECRET SSM loading in non-AWS terminal | Set $env:AWS_PROFILE = noisemaker-dev |
| **FIX** | Song upload 422 error (step 7 of onboarding) | Verify still exists after pipeline refactor |

[continue with remaining phases in same markdown table format]