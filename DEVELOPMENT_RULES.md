# NOISEMAKER Development Rules

## NON-NEGOTIABLE RULES

### 1. No Assumptions
- If you don't know, ASK
- Never guess paths, URLs, or configurations
- Verify before acting

### 2. Show Before Execute
- State what you will do
- Wait for approval
- Then execute

### 3. One Step at a Time
- Complete one task fully before starting another
- Verify each step worked before proceeding

### 4. No Background Tasks
- Never run commands in background
- Never run unauthorized commands

---

## PRE-COMMIT CHECKLIST

Before EVERY commit:
□ Did I run npm install after changing package.json?
□ Is package-lock.json staged WITH package.json?
□ Did I test locally first? (npm run build)
□ Did I run git status to see exactly what's staged?
□ Do I know what every staged file does?

---

## DEPLOYMENT ORDER

**ALWAYS deploy in this order:**

1. **Backend FIRST** (if backend changes exist)
   - Push to GitHub
   - GitHub Actions deploys to Elastic Beanstalk
   - Wait for completion
   - Verify EB health is Green

2. **Frontend SECOND** (if frontend changes exist)
   - Push to GitHub
   - Amplify auto-builds
   - Wait for build to complete
   - Verify site loads correctly

3. **NEVER deploy both simultaneously**

---

## GIT WORKFLOW

### Before Committing Frontend:
```bash
cd ~/projects/frontend
npm install              # Always regenerate lock file
npm run build            # Test build locally FIRST
git status               # Check what's staged
git add package.json package-lock.json
git commit -m "message"
```

### Before Committing Backend:
```bash
cd ~/projects/backend
pip freeze > requirements.txt  # If dependencies changed
git status
git add .
git commit -m "message"
```

---

## EMERGENCY CONTACTS

- AWS Console: https://console.aws.amazon.com
- Amplify: https://us-east-2.console.aws.amazon.com/amplify/apps/dy72ta11223bp
- EB: https://us-east-2.console.aws.amazon.com/elasticbeanstalk
- GitHub Actions: https://github.com/tretretretretre/Noi/actions

---

**Last Updated:** December 2024
**Owner:** Tre / ADUSON Inc.
