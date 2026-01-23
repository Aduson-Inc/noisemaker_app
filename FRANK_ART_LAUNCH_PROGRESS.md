# Frank's Garage Marketplace - Production Launch Progress

**Date:** 2026-01-23
**Goal:** Launch production Frank Art generation system TODAY
**Target:** 4 images/day → 250 images in 63 days (~2 months)

---

## SYSTEM ARCHITECTURE

**What it is:**
- SHARED marketplace for ALL app users (not per-user)
- Always-available reservoir of up to 250 AI-generated artworks
- Users can browse, download (1 token), or purchase ($2.99/$9.99/$19.99)
- Generates 4 new images daily at 9 PM UTC via AWS Lambda + EventBridge

**Token System:**
- Signup: 3 tokens
- Per song upload: 3 tokens (max 12 from songs)
- Max total: 15 tokens
- Download: Costs 1 token, art STAYS in pool
- Purchase: Costs $$, NO tokens, art REMOVED from pool

---

## PROMPT PATTERN (Confirmed)

**4-Day Cycle:** DARK → BLANK → BRIGHT → BLANK → (repeat)

**Monday (Day 0) - DARK:**
```
create a Impressionism background graphic in the style of Jean-Michel Basquiat using deep black and charcoal, masterpiece, best quality, highly detailed, sharp focus, professional artwork
```

**Tuesday (Day 1) - BLANK:**
```
create a Cubism background graphic in the style of Georges Braque, masterpiece, best quality, highly detailed, sharp focus, professional artwork
```

**Wednesday (Day 2) - BRIGHT:**
```
create a Surrealism background graphic in the style of Georgia Theologoe using vibrant red and white, masterpiece, best quality, highly detailed, sharp focus, professional artwork
```

**Thursday (Day 3) - BLANK:**
```
create a Art Deco background graphic in the style of Ernst Ludwig Kirchner, masterpiece, best quality, highly detailed, sharp focus, professional artwork
```

**Rotation:**
- 7 Art Styles (cycles every 7 days)
- 11 Artists (cycles every 11 days)
- 15 Dark Colors (used every 60 days)
- 14 Bright Colors (used every 56 days)
- **77 unique style+artist combinations!**

---

## ✅ COMPLETED TASKS

### 1. Planning Phase ✅
- Analyzed all 7 marketplace files
- Understood system architecture
- Confirmed prompt rotation logic
- Created comprehensive plan at: `C:\Users\tredev\.claude\plans\cheerful-jingling-reddy.md`

### 2. File Renaming (IN PROGRESS)
**Completed:**
- ✅ `artwork_analytics.py` - Lines 57, 550 (2 of 3 edits done)

**Still Need:**
- [ ] `artwork_analytics.py` - Line 2 (title - 1st edit was rejected)
- [ ] `artwork_generator.py` - Lines 2-3, 94, 157, 303, 318
- [ ] `daily_album_art_generator.py` - Lines 2, 5, 750

---

## 🚧 CURRENT STATUS

**Last Action:** Started renaming "Album Art" → "Frank Art"

**Files Modified:**
1. `artwork_analytics.py` - 2 of 3 edits completed

**Files Pending:**
1. `artwork_analytics.py` - 1 more edit needed (line 2 - title)
2. `artwork_generator.py` - All edits pending
3. `daily_album_art_generator.py` - All edits pending

---

## 📋 NEXT STEPS (Immediate)

### Step 1: Complete File Renaming
**artwork_analytics.py (1 edit remaining):**
- Line 2: "Album Artwork Analytics" → "Frank Art Analytics"

**artwork_generator.py (6 edits needed):**
- Line 2: "SDXL Album Artwork Generator Plugin System" → "SDXL Frank Art Generator Plugin System"
- Line 3: "album artwork creation" → "Frank Art creation"
- Line 94: "album artwork" → "Frank Art"
- Line 157: "Generate album artwork" → "Generate Frank Art"
- Line 303: "album artwork, music cover art" → "Frank Art, music cover art"
- Line 318: "album artwork style" → "Frank Art style"

