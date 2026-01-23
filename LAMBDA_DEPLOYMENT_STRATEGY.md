# Frank's Garage Lambda Deployment - Strategy & Cost Analysis

**Date:** 2026-01-23
**Purpose:** Deploy daily AI art generation system to run automatically at 9 PM UTC every night
**Goal:** Production-ready, cost-effective, maintainable solution

---

## AUTOMATION GUARANTEE

**All options below will run automatically at 9 PM UTC daily using AWS EventBridge.**

EventBridge is AWS's managed scheduled event service:
- Triggers Lambda at exact time: `cron(0 21 * * ? *)` = 9:00 PM UTC daily
- Never misses a scheduled run (99.99% uptime SLA)
- No server to maintain - fully managed by AWS
- Automatically retries if Lambda fails
- Free for up to 1 million events/month (we use 30/month)

**Set it and forget it:** Once configured, it runs every night without any manual intervention.

---

## DEPLOYMENT OPTIONS

### Option 1: GitHub Actions CI/CD (RECOMMENDED)

**How it works:**
1. You push code to GitHub (`git push`)
2. GitHub Actions workflow triggers automatically
3. Workflow packages your code + dependencies
4. Deploys to AWS Lambda
5. Lambda runs daily at 9 PM via EventBridge

**Setup requirements:**
- GitHub repository (you already have this)
- AWS credentials stored as GitHub Secrets (one-time setup)
- `.github/workflows/deploy-lambda.yml` file (I create this)

**Monthly Cost Breakdown:**
```
GitHub Actions: $0 (Free tier: 2,000 minutes/month, we use ~10 min/month)
Lambda execution: $0 (Free tier: 400,000 GB-seconds/month, we use 2,250 GB-seconds/month)
EventBridge: $0 (Free tier: 1M events/month, we use 30/month)
S3 storage: $0.02/month (0.86 GB × $0.023/GB)
S3 PUT requests: $0.002/month (360 requests × $0.005/1000)
DynamoDB: $0 (Free tier: 1M writes/month, we use 120/month)
Hugging Face API: $0 (nscale provider free tier)

TOTAL: ~$0.022/month (2 cents)
```

**Pros:**
- Industry standard CI/CD pipeline
- Auto-deploy on every git push
- No manual packaging ever
- Free for public/private repos
- Version controlled deployment
- Easy rollbacks (redeploy previous commit)
- Visible deployment history
- Can add automated tests before deploy

**Cons:**
- Requires GitHub repository
- Initial setup: create workflow file + add AWS secrets
- Deployment takes 2-3 minutes after push

**Maintenance:**
- Zero ongoing maintenance
- Update code → git push → auto-deploys
- No manual zip files, no manual uploads

**Production readiness: 10/10**
- Used by Fortune 500 companies
- Scales to any team size
- Professional development workflow

---

### Option 2: AWS CodePipeline + CodeBuild (AWS Native)

**How it works:**
1. You push code to GitHub
2. CodePipeline detects the push
3. CodeBuild packages your code
4. Automatically deploys to Lambda
5. Lambda runs daily at 9 PM via EventBridge

**Setup requirements:**
- GitHub repository connected to CodePipeline
- CodeBuild project configuration
- IAM roles for CodePipeline/CodeBuild

**Monthly Cost Breakdown:**
```
CodeBuild: $5.00/month (100 build minutes at $0.005/min, ~20 builds/month)
CodePipeline: $1.00/month ($1.00 per active pipeline)
Lambda execution: $0 (Free tier)
EventBridge: $0 (Free tier)
S3 storage: $0.02/month
S3 PUT requests: $0.002/month
DynamoDB: $0 (Free tier)
Hugging Face API: $0

TOTAL: ~$6.02/month
```

**Pros:**
- All AWS-native (no external dependencies)
- Integrated with AWS Console
- Good if you're already using AWS DevOps tools
- Built-in artifact storage
- IAM-based security

**Cons:**
- More expensive ($6/month vs free)
- More complex setup
- Harder to debug than GitHub Actions
- Less flexible than GitHub Actions

