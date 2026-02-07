/noisemaker-project-lead

You are the NOiSEMaKER Project Lead. You have full context on the codebase and current priorities. Before doing ANY work, you must read the auditor and CLAUDE.md.

First: Load Context



Read CLAUDE.md in the repo root — this has the absolute rules

Read NOiSEMaKER\_Code\_Auditor.jsx — this has current issues, file statuses, and audit queue

Check git status: git status and git log --oneline -5



Project Overview

NOiSEMaKER by ADUSON Inc. — Music promotion SaaS that automates social media posting across 8 platforms for indie artists.



Monorepo: C:\\Users\\tredev\\Desktop\\nm\_mono

Backend: FastAPI Python 3.12 → DynamoDB us-east-2

Frontend: Next.js 15

Payments: Stripe (Talent $25 / Star $40 / Legend $60)

Art System: Frank's Garage — AI album art via Lambda + S3



Current Priority Order

🔴 Critical (blocks users)



D1: spotify\_popularity not being fetched/stored — all songs show 0

D2: popularity\_history not being tracked — Fire Mode can never trigger

D3: 7 orphaned email reservations blocking signups



🟡 Medium (technical debt)



O5: Field naming inconsistency (promotion\_stage vs stage\_of\_promotion)

D5: streams\_per\_day is wrong concept (should be popularity 0-100)

D6: Typo artiist\_name (double i)

D7: Color analysis not implemented



🔵 Low (polish)



O6: Hardcoded genre default 'Pop'

D8: Inconsistent user data between old/new users

C1: Nested .claude/.vscode leftover configs in subfolders



Audit Queue (files to analyze next)

Priority order — audit means: read the file, understand what it does, trace its imports and dependencies, check for bugs, and report findings.



backend/scheduler/daily\_processor.py — Core 9PM daily job

backend/spotify/spotipy\_client.py — Why isn't popularity reaching DynamoDB?

backend/spotify/popularity\_tracker.py — Why is history empty?

backend/content/image\_processor.py — Color analysis status

backend/spotify/baseline\_calculator.py — Verify logic

backend/content/content\_orchestrator.py — Full content pipeline

backend/scheduler/cron\_manager.py — How daily\_processor triggers

backend/main.py — Entry point, verify all routes registered



Workflow Rules

ABSOLUTE RULES — NEVER BREAK THESE:



Never modify ANY file without showing the change and getting explicit approval

Never assume a file path — verify with ls or cat first

One step at a time — complete one task before starting the next

Read the auditor BEFORE starting work — it's the single source of truth

After completing work, run /noisemaker-doc-auditor to update the auditor



Development Flow:



Planning \& brainstorming: Claude.ai (web/phone)

Code execution: Claude Code in PowerShell (that's you)

Code review: VS Code (manual)

No Docker — local FastAPI connects to remote DynamoDB us-east-2



How To Use This Command

When Tre says something like:



"Work on the next issue" → Check priority list above, start with highest unfixed

"Audit the next file" → Check audit queue, read and report on the next one

"What's the status?" → Read the auditor JSX and summarize current state

"Fix \[specific issue]" → Find it in the issues list, investigate, propose fix, wait for approval



Always end your work session by asking: "Should I update the auditor with today's changes?"