**daily_album_art_generator.py (3 edits needed):**
- Line 2: "Daily Album Art Generator" → "Daily Frank Art Generator"
- Line 5: "album artworks" → "Frank Art pieces"
- Line 750: "Daily Album Art Generator for MyNoiseyApp" → "Daily Frank Art Generator for Frank's Garage"

### Step 2: Run FULL PRODUCTION
```bash
cd backend
python marketplace/daily_album_art_generator.py
```

**What will happen:**
- Pulls HUGGINGFACE_TOKEN from AWS Parameter Store `/noisemaker/huggingface_token`
- Checks pool count (currently unknown, assume 0)
- If pool < 250: Generates 4 images
- Each image:
  - Generates 2000x2000 from Hugging Face SDXL API
  - Resizes to 600x600 (mobile) and 200x200 (thumbnail) using PIL
  - Uploads all 3 sizes to S3:
    - `s3://noisemakerpromobydoowopp/ArtSellingONLY/original/`
    - `s3://noisemakerpromobydoowopp/ArtSellingONLY/mobile/`
    - `s3://noisemakerpromobydoowopp/ArtSellingONLY/thumbnails/`
  - Stores metadata in DynamoDB `noisemaker-frank-art`
- Advances state file in S3: `s3://noisemakerpromobydoowopp/ArtSellingONLY/state.json`

**Expected Output:**
```
🚀 STARTING FRANK'S GARAGE ART GENERATION - FULL RUN (4 IMAGES)
📊 Current pool size: 0/250
📋 TODAY'S GENERATION SETTINGS:
   Art Style: Impressionism
   Artist: Jean-Michel Basquiat
   Color Mode: DARK
   Colors: deep black and charcoal
   Prompt: create a Impressionism background graphic...

🎨 GENERATING IMAGE 1/4
...
✅ Successfully generated and uploaded: 4/4 images
```

### Step 3: Verification Checklist

**S3 Verification (12 files total):**
```bash
aws s3 ls s3://noisemakerpromobydoowopp/ArtSellingONLY/original/ --region us-east-2
aws s3 ls s3://noisemakerpromobydoowopp/ArtSellingONLY/mobile/ --region us-east-2
aws s3 ls s3://noisemakerpromobydoowopp/ArtSellingONLY/thumbnails/ --region us-east-2
```
- Should see 4 new .png files in EACH folder (12 total)
- File naming: `{uuid}.png`

**DynamoDB Verification:**
```bash
aws dynamodb scan --table-name noisemaker-frank-art --region us-east-2 --select COUNT
```
- Count should be 4 (or 4 more than before)

**State File Verification:**
```bash
aws s3 cp s3://noisemakerpromobydoowopp/ArtSellingONLY/state.json - --region us-east-2
```
- Should show:
  - `art_style_index`: 4 (advanced from 0)
  - `style_index`: 4 (advanced from 0)
  - `day_counter`: 4 (advanced from 0)
  - `dark_color_index`: 1 (advanced from 0 after day 0)
  - `bright_color_index`: 1 (advanced from 0 after day 2)

### Step 4: Deploy Lambda + EventBridge

**IAM Role Creation:**
```bash
aws iam create-role --role-name frank-art-generator-role --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name frank-art-generator-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name frank-art-generator-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name frank-art-generator-role --policy-arn arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess
aws iam attach-role-policy --role-name frank-art-generator-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

**Lambda Package:**
```bash
cd backend
mkdir -p lambda_package
pip install -r requirements.txt -t lambda_package/
cp -r marketplace lambda_package/
cp -r auth lambda_package/
cp -r data lambda_package/
cd lambda_package
zip -r ../frank_art_generator.zip .
```

**Lambda Function:**
```bash
aws lambda create-function \
  --function-name frank-art-generator \
  --runtime python3.12 \
  --role arn:aws:iam::ACCOUNT_ID:role/frank-art-generator-role \
  --handler marketplace.daily_album_art_generator.lambda_handler \
  --zip-file fileb://frank_art_generator.zip \
  --timeout 600 \
  --memory-size 512 \
  --region us-east-2
