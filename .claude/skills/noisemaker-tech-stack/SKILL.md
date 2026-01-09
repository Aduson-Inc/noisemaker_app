# NOiSEMaKER Tech Stack Skill

## Description
Enforces the locked technology stack for NOiSEMaKER. Prevents unauthorized version changes and ensures all code generation uses correct versions.

## LOCKED VERSIONS (December 21, 2025)

### Frontend
| Package | Version | Status |
|---------|---------|--------|
| Next.js | 15.5.9 | LOCKED |
| React | 19.2.3 | LOCKED |
| React DOM | 19.2.3 | LOCKED |
| TypeScript | 5.9.3 | LOCKED |
| Tailwind CSS | 4.1.18 | LOCKED |
| next-auth | 4.24.13 | LOCKED |

### Backend
| Package | Version | Status |
|---------|---------|--------|
| Python | 3.12 | LOCKED |
| FastAPI | Latest | LOCKED |
| Uvicorn | Latest | LOCKED |
| boto3 | Latest | LOCKED |

### Infrastructure
| Service | Details |
|---------|---------|
| Region | us-east-2 (Ohio) |
| Frontend Hosting | AWS Amplify |
| Backend Hosting | AWS Elastic Beanstalk |
| Database | DynamoDB (24 tables) |
| File Storage | S3 |
| Secrets | AWS Parameter Store |

## RULES

### NEVER DO (without explicit approval from Tre):
- Upgrade or downgrade Next.js version
- Upgrade or downgrade React version
- Change Tailwind CSS version
- Switch from FastAPI to another framework
- Change AWS region
- Add new database technologies
- Switch hosting providers

### ALWAYS DO:
- Use exact versions specified above
- Check package.json before suggesting dependency changes
- Verify compatibility before adding new packages
- Document any new dependencies in TECH_STACK.md

## Package.json Reference

Frontend dependencies should match:
```json
{
  "dependencies": {
    "next": "15.5.9",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "next-auth": "4.24.13"
  },
  "devDependencies": {
    "typescript": "5.9.3",
    "tailwindcss": "4.1.18",
    "@types/react": "^19",
    "@types/react-dom": "^19"
  }
}
```

## Validation Commands

Check current versions:
```bash
cd ~/projects/frontend && npm list next react tailwindcss typescript --depth=0
```

## When This Skill Applies
- Any code generation for frontend or backend
- Package installation suggestions
- Infrastructure recommendations
- Migration discussions
