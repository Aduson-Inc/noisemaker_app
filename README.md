# NOISEMAKER

music promotion platform for independent artists.

## Overview
Automates social media posting across 8 platforms with auto-generated content and Fire Mode viral detection.

## Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- React
- TypeScript
- Tailwind CSS


**Backend:**
- FastAPI (Python 3.12)
- DynamoDB (12 tables)


**Infrastructure:**
- Region: us-east-2 (Ohio)
- SSL: ACM wildcard certificate
- Authentication: JWT tokens
- Payment: Stripe (Test mode)

## Features

**Subscription Tiers:**
- Talent: $25/month
- Star: $40/month  
- Legend: $60/month

**Platform Integration:**
- 8 social platforms (Facebook, Instagram, Twitter/X, TikTok, YouTube, Reddit, Discord, Threads)
- Spotify integration (app-level credentials for track data)
- AI-powered content generation
- Fire Mode for high-performing tracks

## Project Structure
```
projects/
├── frontend/          # Next.js 15 application
├── backend/           # FastAPI Python backend
└── .git/             # Monorepo
```

## Authentication
- Email/password signup
- JWT session tokens
- No user-level Spotify OAuth (app uses its own credentials)


- Node: Latest LTS
- Python: 3.12