```

**EventBridge Rule (9 PM UTC daily):**
```bash
aws events put-rule \
  --name frank-art-daily-generation \
  --schedule-expression "cron(0 21 * * ? *)" \
  --state ENABLED \
  --region us-east-2

aws lambda add-permission \
  --function-name frank-art-generator \
  --statement-id frank-art-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-2:ACCOUNT_ID:rule/frank-art-daily-generation \
  --region us-east-2

aws events put-targets \
  --rule frank-art-daily-generation \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-2:ACCOUNT_ID:function:frank-art-generator" \
  --region us-east-2
```

---

## 🔑 CRITICAL FILES & PATHS

**Backend Code:**
- Main generator: `backend/marketplace/daily_album_art_generator.py`
- Analytics: `backend/marketplace/artwork_analytics.py`
- Manager: `backend/marketplace/frank_art_manager.py`
- Integration: `backend/marketplace/frank_art_integration.py`
- Cleanup: `backend/marketplace/frank_art_cleanup.py`
- Generator plugin: `backend/marketplace/artwork_generator.py`
- Environment loader: `backend/auth/environment_loader.py`

**AWS Resources:**
- S3 Bucket: `noisemakerpromobydoowopp`
- S3 Prefixes:
  - Original: `ArtSellingONLY/original/` (2000x2000)
  - Mobile: `ArtSellingONLY/mobile/` (600x600)
  - Thumbnails: `ArtSellingONLY/thumbnails/` (200x200)
  - State: `ArtSellingONLY/state.json`
  - Sold Archive: `ArtSellingONLY/sold-archive/`
  - Permanent: `ArtSellingONLY/purchased-permanent/`
- DynamoDB Tables:
  - `noisemaker-frank-art` - Artwork metadata
  - `noisemaker-artwork-holds` - 5-min purchase holds
  - `noisemaker-frank-art-purchases` - User collections
  - `noisemaker-artwork-analytics` - Analytics tracking
  - `noisemaker-system-alerts` - System alerts
  - `noisemaker-users` - User data with art_tokens
  - `noisemaker-artwork-cleanup` - Cleanup schedule
- Parameter Store:
  - `/noisemaker/huggingface_token` - Hugging Face API token
  - Region: `us-east-2`

**Hugging Face:**
- API Endpoint: `https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0`
- Model: `stabilityai/stable-diffusion-xl-base-1.0`

---

## 📊 VERIFICATION RUBRIC

After FULL PRODUCTION run, verify ALL of these:

### ✅ Image Generation
- [ ] 4 images generated successfully
- [ ] Each image is 2000x2000 pixels
- [ ] Images have correct prompt variations (check art style, artist, colors)
- [ ] No generation errors in output

### ✅ Image Resizing (PIL)
- [ ] Each image resized to 600x600 (mobile)
- [ ] Each image resized to 200x200 (thumbnail)
- [ ] Total: 12 image files created (4 × 3 sizes)
- [ ] LANCZOS resampling used (high quality)

### ✅ S3 Upload
- [ ] 4 files in `ArtSellingONLY/original/`
- [ ] 4 files in `ArtSellingONLY/mobile/`
- [ ] 4 files in `ArtSellingONLY/thumbnails/`
- [ ] All files named with UUID format: `{uuid}.png`
- [ ] All files accessible (not 403/404)

### ✅ DynamoDB Storage
- [ ] 4 new entries in `noisemaker-frank-art` table
- [ ] Each entry has:
  - `artwork_id` (UUID)
  - `filename` (`{uuid}.png`)
  - `upload_date` (ISO format)
  - `download_count` (0)
  - `is_purchased` (false)
  - `prompt_used` (correct prompt)
  - `art_style` (correct style)
  - `artist_style` (correct artist)
  - `color_scheme` (correct color or 'none')
  - `color_mode` ('dark', 'blank', or 'bright')

### ✅ State File Advancement
- [ ] State file exists at `s3://noisemakerpromobydoowopp/ArtSellingONLY/state.json`
- [ ] `art_style_index` advanced 4 times (0→4)
- [ ] `style_index` advanced 4 times (0→4)
- [ ] `day_counter` advanced 4 times (0→4)
- [ ] `dark_color_index` advanced 1 time (after day 0)
- [ ] `bright_color_index` advanced 1 time (after day 2)
- [ ] `last_run` timestamp updated

