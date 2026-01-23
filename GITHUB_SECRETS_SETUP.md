# GitHub Secrets Setup Guide

**One-time setup (2 minutes)**

This guide will help you add your AWS credentials to GitHub so the automated deployment can work.

---

## Step 1: Get Your AWS Credentials

You already have AWS credentials configured locally (they're in `~/.aws/credentials`).

**Option A: Use existing credentials**
```bash
# View your current AWS credentials
cat ~/.aws/credentials
```

You'll see:
```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

**Option B: Create new IAM user (recommended for production)**
1. Go to AWS Console → IAM → Users → Add User
2. User name: `github-actions-frank-art`
3. Attach policies:
   - `AWSLambda_FullAccess`
   - `IAMReadOnlyAccess` (to read role ARN)
4. Create user → Download credentials

---

## Step 2: Add Secrets to GitHub

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/nm_mono`

2. Click **Settings** (top right)

3. In left sidebar, click **Secrets and variables** → **Actions**

4. Click **New repository secret**

5. Add first secret:
   - **Name:** `AWS_ACCESS_KEY_ID`
   - **Value:** Your AWS access key (starts with `AKIA...`)
   - Click **Add secret**

6. Click **New repository secret** again

7. Add second secret:
   - **Name:** `AWS_SECRET_ACCESS_KEY`
   - **Value:** Your AWS secret access key
   - Click **Add secret**

---

## Step 3: Verify Secrets

You should now see 2 secrets in the list:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**Security note:** GitHub encrypts these and never displays them after you save them.

---

## Step 4: Test the Workflow

Once secrets are added, the workflow will trigger automatically on your next `git push` to the `main` branch.

**To test immediately:**

```bash
# Make a small change (like adding a comment)
cd backend
echo "# GitHub Actions test" >> marketplace/artwork_analytics.py

# Commit and push
git add .
git commit -m "test: trigger GitHub Actions deployment"
git push origin main
```

**Monitor the deployment:**
1. Go to your GitHub repo
2. Click **Actions** tab (top)
3. You'll see the workflow running
4. Click on the run to see live logs
5. Deployment takes ~2-3 minutes

---

## Step 5: Confirm Success

After the workflow completes, verify:

```bash
# Check Lambda function was updated
aws lambda get-function --function-name frank-art-generator --region us-east-2 --query 'Configuration.LastModified'
```

You should see a recent timestamp.

---

## Troubleshooting

**Error: "User is not authorized to perform: lambda:UpdateFunctionCode"**
- Solution: Your AWS credentials need Lambda permissions
- Add `AWSLambda_FullAccess` policy to the IAM user

**Error: "ResourceNotFoundException: Function not found: frank-art-generator"**
- Solution: Lambda function doesn't exist yet
- We'll create it in the next step (initial deployment)

**Workflow doesn't trigger:**
- Check you pushed to the `main` branch
- Check the workflow file is in `.github/workflows/` directory
- Check GitHub Actions is enabled (Settings → Actions → General → Allow all actions)

---

## Security Best Practices

1. **Never commit credentials to Git**
   - AWS credentials should ONLY be in GitHub Secrets
   - Never in code, never in files

2. **Use separate IAM user for GitHub Actions**
   - Don't use your personal AWS credentials
   - Create dedicated user with minimal permissions

3. **Rotate credentials periodically**
   - Update secrets in GitHub when you rotate AWS keys

4. **Review deployment logs**
   - GitHub Actions logs show each deployment
   - Check for any errors or warnings

---

## What Happens After Setup

**Every time you push to main branch:**
1. GitHub Actions detects the push
2. Builds Lambda package automatically
3. Deploys to AWS Lambda
4. Lambda continues running at 9 PM UTC daily

**You never need to:**
- Manually create zip files
- Manually upload to Lambda
- Manually deploy anything

**Just:**
```bash
git add .
git commit -m "your changes"
git push
```

And it deploys automatically!

---

**Setup complete?** Move to next step: Initial Lambda deployment
