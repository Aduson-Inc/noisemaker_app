# POST SCHEDULES - INTEGRATION TODO

**Status:** NOT YET IMPLEMENTED
**Priority:** HIGH
**Created:** December 15, 2025

---

## OVERVIEW

This document defines the exact post schedules for all platform/song combinations. These schedules must be integrated into the backend posting system.

---

## BUSINESS RULES

### 1. Post Frequency
- 1 post per platform per day
- 14 days = 1 scheduling cycle (repeats)

### 2. Song Allocation (3 Songs)
| Position | Stage | % of Posts |
|----------|-------|------------|
| A | UPCOMING (days 1-14) | 20% |
| B | LIVE (days 15-28) | 50% |
| C | TWILIGHT (days 29-42) | 30% |

### 3. Platform Variety Rule
**CRITICAL:** Every platform MUST post about ALL songs during the 2-week cycle. No platform should only post about one song.

### 4. Song Count Variations
| Songs | Behavior |
|-------|----------|
| 3 | Use A/B/C schedules below |
| 2 | 50/50 split, alternate platforms |
| 1 | 100% of posts to single song |

---

## 3 SONGS - SCHEDULES BY PLATFORM COUNT

### 8 PLATFORMS (112 posts) - LEGEND TIER

**Allocation:** A=22, B=56, C=34

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P6 | 3 | 7 | 4 | 14 |
| P7-P8 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|-----|----|----|----|----|----|----|----|----|
| MON | A | B | B | C | B | B | C | A |
| TUE | B | A | C | B | A | B | C | B |
| WED | C | B | A | B | B | C | A | B |
| THU | B | C | B | A | C | B | B | C |
| FRI | A | B | C | B | B | A | C | C |
| SAT | B | A | B | C | B | B | B | C |
| SUN | C | C | B | B | C | C | B | A |

#### WEEK 2
| Day | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|-----|----|----|----|----|----|----|----|----|
| MON | B | B | A | A | B | C | B | C |
| TUE | C | B | B | A | A | B | C | B |
| WED | B | C | A | B | B | A | B | C |
| THU | A | B | B | C | B | B | C | B |
| FRI | B | A | C | B | C | B | B | C |
| SAT | C | B | B | B | B | C | C | A |
| SUN | B | C | C | B | C | B | A | B |

---

### 7 PLATFORMS (98 posts)

**Allocation:** A=20, B=49, C=29

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P6 | 3 | 7 | 4 | 14 |
| P7 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 | P4 | P5 | P6 | P7 |
|-----|----|----|----|----|----|----|-----|
| MON | A | B | B | C | B | B | C |
| TUE | B | A | C | B | A | B | C |
| WED | C | B | A | B | B | C | B |
| THU | B | C | B | A | C | B | B |
| FRI | A | B | C | B | B | A | C |
| SAT | B | A | B | C | B | B | C |
| SUN | C | C | B | B | C | C | A |

#### WEEK 2
| Day | P1 | P2 | P3 | P4 | P5 | P6 | P7 |
|-----|----|----|----|----|----|----|-----|
| MON | B | B | A | A | B | C | B |
| TUE | C | B | B | A | A | B | C |
| WED | B | C | A | B | B | A | B |
| THU | A | B | B | C | B | B | C |
| FRI | B | A | C | B | C | B | B |
| SAT | C | B | B | B | B | C | C |
| SUN | B | C | C | B | C | B | A |

---

### 6 PLATFORMS (84 posts)

**Allocation:** A=17, B=42, C=25

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P5 | 3 | 7 | 4 | 14 |
| P6 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 | P4 | P5 | P6 |
|-----|----|----|----|----|----|----|
| MON | A | B | B | C | B | C |
| TUE | B | A | C | B | A | B |
| WED | C | B | A | B | B | C |
| THU | B | C | B | A | C | B |
| FRI | A | B | C | B | B | C |
| SAT | B | A | B | C | B | B |
| SUN | C | C | B | B | C | A |