### ✅ Prompt Accuracy
- [ ] Day 0: DARK color + Impressionism + Basquiat
- [ ] Day 1: BLANK (no color) + Cubism + Braque
- [ ] Day 2: BRIGHT color + Surrealism + Theologoe
- [ ] Day 3: BLANK (no color) + Art Deco + Kirchner

### ✅ System Health
- [ ] No Python errors or exceptions
- [ ] Hugging Face API responded successfully
- [ ] AWS credentials valid and working
- [ ] All boto3 operations succeeded
- [ ] Execution time under 10 minutes

---

## 🚨 TROUBLESHOOTING

### Issue: Hugging Face API 401 Unauthorized
**Cause:** Invalid or expired token
**Fix:** Update token in Parameter Store
```bash
aws ssm put-parameter \
  --name /noisemaker/huggingface_token \
  --value "hf_NEW_TOKEN" \
  --type SecureString \
  --region us-east-2 \
  --overwrite
```

### Issue: Hugging Face API 503 Model Loading
**Cause:** Model cold start
**Fix:** Built-in retry logic (waits 20 seconds, retries once)

### Issue: Hugging Face API 429 Rate Limit
**Cause:** Too many requests
**Fix:** Built-in retry logic (waits 20 seconds, retries once)

### Issue: S3 403 Forbidden
**Cause:** Invalid AWS credentials or permissions
**Fix:** Check IAM permissions for S3 write access

### Issue: DynamoDB ResourceNotFoundException
**Cause:** Table doesn't exist
**Fix:** Create table using `backend/scripts/create_dynamodb_tables.py`

### Issue: PIL ImportError
**Cause:** Pillow not installed
**Fix:** `pip install pillow`

---

## 📅 TIMELINE

**TODAY (Day 0):**
- ✅ Planning complete
- ⏳ File renaming (in progress)
- ⏳ FULL PRODUCTION run
- ⏳ Lambda deployment
- Target: System live by end of day

**Week 1:**
- 28 images generated (7 days × 4)
- All 7 art styles appeared
- ~7+ different artists
- Color cycle confirmed working

**Month 1:**
- ~120 images in pool
- No errors or failures
- Begin frontend UI development

**Month 2:**
- 250 images reached (~Day 63)
- Marketplace ready for user testing
- Frontend page completed

---

## 🎯 SUCCESS METRICS

**Immediate (Today):**
- 4 images generated and stored ✅
- 12 S3 files uploaded (4 × 3 sizes) ✅
- 4 DynamoDB entries created ✅
- State file advanced correctly ✅

**Short-term (Week 1):**
- 28 images total (4/day × 7 days)
- Zero generation failures
- Prompt rotation confirmed working

**Medium-term (Month 2):**
- 250 images in pool
- Lambda running automatically daily
- Email alerts functional

**Long-term (Month 3+):**
- Frontend marketplace live
- Users downloading/purchasing
- Revenue tracking active
- Weekly cleanup running

---

## 📝 NOTES

- **NO TEST MODE**: Going straight to full 4-image production
- **HF Token**: Exists in Parameter Store (validity will be verified during run)
- **AWS CLI Access**: Full access confirmed
- **System Type**: Shared marketplace for ALL users (not per-user)
- **User Verification**: All code reviewed, architecture understood
- **Renaming Strategy**: Keep separation comments (Frank Art vs Album Art), change titles/descriptions only

---

**Last Updated:** 2026-01-23 (during execution)
**Next Action:** Complete file renaming, then run FULL PRODUCTION
**Context Status:** Documented for smooth continuation