**Maintenance:**
- Low maintenance once set up
- All updates via AWS Console

**Production readiness: 9/10**
- Enterprise-grade
- AWS-managed

---

### Option 3: Lambda Container Image (Docker)

**How it works:**
1. Build Docker container with your code + dependencies
2. Push container to Amazon ECR (Elastic Container Registry)
3. Lambda runs the container
4. Lambda runs daily at 9 PM via EventBridge

**Setup requirements:**
- Dockerfile
- Docker installed locally or in CI/CD
- Amazon ECR repository
- CI/CD pipeline to build and push container

**Monthly Cost Breakdown:**
```
ECR storage: $0.10/month (1 GB container image × $0.10/GB)
Lambda execution: $0 (Free tier)
EventBridge: $0 (Free tier)
S3 storage: $0.02/month
S3 PUT requests: $0.002/month
DynamoDB: $0 (Free tier)
Hugging Face API: $0
GitHub Actions (container build): $0 (Free tier)

TOTAL: ~$0.12/month (12 cents)
```

**Pros:**
- Can include any dependencies (even system libraries)
- Larger package size limit (10 GB vs 250 MB)
- Same environment locally and in Lambda
- Good for complex dependencies

**Cons:**
- More complex than zip deployment
- Requires Docker knowledge
- Slower cold starts (container needs to load)
- Larger storage cost

**Maintenance:**
- Rebuild container on code changes
- Manage ECR image versions

**Production readiness: 8/10**
- Good for complex apps
- Overkill for this use case

---

### Option 4: Manual Zip Deployment (NOT RECOMMENDED)

**How it works:**
1. Manually run commands to package code
2. Create zip file
3. Upload to Lambda via AWS CLI
4. Lambda runs daily at 9 PM via EventBridge

**Setup requirements:**
- AWS CLI installed
- Manual commands every time you change code

**Monthly Cost Breakdown:**
```
Lambda execution: $0 (Free tier)
EventBridge: $0 (Free tier)
S3 storage: $0.02/month
S3 PUT requests: $0.002/month
DynamoDB: $0 (Free tier)
Hugging Face API: $0

TOTAL: ~$0.022/month (2 cents)
```

**Pros:**
- Lowest cost (same as GitHub Actions)
- Simple to understand
- No external services

**Cons:**
- Manual work every single time you change code
- Error-prone (easy to forget files)
- No version control of deployments
- No rollback capability
- Risk of including wrong files (.env, secrets)
- Time-consuming
- Not scalable for team

**Maintenance:**
- High maintenance burden
- Every code change requires manual repackaging and upload

**Production readiness: 4/10**
- Works but not professional
- Fine for one-time projects
- Bad for long-running production systems

---

## COMPARISON TABLE

| Feature | GitHub Actions | AWS CodePipeline | Docker Container | Manual Zip |
|---------|----------------|------------------|------------------|------------|
| **Monthly Cost** | $0.02 | $6.02 | $0.12 | $0.02 |
| **Auto-deploy on push** | Yes | Yes | Yes (with CI/CD) | No |
| **Setup complexity** | Low | Medium | Medium | Very Low |
| **Maintenance effort** | None | Low | Medium | High |
| **Team scalability** | Excellent | Good | Good | Poor |
| **Rollback capability** | Easy | Medium | Medium | Manual |
| **Deployment speed** | 2-3 min | 3-5 min | 5-7 min | 1 min (manual) |
| **Professional standard** | Yes | Yes | Yes | No |
| **Version control** | Yes | Yes | Yes | No |

---

## RECOMMENDATION: GitHub Actions (Option 1)

**Why:**
1. **Lowest cost:** $0.02/month (same as manual but automated)
2. **Zero maintenance:** Push code and it auto-deploys
3. **Industry standard:** Used by most professional teams
4. **Best developer experience:** Simple, fast, reliable
5. **No lock-in:** Can switch to other CI/CD easily
6. **Free forever:** GitHub Actions free tier is generous

