# Initial Lambda Deployment - Execution Plan

**What we're doing:** Setting up Lambda function for the FIRST time. After this, GitHub Actions will handle all future deployments automatically.

---

## Current Status

**Completed:**
- ✅ Production generation system working (4 images generated successfully)
- ✅ GitHub Actions workflow created (`.github/workflows/deploy-lambda.yml`)
- ✅ IAM role created (`frank-art-generator-role`)
- ✅ AWS credentials guide created

**Next:**
- Initial Lambda function deployment
- EventBridge schedule setup
- Testing and verification

---

## Deployment Steps

### Step 1: Package Code (1 minute)

```bash
cd backend

# Clean old package if exists
rm -rf lambda_package
mkdir lambda_package

# Install minimal dependencies
pip install huggingface_hub==0.26.5 Pillow==11.1.0 requests==2.32.4 urllib3==2.5.0 -t lambda_package/

# Copy code folders
cp -r marketplace lambda_package/
cp -r auth lambda_package/
cp -r data lambda_package/

# Create zip (excluding cache files)
cd lambda_package
zip -r ../frank_art_generator.zip . -x "*.pyc" -x "*__pycache__*" -x "*.dist-info/*"
cd ..
```

**Expected:** `frank_art_generator.zip` created (~50-80 MB)

---

### Step 2: Create Lambda Function (1 minute)

```bash
# Get IAM role ARN
ROLE_ARN=$(aws iam get-role --role-name frank-art-generator-role --query 'Role.Arn' --output text --region us-east-2)

# Create Lambda function
aws lambda create-function \
  --function-name frank-art-generator \
  --runtime python3.12 \
  --role $ROLE_ARN \
  --handler marketplace.daily_album_art_generator.lambda_handler \
  --zip-file fileb://frank_art_generator.zip \
  --timeout 300 \
  --memory-size 256 \
  --region us-east-2 \
  --description "Frank's Garage - Daily AI art generation (4 images at 9 PM UTC)"
```

**Expected output:**
```json
{
    "FunctionName": "frank-art-generator",
    "FunctionArn": "arn:aws:lambda:us-east-2:...",
    "Runtime": "python3.12",
    "Handler": "marketplace.daily_album_art_generator.lambda_handler",
    "State": "Active"
}
```

---

### Step 3: Create EventBridge Rule (1 minute)

```bash
# Create schedule rule (9 PM UTC daily)
aws events put-rule \
  --name frank-art-daily-generation \
  --schedule-expression "cron(0 21 * * ? *)" \
  --state ENABLED \
  --description "Trigger Frank Art generation daily at 9 PM UTC" \
  --region us-east-2

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Add Lambda permission for EventBridge
aws lambda add-permission \
  --function-name frank-art-generator \
  --statement-id frank-art-eventbridge-trigger \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-2:${ACCOUNT_ID}:rule/frank-art-daily-generation \
  --region us-east-2

# Connect rule to Lambda
aws events put-targets \
  --rule frank-art-daily-generation \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-2:${ACCOUNT_ID}:function:frank-art-generator" \
  --region us-east-2
```

**Expected:** EventBridge rule created and linked to Lambda

---

### Step 4: Test Lambda Manually (5 minutes)

```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name frank-art-generator \
  --region us-east-2 \
  --log-type Tail \
  output.json

# Check output
cat output.json

# View logs
aws logs tail /aws/lambda/frank-art-generator --follow --region us-east-2
```

**Expected:**
- Lambda executes successfully
- 4 new images appear in S3
- DynamoDB gets 4 new entries
- State file advances
- Logs show generation progress

---

### Step 5: Verify Automation (1 minute)

```bash
# Check EventBridge rule status
aws events describe-rule \
  --name frank-art-daily-generation \
  --region us-east-2

# Check Lambda configuration
aws lambda get-function-configuration \
  --function-name frank-art-generator \
  --region us-east-2
```

**Expected:**
- Rule state: `ENABLED`
- Schedule: `cron(0 21 * * ? *)`
- Lambda timeout: 300 seconds
- Lambda memory: 256 MB

---

### Step 6: Setup GitHub Secrets (2 minutes)

**Manual step - you need to do this:**

1. Go to GitHub repo settings
2. Add 2 secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Follow [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) guide

---

### Step 7: Test GitHub Actions Deployment (3 minutes)

```bash
# Make a small change to trigger deployment
cd backend
echo "# Deployment test" >> marketplace/artwork_analytics.py

# Commit and push
git add .
git commit -m "test: verify GitHub Actions auto-deployment"
git push origin main

# Monitor deployment in GitHub Actions tab
```

**Expected:**
- GitHub Actions workflow runs automatically
- Deployment completes in ~2-3 minutes
- Lambda function updated with new code

---

## Verification Checklist

After deployment, verify:

- [ ] Lambda function exists: `aws lambda list-functions --region us-east-2 | grep frank-art-generator`
- [ ] EventBridge rule exists: `aws events list-rules --region us-east-2 | grep frank-art-daily`
- [ ] Rule has target: `aws events list-targets-by-rule --rule frank-art-daily-generation --region us-east-2`
- [ ] Lambda can be invoked: `aws lambda invoke --function-name frank-art-generator --region us-east-2 test.json`
- [ ] Logs appear in CloudWatch: `aws logs tail /aws/lambda/frank-art-generator --region us-east-2`
- [ ] Images generated successfully (check S3)
- [ ] GitHub Actions workflow passes

---

## Timeline

**Total time: ~15 minutes**

1. Package code: 1 min
2. Create Lambda: 1 min
3. Setup EventBridge: 1 min
4. Test execution: 5 min (Lambda runtime)
5. Verify automation: 1 min
6. Setup GitHub Secrets: 2 min (manual)
7. Test GitHub Actions: 3 min

---

## What Happens After Deployment

**Automatically every night at 9 PM UTC:**
- EventBridge triggers Lambda
- Lambda generates 4 images
- Images uploaded to S3
- Metadata stored in DynamoDB
- State file advanced
- Logs written to CloudWatch

**When you push code to GitHub:**
- GitHub Actions detects push
- Packages code automatically
- Deploys to Lambda
- Lambda continues running at 9 PM daily

**You never manually deploy again!**

---

## Cost Reminder

**Monthly: $0.02**
- GitHub Actions: Free
- Lambda: Free (within tier)
- EventBridge: Free
- S3: $0.02
- DynamoDB: Free

---

## Ready to Deploy?

**Confirm before I execute:**
1. Do you want me to run Steps 1-5 now? (packaging, Lambda creation, EventBridge setup, testing)
2. You'll need to do Step 6 (GitHub Secrets) manually
3. Then we test Step 7 (GitHub Actions) together

Say "yes" to proceed with automated deployment, or let me know if you have questions.
