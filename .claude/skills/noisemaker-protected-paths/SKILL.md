# NOiSEMaKER Protected Paths Skill

## Description
Defines files and directories that require explicit approval before modification. Prevents accidental or unauthorized changes to critical infrastructure.

---

## PROTECTION LEVELS

### 🔴 CRITICAL - Never modify without Tre's explicit approval
These files control core infrastructure and authentication. Unauthorized changes can break the entire application.
```
# Package versions
frontend/package.json
frontend/package-lock.json
backend/requirements.txt

# Authentication
frontend/src/app/api/auth/[...nextauth]/route.ts
backend/auth/user_auth.py
backend/middleware/auth.py

# Database schemas
backend/scripts/create_dynamodb_tables.py
backend/data/dynamodb_client.py

# Environment/Config
frontend/next.config.js
frontend/tailwind.config.js
backend/main.py
.env*
*.env

# Infrastructure
amplify.yml
.ebextensions/*
Procfile

# Project rules
CLAUDE.md
.claude/*
```

### 🟡 HIGH - Requires confirmation before changes
Important files that affect multiple parts of the application.
```
# Shared types and schemas
frontend/src/types/*
backend/models/schemas.py

# API routes
backend/routes/*.py

# Core components
frontend/src/components/ui/*
frontend/src/lib/*

# Middleware
frontend/src/middleware.ts

# Documentation
docs/*.md
README.md
HANDOFF.md
DEVELOPMENT_RULES.md
```

### 🟢 STANDARD - Normal development workflow
Can be modified following coding standards.
```
# Page components
frontend/src/app/**/page.tsx

# Feature components
frontend/src/components/landing/*
frontend/src/components/dashboard/*

# Backend business logic
backend/content/*
backend/marketplace/*
backend/scheduler/*
backend/spotify/*

# Tests
backend/tests/*
frontend/**/*.test.ts
```

---

## BEFORE MODIFYING PROTECTED FILES

### For 🔴 CRITICAL files:
1. STOP - Do not proceed without approval
2. Explain what change is needed and why
3. Show the exact diff of proposed changes
4. Wait for explicit "yes" or "approved" from Tre
5. Only then make the change

### For 🟡 HIGH files:
1. Explain what change is needed
2. Confirm with user before proceeding
3. Make minimal, focused changes
4. Document what was changed

---

## SPECIFIC RULES

### package.json / requirements.txt
- NEVER add new dependencies without explaining why
- NEVER upgrade versions without approval
- NEVER remove dependencies without confirming they're unused
- Always run `npm list` or `pip freeze` to verify current state first

### Authentication files
- NEVER modify OAuth flows without understanding full impact
- NEVER change JWT/session handling without security review
- NEVER expose secrets or tokens in code

### Database files
- NEVER delete tables or indexes
- NEVER modify partition/sort keys on existing tables
- NEVER rename tables (this breaks all references)
- Always use `noisemaker-` prefix for any new tables

### CLAUDE.md and .claude/*
- These files control AI agent behavior
- Changes here affect all future AI interactions
- Only modify to fix errors or add new verified rules

---

## EMERGENCY OVERRIDES

If a critical bug requires immediate changes to protected files:

1. State clearly: "EMERGENCY: [description of critical issue]"
2. Explain the immediate risk if not fixed
3. Propose the minimal fix required
4. Get approval before proceeding
5. Document the emergency change in git commit

---

## AUDIT TRAIL

When modifying any 🔴 or 🟡 file, the git commit MUST include:
```
[PROTECTED] <type>: <description>

Approval: <how approval was given>
Reason: <why change was needed>
Impact: <what this affects>
```

Example:
```
[PROTECTED] fix: Update DynamoDB table reference in user_auth.py

Approval: Tre confirmed in chat
Reason: Old spotify-promo reference causing 500 errors
Impact: Fixes user login flow
```