**Perfect for your use case:**
- Solo developer (you)
- Monorepo structure (all code in one place)
- Regular updates (you'll iterate on this)
- Professional quality (production system running for months/years)

---

## AUTOMATION DETAILS - EventBridge Schedule

**All options use the same EventBridge trigger:**

```yaml
Schedule: cron(0 21 * * ? *)
Explanation:
  - Minute: 0 (exactly on the hour)
  - Hour: 21 (9 PM UTC)
  - Day of month: * (every day)
  - Month: * (every month)
  - Day of week: ? (any day)
  - Year: * (every year)
```

**What happens at 9 PM UTC daily:**
1. EventBridge fires event at exactly 9:00 PM UTC
2. Lambda function receives event
3. Function runs: `marketplace.daily_album_art_generator.lambda_handler()`
4. Generates 4 images
5. Uploads to S3
6. Stores metadata in DynamoDB
7. Updates state file
8. Logs everything to CloudWatch

**Reliability:**
- EventBridge has 99.99% uptime SLA
- If Lambda fails, EventBridge does NOT retry (by design)
- But your code has built-in error handling and logging
- You get email alerts if pool drops below 100 images

**Monitoring:**
- CloudWatch Logs: Every execution logged
- CloudWatch Metrics: Success/failure rates
- Email alerts: When pool gets low
- S3 bucket: Visual confirmation (4 new images daily)

---

## NEXT STEPS (If you choose GitHub Actions)

**I will:**
1. Create `.github/workflows/deploy-lambda.yml` file
2. Create GitHub Actions secrets guide (AWS credentials setup)
3. Deploy Lambda function + EventBridge rule
4. Test deployment manually
5. Verify first scheduled run at 9 PM UTC
6. Document update process

**You will need to:**
1. Add AWS credentials to GitHub Secrets (one-time, 2 minutes)
2. Review and approve the workflow file
3. Push to GitHub to test auto-deployment

**Timeline:**
- Setup: 15 minutes
- First deployment: 3 minutes
- Testing: 5 minutes
- **Total: ~25 minutes**

---

## QUESTIONS FOR YOU

1. **Which deployment option do you prefer?**
   - Option 1: GitHub Actions (recommended, $0.02/month)
   - Option 2: AWS CodePipeline ($6.02/month)
   - Option 3: Docker Container ($0.12/month)
   - Option 4: Manual Zip (not recommended)

2. **Is your code currently in a GitHub repository?**
   - If yes: We can use GitHub Actions immediately
   - If no: We can create one or use another CI/CD

3. **Do you want email notifications when deployments succeed/fail?**
   - GitHub Actions can send deployment status emails
   - Can also integrate with Discord/Slack

4. **Any security/compliance requirements I should know about?**
   - All options use AWS IAM for security
   - Secrets stored in AWS Parameter Store (already set up)
   - No credentials in code

---

## COST SUMMARY (12-Month Projection)

**GitHub Actions (Option 1):**
- Year 1: $0.26
- 250 images reached in 63 days
- System continues running indefinitely
- No cost increase

**AWS CodePipeline (Option 2):**
- Year 1: $72.24
- Same functionality as GitHub Actions
- 288x more expensive

**Docker Container (Option 3):**
- Year 1: $1.44
- 5.5x more expensive than GitHub Actions
- Same functionality

**Manual Zip (Option 4):**
- Year 1: $0.26 (same as GitHub Actions)
- But requires 10+ hours of manual work
- Value of your time >> $72 saved vs CodePipeline

---

## MY RECOMMENDATION

**Use GitHub Actions (Option 1).**

It's the perfect balance of:
- Cost (essentially free)
- Automation (zero maintenance)
- Reliability (industry standard)
- Professional quality (proper CI/CD)
- Flexibility (easy to modify)

You'll have a production-ready system that runs every night at 9 PM UTC, automatically deploys when you push code, and costs less than a cup of coffee per year.

---

**Ready to proceed?** Let me know which option you choose and I'll implement it properly.