#### WEEK 2
| Day | P1 | P2 | P3 | P4 | P5 | P6 |
|-----|----|----|----|----|----|----|
| MON | B | B | A | A | B | C |
| TUE | C | B | B | A | A | B |
| WED | B | C | A | B | B | C |
| THU | A | B | B | C | B | B |
| FRI | B | A | C | B | C | C |
| SAT | C | B | B | B | B | C |
| SUN | B | C | C | B | C | A |

---

### 5 PLATFORMS (70 posts) - STAR TIER

**Allocation:** A=14, B=35, C=21

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P4 | 3 | 7 | 4 | 14 |
| P5 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 | P4 | P5 |
|-----|----|----|----|----|-----|
| MON | A | B | B | C | B |
| TUE | B | A | B | B | C |
| WED | B | B | A | B | C |
| THU | C | B | B | A | B |
| FRI | B | C | B | B | A |
| SAT | C | B | C | B | B |
| SUN | B | C | A | C | B |

#### WEEK 2
| Day | P1 | P2 | P3 | P4 | P5 |
|-----|----|----|----|----|-----|
| MON | A | B | B | B | C |
| TUE | B | A | C | B | B |
| WED | B | B | B | C | C |
| THU | C | B | A | B | B |
| FRI | A | A | B | B | C |
| SAT | A | B | C | B | B |
| SUN | C | B | B | C | A |

---

### 4 PLATFORMS (56 posts)

**Allocation:** A=11, B=28, C=17

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P3 | 3 | 7 | 4 | 14 |
| P4 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 | P4 |
|-----|----|----|----|----|
| MON | A | B | C | B |
| TUE | B | A | B | C |
| WED | B | B | A | C |
| THU | C | B | B | B |
| FRI | B | C | B | A |
| SAT | C | B | B | B |
| SUN | B | C | A | C |

#### WEEK 2
| Day | P1 | P2 | P3 | P4 |
|-----|----|----|----|----|
| MON | A | B | B | C |
| TUE | B | A | C | B |
| WED | B | B | B | C |
| THU | C | B | A | B |
| FRI | B | C | B | B |
| SAT | A | B | C | C |
| SUN | C | B | B | A |

---

### 3 PLATFORMS (42 posts)

**Allocation:** A=8, B=21, C=13

#### Per Platform Distribution
| Platform | A | B | C | Total |
|----------|---|---|---|-------|
| P1-P2 | 3 | 7 | 4 | 14 |
| P3 | 2 | 7 | 5 | 14 |

#### WEEK 1
| Day | P1 | P2 | P3 |
|-----|----|----|-----|
| MON | A | B | C |
| TUE | B | A | B |
| WED | B | B | C |
| THU | C | B | B |
| FRI | B | C | A |
| SAT | C | B | B |
| SUN | B | C | C |

#### WEEK 2
| Day | P1 | P2 | P3 |
|-----|----|----|-----|
| MON | A | B | B |
| TUE | B | A | C |
| WED | B | B | C |
| THU | C | B | B |
| FRI | B | C | B |
| SAT | A | B | C |
| SUN | C | B | A |

---

### 2 PLATFORMS (28 posts) - TALENT TIER

**Allocation:** A=5, B=14, C=9

#### WEEK 1
| Day | P1 | P2 |
|-----|----|----|
| MON | A | C |
| TUE | B | C |
| WED | B | B |
| THU | B | B |
| FRI | C | B |
| SAT | C | B |
| SUN | C | A |

#### WEEK 2
| Day | P1 | P2 |
|-----|----|----|
| MON | A | A |
| TUE | C | B |
| WED | C | B |
| THU | B | B |
| FRI | B | C |
| SAT | B | C |
| SUN | B | A |

---

## 2 SONGS - ALL PLATFORMS

### Rule: 50/50 Split with Platform Alternation

| Platforms | Posts | Each Song |
|-----------|-------|-----------|
| 8 | 112 | 56 |
| 7 | 98 | 49 |
| 6 | 84 | 42 |
| 5 | 70 | 35 |
| 4 | 56 | 28 |
| 3 | 42 | 21 |
| 2 | 28 | 14 |

