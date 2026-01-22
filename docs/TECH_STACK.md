# NOiSEMaKER Tech Stack

**Last Verified:** December 21, 2025
**Status:** LOCKED — No changes without Tre's authorization

---

## Frontend

| Technology | Version | Notes |
|------------|---------|-------|
| Next.js | 15.5.9 | App Router |
| React | 19.2.3 | |
| TypeScript | 5.9.3 | |
| Tailwind CSS | 4.1.18 | |
| Framer Motion | Latest | Animations |

**Hosting:** AWS Amplify
**Domain:** https://noisemaker.doowopp.com

---

## Backend

| Technology | Version | Notes |
|------------|---------|-------|
| FastAPI | Latest | Python web framework |
| Python | 3.12 | |
| Uvicorn | Latest | ASGI server |

**Hosting:** AWS Elastic Beanstalk (Single Instance)
**Environment:** noisemaker-api-prod
**Domain:** https://api.noisemaker.doowopp.com

---

## Database & Storage

| Service | Details |
|---------|---------|
| DynamoDB | 26 tables, `noisemaker-*` prefix |
| S3 | `noisemakerpromobydoowopp` bucket |
| Parameter Store | `/noisemaker/*` secrets |

**Region:** us-east-2 (Ohio)
**Billing:** PAY_PER_REQUEST (on-demand)

---

## Subscription Tiers

| Tier | Price | Platforms | Songs |
|------|-------|-----------|-------|
| Talent | $25/month | 2 | 3 |
| Star | $40/month | 5 | 3 |
| Legend | $60/month | 8 | 3 |

---

## Supported Platforms (8)

1. Instagram
2. Twitter/X
3. Facebook
4. TikTok
5. YouTube
6. Reddit
7. Discord
8. Threads

---

## AWS Resources

| Service | Resource Name |
| DynamoDB | 24 tables (`noisemaker-*`) |
| S3 | noisemakerpromobydoowopp |
| Parameter Store | `/noisemaker/*` (count TBD) |

---

## Version History

| Date | Change |
|------|--------|
| 2025-12-21 | Verified: Next.js 15.5.9, React 19.2.3, Tailwind 4.1.18, TS 5.9.3 |
| 2025-12-13 | Migrated all DynamoDB tables from `spotify-promo-*` to `noisemaker-*` |
