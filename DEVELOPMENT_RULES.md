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


### Before Committing Frontend:
```bash
C:\Users\tredev\Desktop\nm_mono\frontend
npm install              # Always regenerate lock file
npm run build            # Test build locally FIRST
git status               # Check what's staged
git add package.json package-lock.json
git commit -m "message"
```

### Before Committing Backend:
```bash
C:\Users\tredev\Desktop\nm_mono\backend
pip freeze > requirements.txt  # If dependencies changed
git status
git add .
git commit -m "message"
```

---