### Pattern: Checkerboard Alternation
```
Day 1: P1=X, P2=Y, P3=X, P4=Y...
Day 2: P1=Y, P2=X, P3=Y, P4=X...
Day 3: P1=X, P2=Y, P3=X, P4=Y...
(repeat)
```

---

## 1 SONG - ALL PLATFORMS

### Rule: 100% of Posts

| Platforms | Posts | Song Gets |
|-----------|-------|-----------|
| 8 | 112 | 112 |
| 7 | 98 | 98 |
| 6 | 84 | 84 |
| 5 | 70 | 70 |
| 4 | 56 | 56 |
| 3 | 42 | 42 |
| 2 | 28 | 28 |

---

## FIRE MODE OVERRIDE

When a song enters Fire Mode, the allocation changes:

### Normal → Fire Mode
| Stage | Normal | Fire Mode Active |
|-------|--------|------------------|
| A (UPCOMING) | 20% | 10% |
| B (LIVE) | 50% | 20% |
| C (TWILIGHT) | 30% | 0% |
| **FIRE SONG** | - | **70%** |

**TODO:** Create separate Fire Mode schedule tables for each platform count.

---

## EXTENDED PROMOTION ($10/month add-on)

### Eligibility
- Song had Fire Mode active at ANY point during 42-day cycle
- User opts in after song completes day 42

### Schedule
- 1 post every 3 days
- Rotates through user's connected platforms
- Does NOT count toward 3-song limit (can be 4th song)

### Example Rotation (5 platforms)
```
Day 1: P1
Day 4: P2
Day 7: P3
Day 10: P4
Day 13: P5
Day 16: P1 (repeat)
```

---

## INTEGRATION TODO

### Phase 1: Data Model
- [ ] Add `schedule_position` field to songs (A, B, or C)
- [ ] Add `schedule_day` tracker (1-14, resets each cycle)
- [ ] Store user's platform order (P1-P8 mapping to actual platforms)

### Phase 2: Schedule Engine
- [ ] Create `backend/scheduling/post_scheduler.py`
- [ ] Load correct schedule based on platform count + song count
- [ ] Determine daily posts from schedule tables
- [ ] Handle Fire Mode override

### Phase 3: Database Tables
- [ ] `noisemaker-scheduled-posts` - queue of upcoming posts
- [ ] `noisemaker-posting-history` - completed posts

### Phase 4: Cron Job
- [ ] Daily scheduler runs at midnight user timezone
- [ ] Creates posts for the day based on schedule
- [ ] Handles timezone differences across users

### Phase 5: Fire Mode Integration
- [ ] Create Fire Mode schedule tables
- [ ] Override normal schedule when Fire Mode active
- [ ] Track `fire_mode_history` (NEVER clear on retire)

### Phase 6: Extended Promotion
- [ ] Add `extended_promotion_active` flag to songs
- [ ] Add `extended_promotion_last_post` timestamp
- [ ] Calculate 3-day rotation separately from main schedule
- [ ] Stripe integration for $10/month billing

---

## QUICK REFERENCE TABLE

| Platforms | Posts/2wk | A (20%) | B (50%) | C (30%) |
|-----------|-----------|---------|---------|---------|
| 8 | 112 | 22 | 56 | 34 |
| 7 | 98 | 20 | 49 | 29 |
| 6 | 84 | 17 | 42 | 25 |
| 5 | 70 | 14 | 35 | 21 |
| 4 | 56 | 11 | 28 | 17 |
| 3 | 42 | 8 | 21 | 13 |
| 2 | 28 | 5 | 14 | 9 |

---

## FILE LOCATIONS

After integration, schedules will be in:
- `backend/scheduling/schedules/` - JSON schedule files
- `backend/scheduling/post_scheduler.py` - Main scheduler logic
- `backend/scheduling/fire_mode_scheduler.py` - Fire Mode overrides

---

**Document Version:** 1.0
**Last Updated:** December 15, 2025
**Author:** Development Team