# NOiSEMaKER Documentation Sync Skill

## Description
Ensures documentation stays synchronized with actual code and infrastructure. Triggers documentation updates when relevant changes are made.

---

## DOCUMENTATION FILES

### Primary Docs (in /docs/)
| File | Purpose | Update When |
|------|---------|-------------|
| TECH_STACK.md | Technology versions | Package versions change |
| DYNAMODB_TABLES.md | Database schema | Tables added/modified |
| NAMING_INVENTORY.md | AWS resource names | Any AWS resource changes |
| POST_SCHEDULES_TODO.md | Posting logic specs | Scheduling logic changes |
| SYSTEMS_TODO.md | System integrations | Backend flow changes |

### Root Docs
| File | Purpose | Update When |
|------|---------|-------------|
| README.md | Project overview | Major features added |
| HANDOFF.md | Current state summary | After any work session |
| DEVELOPMENT_RULES.md | Dev guidelines | Rules change |
| CLAUDE.md | AI agent instructions | Agent behavior rules change |

---

## SYNC TRIGGERS

### After modifying DynamoDB code:
- Update `docs/DYNAMODB_TABLES.md` with any schema changes
- Update `docs/NAMING_INVENTORY.md` if tables added/removed
- Verify table names use `noisemaker-` prefix

### After modifying S3 code:
- Update `docs/NAMING_INVENTORY.md` with new paths
- Document new folder structures
- Verify bucket name is `noisemakerpromobydoowopp`

### After modifying package.json or requirements.txt:
- Update `docs/TECH_STACK.md` with new versions
- Update root `CLAUDE.md` if versions are locked

### After modifying API routes:
- Update `docs/NAMING_INVENTORY.md` endpoints section
- Update `backend/README_API.md` if it exists
- Document new request/response schemas

### After modifying Parameter Store references:
- Update `docs/NAMING_INVENTORY.md` parameters section
- Verify paths use `/noisemaker/` prefix

### After any work session:
- Update `HANDOFF.md` with current state
- Note what was completed and what's pending

---

## VERIFICATION COMMANDS

### Check DynamoDB matches docs:
```bash
aws dynamodb list-tables --region us-east-2 --output table
```

### Check S3 matches docs:
```bash
aws s3 ls s3://noisemakerpromobydoowopp/ --recursive
```

### Check Parameter Store matches docs:
```bash
aws ssm describe-parameters --region us-east-2 --query "Parameters[].Name" --output text | tr '\t' '\n' | sort
```

### Check package versions match docs:
```bash
cd ~/projects/frontend && npm list next react tailwindcss typescript --depth=0
```

---

## DOC UPDATE FORMAT

When updating documentation, include a header showing last verification:
```markdown
# Document Title

**Last Verified:** December 21, 2025
**Verified By:** [human/agent name]
**Method:** [AWS CLI / Code inspection / Manual test]

---
```

---

## INCONSISTENCY PROTOCOL

If you find docs that don't match reality:

1. **DO NOT assume the doc is correct**
2. **DO NOT assume the code is correct**
3. Ask: "I found an inconsistency between [doc] and [reality]. Which is the source of truth?"
4. Wait for clarification before making changes
5. Update the incorrect source once confirmed

### Common Inconsistencies to Watch:
- Table names (`spotify-promo-*` vs `noisemaker-*`)
- Package versions (docs say X, package.json says Y)
- API endpoints (docs list endpoint that doesn't exist)
- S3 paths (code references path that doesn't exist)
- Parameter paths (`/spotify-promo/` vs `/noisemaker/`)

---

## DOCUMENTATION STANDARDS

### Use Present Tense
```markdown
# GOOD
The system uses DynamoDB for storage.

# BAD
The system will use DynamoDB for storage.
```

### Be Specific with Versions
```markdown
# GOOD
Next.js 15.5.9

# BAD
Next.js 15.x
Latest Next.js
```

### Include Verification Method
```markdown
# GOOD
| noisemaker-users | ✅ Verified via AWS CLI |

# BAD
| noisemaker-users | Created |
```

### Mark Uncertain Information
```markdown
# GOOD
| Feature X | ⚠️ UNVERIFIED - needs testing |

# BAD
| Feature X | Working |
```

---

## HANDOFF.md TEMPLATE

After each work session, update HANDOFF.md:
```markdown
# NOiSEMaKER Handoff

**Last Updated:** [DATE]
**Updated By:** [NAME/AGENT]

## Session Summary
[2-3 sentences on what was accomplished]

## Completed This Session
- [x] Task 1
- [x] Task 2

## In Progress
- [ ] Task 3 (blocked by X)

## Next Steps
1. Priority task
2. Secondary task

## Known Issues
- Issue description (file:line if applicable)

## Files Modified
- path/to/file.ts - description of change
```
