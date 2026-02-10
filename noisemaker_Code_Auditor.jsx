import React, { useState } from 'react';
import { FileCode, CheckCircle, AlertCircle, Circle, HelpCircle, Layers, ArrowRight, GitBranch, Database, Clock, Shield, FolderTree, Search } from 'lucide-react';

export default function NoiseMAKERAuditor() {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedFolders, setExpandedFolders] = useState(['backend', 'frontend', 'frontend/src']);
  const [treeFilter, setTreeFilter] = useState('all');

  const toggleFolder = (path) => {
    setExpandedFolders(prev =>
      prev.includes(path)
        ? prev.filter(p => p !== path)
        : [...prev, path]
    );
  };

  const techStack = {
    frontend: "Next.js 15",
    backend: "FastAPI Python 3.12",
    database: "DynamoDB (9 tables, us-east-2)",
    auth: "JWT",
    storage: "S3 — noisemakerpromobydoowopp",
    payments: "Stripe (Talent $25 / Star $40 / Legend $60)"
  };

  // ============================================
  // SESSION: Feb 7, 2026
  // ============================================
  // - Added CLAUDE.md with project guidance + strict dev rules (commit ff6fa07)
  // - Reverted /my-collection endpoint from frank_art.py (feature not needed)
  // - Established workflow: Claude.ai (planning) + Claude Code PowerShell (execution) + VS Code (review)
  // - Uninstalled Claude Desktop + Chrome extension
  // - Identified stale docs/skills needing cleanup
  // - Discovered nested .claude/.vscode folders in subfolders (agent leftovers)
  // - Updated auditor to master version with complete file tree

  // ============================================
  // SESSION: Feb 10, 2026 — Frank Art Lambda Rebuild
  // ============================================
  // - Rebuilt frank-art-generator Lambda from scratch (pure AWS CLI, no SAM)
  // - Created IAM role (frank-art-generator-role) with S3/DynamoDB/SSM permissions
  // - Created EventBridge schedule (frank-art-daily-schedule) cron(0 6 * * ? *) 6 AM UTC
  // - Created scheduler IAM role (frank-art-scheduler-role)
  // - FIXED: Pillow _imaging crash — Windows-built .pyd binaries → Linux manylinux2014_x86_64 .so
  // - Verified: 4 images generated, pool at 35, 188s duration, 180MB memory
  // - Removed unused HTML templates (commit 7e98316)

  // ============================================
  // SESSION: Feb 8, 2026 — Milestone System Rewrite
  // ============================================
  // - MEGA REWRITE: milestone system (stream-based → followers/popularity/fire_mode/posts/longevity)
  // - user_manager.py: deleted 4 dead baseline functions, replaced MILESTONE_TYPES, new achieve_milestone with per-song tracking
  // - milestone_tracker.py: complete rewrite — class-based SMS/SES → pure detection functions (no AWS clients)
  // - baseline_calculator.py: removed min baseline of 5, averages however many tracks exist
  // - payment.py: baseline trigger wired to confirm_payment AND stripe_webhook, idempotency guard
  // - fire_mode_analyzer.py: rewritten — levels not tiers, 5-day guaranteed window, 2 consecutive days below peak = exit
  // - auth.py: removed dead MilestoneTracker import + instance (crash fix)
  // - noisemaker-baselines table recreated (was deleted in previous purge)
  // - DynamoDB tables confirmed at 9 (was 26 pre-purge)
  // - Known blast radius: daily_processor.py, song_manager.py still reference old APIs

  // ============================================
  // SESSION: Feb 7, 2026 — Evening (Deep Audit)
  // ============================================
  // - Comprehensive 6-task backend audit completed (READ ONLY)
  // - CRITICAL: noisemaker-platform-connections table MISSING — platform OAuth fully broken
  // - CRITICAL: routes/platforms.py passes state=None — CSRF validation always fails
  // - Baseline calculation is dead code — never triggered after signup/payment
  // - Found 3 duplicate PlatformOAuthManager instances (3 SSM calls on startup)
  // - Found 4 duplicate SongManager instances + 1 duplicate UserManager
  // - Timestamp inconsistency: datetime.now() vs datetime.utcnow() mixed in user_manager.py
  // - Default platform limit fallback is 3 (should be 2 for Talent tier)
  // - DynamoDB table counts updated from live scans
  // - Custom commands created: noisemaker-doc-auditor, noisemaker-project-lead
  // - .gitignore updated to track .claude/commands/ (settings.local.json still ignored)
  // - DEVELOPMENT_RULES.md deleted (superseded by CLAUDE.md)
  // - 11 backend files audited/analyzed in this session
  // - Test user TRESCH active: Star tier, platforms_pending, first_payment milestone achieved

  // ============================================
  // COMPLETED FIXES
  // ============================================
  const completedFixes = [
    { id: "O1", file: "song_manager.py", fix: "Now respects initial_days (added _get_stage_from_days())", date: "Feb 4 AM" },
    { id: "O2", file: "api.ts", fix: "Fixed getUserSongs path → /api/songs/user/:id", date: "Feb 4 AM" },
    { id: "O3", file: "api.ts", fix: "Removed redundant user_id from addSongFromUrl body", date: "Feb 4 AM" },
    { id: "O4", file: "song_manager.py", fix: "Removed deprecated stream_count fields", date: "Feb 4 AM" },
    { id: "—", file: "dynamodb_client.py", fix: "Added convert_floats_to_decimal() helper", date: "Feb 4 AM" },
    { id: "—", file: "frank_art_generator.py", fix: "Switched to Tongyi-MAI/Z-Image-Turbo (HF pricing fix)", date: "Feb 4 AM" },
    { id: "—", file: "add-songs/page.tsx", fix: "Updated to match new API signature", date: "Feb 4 AM" },
    { id: "D4", file: "S3 CORS + frank_art.py", fix: "S3 CORS fix applied. /my-collection removed (not needed)", date: "Feb 4 PM → Feb 7" },
    { id: "—", file: "S3 CORS", fix: "Added CORS config to noisemakerpromobydoowopp bucket", date: "Feb 4 PM" },
    { id: "—", file: "CLAUDE.md", fix: "Added project guidance + strict dev rules (commit ff6fa07)", date: "Feb 7" },
    { id: "D9", file: "DynamoDB", fix: "noisemaker-platform-connections table recreated", date: "Feb 8" },
    { id: "D10", file: "routes/platforms.py", fix: "OAuth state=None bug fixed (CSRF validation)", date: "Feb 8" },
    { id: "D11", file: "payment.py + webhook", fix: "Baseline calculation now triggered after payment confirm + webhook", date: "Feb 8" },
    { id: "D12", file: "routes/auth.py", fix: "Removed duplicate PlatformOAuthManager. Dead MilestoneTracker import removed.", date: "Feb 8" },
    { id: "D13", file: "data/user_manager.py", fix: "Removed duplicate instances. Milestone system fully rewritten.", date: "Feb 8" },
    { id: "—", file: "fire_mode_analyzer.py", fix: "Complete rewrite: levels not tiers, 5-day window, consecutive-day exit", date: "Feb 8" },
    { id: "—", file: "milestone_tracker.py", fix: "Complete rewrite: pure functions, no classes, no AWS clients", date: "Feb 8" },
    { id: "D16", file: "routes/auth.py", fix: "Removed dead initialize_baseline_collection() call that crashed signup", date: "Feb 8" },
    { id: "—", file: "Lambda", fix: "Rebuilt frank-art-generator Lambda from scratch (AWS CLI, no SAM). IAM + EventBridge + schedule.", date: "Feb 10" },
    { id: "—", file: "Lambda", fix: "Fixed Pillow _imaging crash: rebuilt zip with manylinux2014_x86_64 Linux binaries", date: "Feb 10" },
  ];

  // ============================================
  // OPEN ISSUES
  // ============================================
  const openIssues = [
    { id: "D1", priority: "critical", title: "spotify_popularity NOT being fetched/stored", location: "noisemaker-songs table", description: "All songs have spotify_popularity = 0. Breaks Fire Mode." },
    { id: "D2", priority: "critical", title: "popularity_history NOT being tracked", location: "noisemaker-songs table", description: "popularity_history = empty []. Fire Mode can never trigger." },
    { id: "D3", priority: "medium", title: "Orphaned email reservations (was 7, now 1)", location: "noisemaker-email-reservations", description: "Previously 7 orphaned entries. Now 1 active entry (TRESCH). Verify old entries were cleaned up or if table was recreated." },
    { id: "O5", priority: "medium", title: "Field naming inconsistency", location: "songs.py vs song_manager.py", description: "promotion_stage vs stage_of_promotion — pick one." },
    { id: "D5", priority: "medium", title: "streams_per_day is WRONG concept", location: "noisemaker-users table", description: "Spotify has popularity (0-100), not streams_per_day." },
    { id: "D6", priority: "medium", title: "Typo: artiist_name (double i)", location: "noisemaker-users table", description: "Should be artist_name." },
    { id: "D7", priority: "medium", title: "Color analysis not implemented", location: "content/image_processor.py", description: "File exists, needs audit. Should match song art colors → background templates." },
    { id: "D17", priority: "medium", title: "daily_processor.py uses old MilestoneTracker class", location: "scheduler/daily_processor.py:30,60,596", description: "MilestoneTracker class was removed. daily_processor will crash." },
    { id: "D18", priority: "medium", title: "schemas.py still has fire_mode_available field", location: "backend/models/schemas.py:204", description: "Stale field from old fire mode system." },
    { id: "D19", priority: "low", title: "Fake rubric headers in ~30 backend files", location: "Multiple files", description: "'Senior Python Backend Engineer' / 'SCORE: 10/10' still in unmodified files." },
    { id: "D14", priority: "medium", title: "Timestamp inconsistency (now vs utcnow)", location: "data/user_manager.py", description: "Some fields use datetime.now() (local EST), others datetime.utcnow(). 5-hour gap causes comparison bugs." },
    { id: "O6", priority: "low", title: "Hardcoded genre default 'Pop'", location: "songs.py:519", description: "All songs default to Pop." },
    { id: "D8", priority: "low", title: "Inconsistent user data between old/new users", location: "noisemaker-users table", description: "Jan 30 user missing fields that Feb 4 user has." },
    { id: "D15", priority: "low", title: "Platform limit default fallback is 3", location: "routes/platforms.py:270, scheduler/daily_processor.py:482", description: "Default should be 2 (Talent tier minimum), not 3." },
    { id: "C1", priority: "low", title: "Nested .claude/.vscode in subfolders", location: "backend/content, marketplace, scheduler", description: "Agent leftover config files. Verify then remove." },
  ];

  // ============================================
  // OPEN QUESTIONS
  // ============================================
  const openQuestions = [
    { id: 1, category: "Data Storage", question: "Which DynamoDB table stores song data?", status: "answered", answer: "noisemaker-songs (PK: user_id, SK: song_id)" },
    { id: 2, category: "Data Storage", question: "Where are color analysis results stored?", status: "open", answer: null },
    { id: 3, category: "Data Storage", question: "Where is baseline popularity stored?", status: "answered", answer: "noisemaker-baselines table (may be redundant with users table)" },
    { id: 4, category: "Data Storage", question: "Is there an onboarding_complete flag?", status: "answered", answer: "Yes — set to true after songs added, before redirect to dashboard" },
    { id: 5, category: "Color Analysis", question: "Which file runs color analysis?", status: "answered", answer: "content/image_processor.py — exists but needs audit" },
    { id: 6, category: "Color Analysis", question: "External API or local library?", status: "open", answer: null },
    { id: 7, category: "Color Analysis", question: "What format is the color output?", status: "open", answer: null },
    { id: 8, category: "Baseline Popularity", question: "Spotify field or calculated?", status: "answered", answer: "Spotify popularity (0-100). baseline_calculator.py averages 5 most recent songs, rounds UP" },
    { id: 9, category: "Baseline Popularity", question: "Which file runs this calculation?", status: "answered", answer: "backend/spotify/baseline_calculator.py" },
    { id: 10, category: "Daily Processor", question: "What file adds +1 to days_in_promotion?", status: "answered", answer: "backend/scheduler/daily_processor.py" },
    { id: 11, category: "Daily Processor", question: "Is this Lambda, cron job, or backend service?", status: "answered", answer: "Not visible in main.py. cron_manager.py exists but unaudited. Likely needs EventBridge or external trigger." },
    { id: 12, category: "Frontend", question: "Is the loading state already built?", status: "open", answer: null },
    { id: 13, category: "Frontend", question: "Progress updates: WebSocket, polling, or single?", status: "open", answer: null },
    { id: 14, category: "Business Logic", question: "If user uploads only 1 song, does it start at Day 0?", status: "open", answer: null },
    { id: 15, category: "Business Logic", question: "Can users add songs 2 & 3 later?", status: "open", answer: null },
    { id: 16, category: "Architecture", question: "Which tables can merge into user profile?", status: "answered", answer: "platform-connections should NOT merge (composite key needed). milestones already IN user record. noisemaker-baselines could potentially merge." },
    { id: 17, category: "Frontend", question: "Which landing page variant is active? (aurora/monolith/noir-luxe/genz)", status: "open", answer: null },
    { id: 18, category: "Frontend", question: "Are pricing-v2.tsx and platforms-v*.tsx still in use?", status: "open", answer: null },
    { id: 19, category: "Architecture", question: "Should noisemaker-platform-connections be recreated or redesigned?", status: "answered", answer: "Recreated with same schema (PK: user_id, SK: platform). Working." },
    { id: 20, category: "Business Logic", question: "When should baseline calculation trigger? After payment? After first song? On schedule?", status: "answered", answer: "After payment confirmation (both confirm_payment endpoint and checkout.session.completed webhook). Idempotency guard prevents double-calc." },
    { id: 21, category: "Data Storage", question: "Is the noisemaker-baselines table also missing? baseline_calculator.py references it.", status: "answered", answer: "Was deleted in purge. Recreated Feb 8 (PK: user_id, SK: calculation_date)." },
  ];

  // ============================================
  // FILES ANALYZED
  // ============================================
  const analyzedFiles = [
    { path: "backend/routes/songs.py", status: "done", notes: "4 endpoints mapped, all dependencies traced" },
    { path: "backend/data/song_manager.py", status: "fixed", notes: "initial_days fixed, stream_count removed, _get_stage_from_days() added" },
    { path: "backend/data/dynamodb_client.py", status: "fixed", notes: "Float→Decimal conversion added" },
    { path: "backend/marketplace/frank_art_generator.py", status: "fixed", notes: "Lambda rebuilt Feb 10 via AWS CLI. Pillow Linux binary fix. Verified: 4 imgs, 188s, 180MB." },
    { path: "backend/routes/frank_art.py", status: "fixed", notes: "/my-collection removed (not needed). S3 CORS fixed." },
    { path: "frontend/src/lib/api.ts", status: "fixed", notes: "getUserSongs path fixed, redundant user_id removed" },
    { path: "frontend/src/app/onboarding/add-songs/page.tsx", status: "fixed", notes: "Updated API call signature" },
    { path: "CLAUDE.md", status: "done", notes: "Added Feb 7 — project guidance + dev rules + auditor reference" },
    { path: "backend/data/platform_oauth_manager.py", status: "audited", notes: "CRITICAL: writes to missing table. 835 lines. Token encryption, OAuth for 8 platforms." },
    { path: "backend/data/user_manager.py", status: "fixed", notes: "REWRITTEN: Dead baseline funcs removed, milestone system replaced (30+ milestones, per-song tracking, S3 presigned URLs)" },
    { path: "backend/routes/auth.py", status: "fixed", notes: "Dead MilestoneTracker import + initialize_baseline_collection call removed." },
    { path: "backend/routes/platforms.py", status: "audited", notes: "288 lines. BUG: state=None in callback. Default limit fallback 3." },
    { path: "backend/main.py", status: "audited", notes: "111 lines. All routes registered correctly. CORS configured." },
    { path: "backend/spotify/baseline_calculator.py", status: "fixed", notes: "Min baseline removed. Averages however many tracks exist. Now triggered by payment.py" },
    { path: "backend/spotify/spotipy_client.py", status: "audited", notes: "548 lines. Works correctly but not invoked for popularity tracking." },
    { path: "backend/spotify/popularity_tracker.py", status: "audited", notes: "409 lines. Never invoked — explains D1/D2." },
    { path: "backend/spotify/fire_mode_analyzer.py", status: "fixed", notes: "Complete rewrite: levels (not tiers), 5-day guaranteed window, consecutive-day exit" },
    { path: "backend/models/schemas.py", status: "audited", notes: "270 lines. All Pydantic request/response models." },
    { path: "backend/auth/user_auth.py", status: "audited", notes: "Partial read. Password hashing, sessions. Uses time.time() for created_at." },
    { path: "backend/routes/payment.py", status: "fixed", notes: "Baseline trigger wired. Webhook synced with confirm_payment." },
    { path: "backend/notifications/milestone_tracker.py", status: "fixed", notes: "Complete rewrite: pure functions for follower/popularity/fire_mode/post/longevity detection" },
    { path: "backend/routes/dashboard.py", status: "audited", notes: "Partial read. mark_milestone_video_played compat verified." },
  ];

  // ============================================
  // FILE QUEUE (next to analyze)
  // ============================================
  const fileQueue = [
    { priority: 1, file: "backend/scheduler/daily_processor.py", reason: "Core product — 9 PM daily job. Only major unaudited backend file.", status: "next" },
    { priority: 2, file: "backend/scheduler/cron_manager.py", reason: "How daily_processor is triggered — EventBridge? Cron?", status: "queued" },
    { priority: 3, file: "backend/content/image_processor.py", reason: "Color analysis implementation status (D7)", status: "queued" },
    { priority: 4, file: "backend/content/content_orchestrator.py", reason: "Full content creation pipeline", status: "queued" },
    { priority: 5, file: "backend/content/caption_generator.py", reason: "AI caption generation — platform character limits", status: "queued" },
    { priority: 6, file: "backend/content/multi_platform_poster.py", reason: "Actual posting logic — depends on platform_oauth_manager", status: "queued" },
    { priority: 7, file: "backend/auth/environment_loader.py", reason: "get_platform_credentials — used by baseline_calculator + popularity_tracker", status: "queued" },
    { priority: 8, file: "backend/scripts/create_dynamodb_tables.py", reason: "Check if platform-connections table is in the creation script", status: "queued" },
    { priority: 9, file: "backend/config/platform_config.py", reason: "Unknown file — not in old auditor, needs investigation", status: "queued" },
    { priority: 10, file: "backend/content/content_integration.py", reason: "Unknown file — not in old auditor, needs investigation", status: "queued" },
  ];

  // ============================================
  // DynamoDB TABLE STATUS (from Feb 4 audit)
  // ============================================
  const tableStatus = [
    { name: "noisemaker-users", items: 1, size: "~3 KB", status: "active", issue: "artiist_name typo, mixed timestamp formats" },
    { name: "noisemaker-songs", items: 0, size: "0 B", status: "active", issue: "Empty — no songs uploaded yet" },
    { name: "noisemaker-frank-art", items: 19, size: "11.6 KB", status: "active", issue: null },
    { name: "noisemaker-frank-art-purchases", items: 0, size: "0 B", status: "active", issue: null },
    { name: "noisemaker-email-reservations", items: 1, size: "~100 B", status: "active", issue: null },
    { name: "noisemaker-oauth-states", items: 0, size: "0 B", status: "active", issue: "Needs TTL auto-delete" },
    { name: "noisemaker-platform-connections", items: 0, size: "0 B", status: "active", issue: "Recreated Feb 8. PK: user_id, SK: platform" },
    { name: "noisemaker-milestones", items: 0, size: "0 B", status: "active", issue: "PK: user_id, SK: milestone_type. Per-song milestones use composite SK." },
    { name: "noisemaker-baselines", items: 0, size: "0 B", status: "active", issue: "Recreated Feb 8. PK: user_id, SK: calculation_date" },
  ];

  // ============================================
  // COMPLETE FILE TREE (from tree.txt Feb 7, 2026)
  // Status: active = confirmed in use | audited = analyzed | pending = not yet checked | fixed = had issues, now resolved
  // ============================================
  const fileTree = {
    name: 'nm_mono',
    type: 'folder',
    children: [
      { name: 'CLAUDE.md', type: 'file', status: 'audited', note: 'Project guidance + dev rules. Commit ff6fa07' },
      { name: 'DEVELOPMENT_RULES.md', type: 'file', status: 'fixed', note: 'Deleted — superseded by CLAUDE.md (commit 9af0666)' },
      { name: 'README.md', type: 'file', status: 'pending', note: 'Verify if current' },
      { name: '.gitignore', type: 'file', status: 'audited', note: 'Updated to track .claude/commands/, backend/.cache already ignored' },
      { name: 'noisemaker-auditor.tsx', type: 'file', status: 'pending', note: 'Old version — superseded by noisemaker_Code_Auditor.jsx' },
      { name: 'cleanup/', type: 'folder', status: 'pending', note: 'Leftover from previous cleanup session' },
      {
        name: 'backend',
        type: 'folder',
        children: [
          { name: 'main.py', type: 'file', status: 'audited', note: 'Entry point — all routes registered, CORS configured' },
          { name: '__init__.py', type: 'file', status: 'pending' },
          { name: '.cache', type: 'file', status: 'pending', note: 'Should be gitignored' },
          { name: 'requirements.txt', type: 'file', status: 'pending' },
          { name: 'STRIPE_SETUP_GUIDE.md', type: 'file', status: 'pending' },
          { name: 'template.yaml', type: 'file', status: 'audited', note: 'SAM template — Lambda now deployed via AWS CLI instead' },
          {
            name: 'auth',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'environment_loader.py', type: 'file', status: 'pending', note: 'get_platform_credentials' },
              { name: 'user_auth.py', type: 'file', status: 'audited', note: 'Password hashing, sessions. Uses time.time() for created_at' },
            ]
          },
          {
            name: 'community',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'community_integration.py', type: 'file', status: 'pending' },
              { name: 'discord_engagement.py', type: 'file', status: 'pending' },
              { name: 'reddit_engagement.py', type: 'file', status: 'pending' },
            ]
          },
          {
            name: 'config',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'platform_config.py', type: 'file', status: 'pending', note: 'Not in old auditor — investigate' },
            ]
          },
          {
            name: 'content',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'caption_generator.py', type: 'file', status: 'pending' },
              { name: 'content_integration.py', type: 'file', status: 'pending', note: 'Not in old auditor — investigate' },
              { name: 'content_orchestrator.py', type: 'file', status: 'pending' },
              { name: 'image_processor.py', type: 'file', status: 'pending', note: 'Color analysis — D7' },
              { name: 'multi_platform_poster.py', type: 'file', status: 'pending' },
              { name: 'template_manager.py', type: 'file', status: 'pending' },
              { name: '.vscode/', type: 'folder', status: 'pending', note: '⚠ Agent leftover — verify then remove' },
            ]
          },
          {
            name: 'data',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'dynamodb_client.py', type: 'file', status: 'fixed', note: 'Float→Decimal conversion added' },
              { name: 'song_manager.py', type: 'file', status: 'fixed', note: 'initial_days fixed, stream_count removed' },
              { name: 'user_manager.py', type: 'file', status: 'fixed', note: 'REWRITTEN: milestone system, dead baseline funcs removed' },
              { name: 'platform_oauth_manager.py', type: 'file', status: 'audited', note: 'CRITICAL — writes to missing table noisemaker-platform-connections' },
            ]
          },
          {
            name: 'examples',
            type: 'folder',
            children: [
              { name: 'oauth_integration_examples.py', type: 'file', status: 'pending' },
            ]
          },
          {
            name: 'marketplace',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'artwork_analytics.py', type: 'file', status: 'pending' },
              { name: 'frank_art_cleanup.py', type: 'file', status: 'pending', note: 'Not in old auditor — investigate' },
              { name: 'frank_art_generator.py', type: 'file', status: 'fixed', note: 'Lambda rebuilt Feb 10. Linux Pillow fix. 4 imgs/run, pool at 35.' },
              { name: 'frank_art_integration.py', type: 'file', status: 'pending' },
              { name: 'frank_art_manager.py', type: 'file', status: 'pending' },
              { name: 'requirements.txt', type: 'file', status: 'pending' },
              { name: '.claude/', type: 'folder', status: 'pending', note: '⚠ Agent leftover — verify then remove' },
            ]
          },
          {
            name: 'middleware',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'auth.py', type: 'file', status: 'pending', note: 'get_current_user_id' },
            ]
          },
          {
            name: 'models',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'schemas.py', type: 'file', status: 'audited', note: '270 lines. All Pydantic request/response models' },
            ]
          },
          {
            name: 'notifications',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'milestone_tracker.py', type: 'file', status: 'fixed', note: 'Complete rewrite: pure detection functions, no classes' },
            ]
          },
          {
            name: 'routes',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'auth.py', type: 'file', status: 'fixed', note: 'Dead MilestoneTracker + initialize_baseline_collection removed' },
              { name: 'dashboard.py', type: 'file', status: 'audited', note: 'Partial audit. Milestone compat verified.' },
              { name: 'frank_art.py', type: 'file', status: 'fixed', note: '/my-collection removed. CORS fixed.' },
              { name: 'payment.py', type: 'file', status: 'fixed', note: 'Baseline trigger + webhook sync + idempotency guard' },
              { name: 'platforms.py', type: 'file', status: 'audited', note: 'BUG: state=None in callback. Default limit fallback 3.' },
              { name: 'songs.py', type: 'file', status: 'audited', note: '4 endpoints mapped, deps traced' },
            ]
          },
          {
            name: 'scheduler',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'cron_manager.py', type: 'file', status: 'pending' },
              { name: 'daily_processor.py', type: 'file', status: 'pending', note: 'NEXT TO AUDIT — core 9PM daily job' },
              { name: 'monthly_baseline_recalculator.py', type: 'file', status: 'pending' },
              { name: 'posting_schedule.py', type: 'file', status: 'pending' },
              { name: '.claude/', type: 'folder', status: 'pending', note: '⚠ Agent leftover — verify then remove' },
            ]
          },
          {
            name: 'scripts',
            type: 'folder',
            children: [
              { name: 'add_email_gsi.py', type: 'file', status: 'pending' },
              { name: 'create_dynamodb_tables.py', type: 'file', status: 'pending' },
              { name: 'create_oauth_tables.py', type: 'file', status: 'pending' },
              { name: 'create_test_user.py', type: 'file', status: 'pending' },
              {
                name: 'oauth_tests',
                type: 'folder',
                children: [
                  { name: 'test_all_platforms.py', type: 'file', status: 'pending' },
                  { name: 'test_discord.py', type: 'file', status: 'pending' },
                  { name: 'test_facebook.py', type: 'file', status: 'pending' },
                  { name: 'test_instagram.py', type: 'file', status: 'pending' },
                  { name: 'test_reddit.py', type: 'file', status: 'pending' },
                  { name: 'test_threads.py', type: 'file', status: 'pending' },
                  { name: 'test_tiktok.py', type: 'file', status: 'pending' },
                  { name: 'test_twitter.py', type: 'file', status: 'pending' },
                  { name: 'test_youtube.py', type: 'file', status: 'pending' },
                ]
              },
            ]
          },
          {
            name: 'spotify',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'baseline_calculator.py', type: 'file', status: 'fixed', note: 'Min baseline removed. Triggered by payment.py now.' },
              { name: 'fire_mode_analyzer.py', type: 'file', status: 'fixed', note: 'Complete rewrite: levels, 5-day window, consecutive-day exit' },
              { name: 'popularity_tracker.py', type: 'file', status: 'audited', note: 'Never invoked — explains D1/D2.' },
              { name: 'spotipy_client.py', type: 'file', status: 'audited', note: 'Works correctly but not invoked for tracking.' },
            ]
          },
          {
            name: 'templates',
            type: 'folder',
            status: 'pending',
            note: 'Not in old auditor — investigate contents'
          },
          {
            name: 'tests',
            type: 'folder',
            children: [
              { name: '__init__.py', type: 'file', status: 'pending' },
              { name: 'test_auth_and_payment.py', type: 'file', status: 'pending' },
              { name: 'test_fire_mode_integration.py', type: 'file', status: 'pending' },
              { name: 'test_marketplace_routes.py', type: 'file', status: 'pending' },
              { name: 'test_phase_1_and_2.py', type: 'file', status: 'pending' },
            ]
          },
        ]
      },
      {
        name: 'frontend',
        type: 'folder',
        children: [
          { name: '.eslintrc.json', type: 'file', status: 'pending' },
          { name: 'components.json', type: 'file', status: 'pending' },
          { name: 'next-env.d.ts', type: 'file', status: 'pending' },
          { name: 'package.json', type: 'file', status: 'pending' },
          { name: 'package-lock.json', type: 'file', status: 'pending' },
          { name: 'tailwind.config.ts', type: 'file', status: 'pending' },
          { name: 'tsconfig.json', type: 'file', status: 'pending' },
          {
            name: 'src',
            type: 'folder',
            children: [
              { name: 'middleware.ts', type: 'file', status: 'pending', note: 'Route protection' },
              {
                name: 'app',
                type: 'folder',
                children: [
                  { name: 'page.tsx', type: 'file', status: 'pending', note: 'Landing page — which variant is active?' },
                  { name: 'layout.tsx', type: 'file', status: 'pending' },
                  { name: 'landing-aurora.tsx', type: 'file', status: 'pending', note: 'Landing variant — check if imported' },
                  { name: 'landing-monolith.tsx', type: 'file', status: 'pending', note: 'Landing variant — check if imported' },
                  { name: 'landing-noir-luxe.tsx', type: 'file', status: 'pending', note: 'Landing variant — check if imported' },
                  { name: 'page-genz.tsx', type: 'file', status: 'pending', note: 'Landing variant — may be ACTIVE, check imports' },
                  {
                    name: 'onboarding',
                    type: 'folder',
                    children: [
                      { name: 'how-it-works/page.tsx', type: 'file', status: 'pending' },
                      { name: 'platforms/page.tsx', type: 'file', status: 'pending', note: 'Connect 1-8 platforms' },
                      { name: 'platforms/platforms-v*.tsx', type: 'file', status: 'pending', note: 'Old variant? Check if imported' },
                      { name: 'how-it-works-2/page.tsx', type: 'file', status: 'pending' },
                      { name: 'add-songs/page.tsx', type: 'file', status: 'fixed', note: 'Updated API signature Feb 4' },
                    ]
                  },
                  {
                    name: 'dashboard',
                    type: 'folder',
                    children: [
                      { name: 'page.tsx', type: 'file', status: 'pending' },
                      { name: 'garage/page.tsx', type: 'file', status: 'pending', note: "Frank's Garage" },
                    ]
                  },
                  { name: 'pricing/page.tsx', type: 'file', status: 'pending' },
                  { name: 'pricing/pricing-v2.tsx', type: 'file', status: 'pending', note: 'Old variant? Check if imported' },
                  { name: 'payment/success/page.tsx', type: 'file', status: 'pending' },
                  { name: 'milestone/[type]/page.tsx', type: 'file', status: 'pending' },
                  {
                    name: 'test-designs',
                    type: 'folder',
                    status: 'pending',
                    note: 'aurora/monolith/noir-luxe test pages — check if still needed'
                  },
                ]
              },
              {
                name: 'lib',
                type: 'folder',
                children: [
                  { name: 'api.ts', type: 'file', status: 'fixed', note: 'getUserSongs path fixed, user_id removed' },
                  { name: 'auth.ts', type: 'file', status: 'pending' },
                  { name: 'auth-options.ts', type: 'file', status: 'pending', note: 'NextAuth config' },
                  { name: 'constants.ts', type: 'file', status: 'pending' },
                  { name: 'ssm-loader.ts', type: 'file', status: 'pending', note: 'AWS SSM Parameter Store loader' },
                  { name: 'utils.ts', type: 'file', status: 'pending' },
                ]
              },
              {
                name: 'components',
                type: 'folder',
                children: [
                  { name: 'PlatformIcon.tsx', type: 'file', status: 'pending' },
                  { name: 'PostReviewModal.tsx', type: 'file', status: 'pending' },
                  { name: 'PricingCard.tsx', type: 'file', status: 'pending' },
                  { name: 'Providers.tsx', type: 'file', status: 'pending' },
                  { name: 'SongCard.tsx', type: 'file', status: 'pending' },
                  { name: 'effects/ParticleBackground.tsx', type: 'file', status: 'pending' },
                  { name: 'effects/SpotlightCursor.tsx', type: 'file', status: 'pending' },
                  { name: 'effects/StageFootlights.tsx', type: 'file', status: 'pending' },
                  { name: 'effects/WaveformVisualizer.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/button.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/card.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/MarqueeButton.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/PlatformOrb.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/PlatformShowcase.tsx', type: 'file', status: 'pending' },
                  { name: 'ui/SignupButtons.tsx', type: 'file', status: 'pending' },
                ]
              },
              {
                name: 'types',
                type: 'folder',
                children: [
                  { name: 'index.ts', type: 'file', status: 'pending' },
                  { name: 'next-auth.d.ts', type: 'file', status: 'pending' },
                ]
              },
            ]
          },
        ]
      },
      {
        name: 'docs',
        type: 'folder',
        children: [
          { name: 'OAUTH_PERMISSIONS_GUIDE.md', type: 'file', status: 'pending', note: 'Verify if current' },
          { name: 'POST_SCHEDULES_TODO.md', type: 'file', status: 'pending', note: 'Verify if current' },
          { name: 'SYSTEMS_TODO.md', type: 'file', status: 'pending', note: 'Verify if current' },
          { name: 'TECH_STACK.md', type: 'file', status: 'pending', note: 'Verify if current' },
          {
            name: 'skills',
            type: 'folder',
            status: 'pending',
            note: '6 skill folders from Jan 8 — all stale, need review before agents read them'
          },
        ]
      },
    ]
  };

  // ============================================
  // ONBOARDING FLOW
  // ============================================
  const onboardingFlow = [
    { step: 1, name: "Signup", status: "complete" },
    { step: 2, name: "Payment (Stripe)", status: "complete" },
    { step: 3, name: "Milestone Video", status: "complete" },
    { step: 4, name: "How It Works (1)", status: "pending", note: "Placeholder text — Tre needs to write copy" },
    { step: 5, name: "Platform Connections", status: "issues", highlight: true, note: "Broken. May require app review/approval from platforms for OAuth scopes. Code needs deep inspection." },
    { step: 6, name: "How It Works (2)", status: "pending", note: "Placeholder text — Tre needs to write copy" },
    { step: 7, name: "Songs Upload (1-3)", status: "pending", note: "Unknown status — needs re-testing" },
    { step: 8, name: "Dashboard", status: "pending", note: "Early development — just beginning" },
  ];

  // ============================================
  // HELPER FUNCTIONS
  // ============================================
  const getStatusColor = (status) => {
    const colors = {
      complete: 'text-green-400', tested: 'text-green-400', fixed: 'text-green-400', done: 'text-green-400', answered: 'text-green-400', audited: 'text-green-400',
      current: 'text-yellow-400', analyzing: 'text-yellow-400', next: 'text-yellow-400',
      active: 'text-blue-400',
      pending: 'text-gray-500', queued: 'text-gray-500',
      open: 'text-red-400', issues: 'text-red-400',
      critical: 'text-red-400', medium: 'text-yellow-400', low: 'text-gray-400',
    };
    return colors[status] || 'text-gray-400';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'complete': case 'tested': case 'fixed': case 'done': case 'answered': case 'audited':
        return <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />;
      case 'current': case 'analyzing': case 'next':
        return <Circle className="w-4 h-4 text-yellow-400 fill-yellow-400 flex-shrink-0" />;
      case 'open': case 'issues':
        return <HelpCircle className="w-4 h-4 text-red-400 flex-shrink-0" />;
      case 'active':
        return <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />;
      default:
        return <Circle className="w-4 h-4 text-gray-500 flex-shrink-0" />;
    }
  };

  const getSmallStatusIcon = (status) => {
    switch (status) {
      case 'complete': case 'tested': case 'fixed': case 'done': case 'answered': case 'audited':
        return <CheckCircle className="w-3 h-3 text-green-400 flex-shrink-0" />;
      case 'current': case 'analyzing': case 'next':
        return <Circle className="w-3 h-3 text-yellow-400 fill-yellow-400 flex-shrink-0" />;
      case 'open': case 'issues':
        return <HelpCircle className="w-3 h-3 text-red-400 flex-shrink-0" />;
      default:
        return <Circle className="w-3 h-3 text-gray-500 flex-shrink-0" />;
    }
  };

  const getPriorityBadge = (priority) => {
    const styles = {
      critical: 'bg-red-900/40 text-red-300 border-red-700',
      medium: 'bg-yellow-900/30 text-yellow-300 border-yellow-700',
      low: 'bg-gray-800 text-gray-400 border-gray-600',
    };
    return (
      <span className={`text-[10px] px-1.5 py-0.5 rounded border ${styles[priority] || styles.low}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  // Count file statuses
  const countFileStatuses = (node) => {
    let counts = { audited: 0, fixed: 0, done: 0, pending: 0, total: 0 };
    if (node.type === 'file') {
      counts.total = 1;
      if (['audited', 'done'].includes(node.status)) counts.audited = 1;
      else if (node.status === 'fixed') counts.fixed = 1;
      else counts.pending = 1;
    }
    if (node.children) {
      node.children.forEach(child => {
        const c = countFileStatuses(child);
        counts.audited += c.audited;
        counts.fixed += c.fixed;
        counts.pending += c.pending;
        counts.total += c.total;
      });
    }
    return counts;
  };

  const treeCounts = countFileStatuses(fileTree);

  const renderTree = (node, path = '', depth = 0) => {
    const fullPath = path ? `${path}/${node.name}` : node.name;
    const isExpanded = expandedFolders.includes(fullPath);

    if (treeFilter !== 'all') {
      if (node.type === 'file' && node.status !== treeFilter) return null;
    }

    if (node.type === 'folder') {
      return (
        <div key={fullPath} style={{ marginLeft: depth * 14 }}>
          <div
            className="flex items-center gap-1.5 py-0.5 cursor-pointer hover:bg-gray-800/50 rounded px-1"
            onClick={() => toggleFolder(fullPath)}
          >
            <span className="text-gray-600 text-[10px] w-3">{node.children ? (isExpanded ? '▼' : '▶') : ''}</span>
            <FolderTree className="w-3 h-3 text-yellow-600" />
            <span className="text-xs text-gray-300">{node.name}</span>
            {node.note && <span className="text-[10px] text-gray-600 ml-1">— {node.note}</span>}
          </div>
          {isExpanded && node.children && (
            <div>{node.children.map(child => renderTree(child, fullPath, depth + 1))}</div>
          )}
        </div>
      );
    }

    return (
      <div key={fullPath} style={{ marginLeft: depth * 14 }} className="flex items-center gap-1.5 py-0.5 px-1">
        {getSmallStatusIcon(node.status)}
        <FileCode className="w-3 h-3 text-blue-500/50" />
        <span className={`text-xs ${getStatusColor(node.status)}`}>{node.name}</span>
        {node.note && <span className="text-[10px] text-gray-600 ml-1">— {node.note}</span>}
      </div>
    );
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'issues', label: 'Issues', icon: AlertCircle },
    { id: 'tree', label: 'File Tree', icon: FolderTree },
    { id: 'files', label: 'Audit Queue', icon: GitBranch },
    { id: 'questions', label: 'Questions', icon: HelpCircle },
    { id: 'tables', label: 'DynamoDB', icon: Database },
    { id: 'flow', label: 'Data Flow', icon: ArrowRight },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 font-mono">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#0d0d14]">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
            <h1 className="text-xl font-bold tracking-tight">
              <span className="text-purple-400">NOiSEMaKER</span>
              <span className="text-gray-500 ml-2">Code Auditor</span>
            </h1>
            <span className="text-[10px] text-gray-600 border border-gray-800 px-1.5 py-0.5 rounded ml-auto">
              Last session: Feb 10, 2026
            </span>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-gray-500 mt-2">
            {Object.entries(techStack).map(([k, v]) => (
              <span key={k}><span className="text-gray-600">{k}:</span> {v}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-800 bg-[#0d0d14]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex gap-0 overflow-x-auto">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-1.5 px-4 py-2.5 text-xs transition-colors border-b-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-purple-400'
                      : 'border-transparent text-gray-600 hover:text-gray-400'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-4">

        {/* ===== OVERVIEW TAB ===== */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {[
                { label: 'Fixed', value: completedFixes.length, color: 'text-green-400' },
                { label: 'Critical Issues', value: openIssues.filter(i => i.priority === 'critical').length, color: 'text-red-400' },
                { label: 'Questions', value: `${openQuestions.filter(q => q.status === 'answered').length}/${openQuestions.length}`, color: 'text-blue-400' },
                { label: 'Files Audited', value: `${treeCounts.audited + treeCounts.fixed}/${treeCounts.total}`, color: 'text-purple-400' },
                { label: 'Queue', value: fileQueue.length, color: 'text-yellow-400' },
              ].map((stat, i) => (
                <div key={i} className="bg-[#111118] rounded-lg p-3 border border-gray-800">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider">{stat.label}</p>
                  <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
                </div>
              ))}
            </div>

            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Onboarding Flow</h3>
              <div className="flex items-center gap-1 overflow-x-auto pb-2">
                {onboardingFlow.map((step, i) => (
                  <React.Fragment key={step.step}>
                    <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs whitespace-nowrap ${
                      step.highlight ? 'bg-green-900/20 border border-green-700' : 'bg-[#0a0a0f] border border-gray-800'
                    }`}>
                      {getStatusIcon(step.status)}
                      <span className={getStatusColor(step.status)}>{step.name}</span>
                    </div>
                    {i < onboardingFlow.length - 1 && <ArrowRight className="w-3 h-3 text-gray-700 flex-shrink-0" />}
                  </React.Fragment>
                ))}
              </div>
            </div>

            <div className="bg-[#111118] rounded-lg p-4 border border-red-900/30">
              <h3 className="text-xs text-red-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <AlertCircle className="w-3.5 h-3.5" /> Critical Open Issues
              </h3>
              <div className="space-y-2">
                {openIssues.filter(i => i.priority === 'critical').map(issue => (
                  <div key={issue.id} className="flex items-start gap-2 text-xs bg-[#0a0a0f] rounded p-2 border border-gray-800">
                    <span className="text-red-500 font-bold w-7">{issue.id}</span>
                    <div>
                      <p className="text-gray-200">{issue.title}</p>
                      <p className="text-gray-600 mt-0.5">{issue.location}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#111118] rounded-lg p-3 border border-yellow-900/30">
              <p className="text-xs text-yellow-400 flex items-center gap-2">
                <ArrowRight className="w-3.5 h-3.5" />
                Next: Audit <span className="text-yellow-300 font-bold">scheduler/daily_processor.py</span>
                <span className="text-gray-600">— core product, 9 PM daily job</span>
              </p>
            </div>
          </div>
        )}

        {/* ===== ISSUES TAB ===== */}
        {activeTab === 'issues' && (
          <div className="space-y-4">
            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Open Issues ({openIssues.length})</h3>
              <div className="space-y-2">
                {openIssues.map(issue => (
                  <div key={issue.id} className="bg-[#0a0a0f] rounded p-3 border border-gray-800">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-500 text-xs font-bold w-7">{issue.id}</span>
                      {getPriorityBadge(issue.priority)}
                      <span className="text-xs text-gray-200 flex-1">{issue.title}</span>
                    </div>
                    <p className="text-[10px] text-gray-600 ml-9">{issue.location} — {issue.description}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <h3 className="text-xs text-green-400 uppercase tracking-wider mb-3">Fixed ({completedFixes.length})</h3>
              <div className="space-y-1">
                {completedFixes.map((fix, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1.5 border-b border-gray-800/50 last:border-0">
                    <CheckCircle className="w-3 h-3 text-green-600 flex-shrink-0" />
                    <span className="text-green-500 w-7">{fix.id}</span>
                    <span className="text-gray-400 flex-1">{fix.file} — {fix.fix}</span>
                    <span className="text-gray-600 text-[10px]">{fix.date}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== FILE TREE TAB ===== */}
        {activeTab === 'tree' && (
          <div className="space-y-4">
            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs text-gray-400 uppercase tracking-wider">
                  Complete File Tree — {treeCounts.total} files ({treeCounts.audited + treeCounts.fixed} audited, {treeCounts.pending} pending)
                </h3>
                <div className="flex gap-1">
                  {['all', 'pending', 'fixed', 'audited'].map(f => (
                    <button key={f} onClick={() => setTreeFilter(f)}
                      className={`text-[10px] px-2 py-0.5 rounded ${treeFilter === f ? 'bg-purple-900/40 text-purple-300 border border-purple-700' : 'text-gray-600 border border-gray-800'}`}>
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <div className="max-h-[600px] overflow-y-auto bg-[#0a0a0f] rounded p-3 border border-gray-800">
                {renderTree(fileTree)}
              </div>
              <div className="flex flex-wrap gap-3 mt-3 text-[10px] text-gray-600">
                <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-green-400" /> Audited/Fixed</span>
                <span className="flex items-center gap-1"><Circle className="w-3 h-3 text-yellow-400 fill-yellow-400" /> Next</span>
                <span className="flex items-center gap-1"><Circle className="w-3 h-3 text-gray-500" /> Pending</span>
                <span className="flex items-center gap-1"><HelpCircle className="w-3 h-3 text-red-400" /> Has issues</span>
              </div>
            </div>
          </div>
        )}

        {/* ===== AUDIT QUEUE TAB ===== */}
        {activeTab === 'files' && (
          <div className="space-y-4">
            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Files Analyzed ({analyzedFiles.length})</h3>
              <div className="space-y-2">
                {analyzedFiles.map((file, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs bg-[#0a0a0f] rounded p-2 border border-gray-800">
                    {getStatusIcon(file.status)}
                    <span className="text-green-400 font-mono">{file.path}</span>
                    <span className="text-gray-600 ml-auto text-[10px] max-w-xs truncate">{file.notes}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-[#111118] rounded-lg p-4 border border-yellow-900/30">
              <h3 className="text-xs text-yellow-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <GitBranch className="w-3.5 h-3.5" /> Queue ({fileQueue.length} files)
              </h3>
              <div className="space-y-2">
                {fileQueue.map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs bg-[#0a0a0f] rounded p-2 border border-gray-800">
                    <span className="text-gray-600 w-5">#{item.priority}</span>
                    {getStatusIcon(item.status)}
                    <span className="text-gray-300 font-mono flex-1">{item.file}</span>
                    <span className="text-gray-600 text-[10px] max-w-xs truncate">{item.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== QUESTIONS TAB ===== */}
        {activeTab === 'questions' && (
          <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
            <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">
              Questions — {openQuestions.filter(q => q.status === 'answered').length} answered, {openQuestions.filter(q => q.status === 'open').length} open
            </h3>
            {['Data Storage', 'Color Analysis', 'Baseline Popularity', 'Daily Processor', 'Frontend', 'Business Logic', 'Architecture'].map(category => {
              const qs = openQuestions.filter(q => q.category === category);
              if (qs.length === 0) return null;
              return (
                <div key={category} className="mb-4">
                  <h4 className="text-[10px] text-gray-500 uppercase tracking-wider mb-2 border-b border-gray-800 pb-1">{category}</h4>
                  <div className="space-y-1.5">
                    {qs.map(q => (
                      <div key={q.id} className="text-xs bg-[#0a0a0f] rounded p-2 border border-gray-800">
                        <div className="flex items-start gap-2">
                          {getStatusIcon(q.status)}
                          <div className="flex-1">
                            <p className={q.status === 'answered' ? 'text-gray-400 line-through' : 'text-gray-200'}>{q.question}</p>
                            {q.answer && <p className="text-green-400/80 text-[10px] mt-1">↳ {q.answer}</p>}
                          </div>
                          <span className="text-gray-700 text-[10px]">#{q.id}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ===== DYNAMODB TAB ===== */}
        {activeTab === 'tables' && (
          <div className="space-y-4">
            <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
              <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Active Tables (9 total, 3 with data)</h3>
              <div className="space-y-2">
                {tableStatus.map((table, i) => (
                  <div key={i} className="bg-[#0a0a0f] rounded p-3 border border-gray-800">
                    <div className="flex items-center gap-2 mb-1">
                      {getStatusIcon(table.status)}
                      <span className="text-xs text-blue-400 font-mono">{table.name}</span>
                      <span className="text-[10px] text-gray-600 ml-auto">{table.items} items · {table.size}</span>
                    </div>
                    {table.issue && <p className="text-[10px] text-red-400/70 ml-6">⚠ {table.issue}</p>}
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-[#111118] rounded-lg p-3 border border-gray-800">
              <p className="text-xs text-gray-500">
                9 tables total. Purged from 26 on Feb 8. All confirmed active.
              </p>
            </div>
          </div>
        )}

        {/* ===== DATA FLOW TAB ===== */}
        {activeTab === 'flow' && (
          <div className="bg-[#111118] rounded-lg p-4 border border-gray-800">
            <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Data Flow: POST /api/songs/add-from-url</h3>
            <div className="space-y-1.5">
              {[
                { label: "Frontend POST /api/songs/add-from-url", color: "blue", note: "request" },
                { label: "Validate: spotify_url, initial_days (0|14|28), release_date", color: "gray", note: "validation" },
                { label: "extract_spotify_track_id() → track_id", color: "gray", note: "process" },
                { label: "song_manager.get_user_active_songs() → check < 3", color: "yellow", note: "db-read" },
                { label: "get_platform_credentials('spotify') → creds", color: "purple", note: "auth" },
                { label: "get_track_information() → metadata from Spotify", color: "green", note: "external" },
                { label: "user_manager.get_user_profile() → verify artist", color: "yellow", note: "db-read" },
                { label: "song_manager.add_song() → noisemaker-songs ✅ (Decimal fix applied)", color: "teal", note: "db-write" },
                { label: "award_art_tokens_for_song() → update balance", color: "yellow", note: "db-write" },
                { label: "Return success → frontend redirects to /dashboard", color: "blue", note: "response" },
              ].map((step, i) => {
                const colorMap = {
                  red: 'bg-red-900/20 border-red-800 text-red-300',
                  yellow: 'bg-yellow-900/15 border-yellow-800/60 text-yellow-300',
                  green: 'bg-green-900/15 border-green-800/60 text-green-300',
                  purple: 'bg-purple-900/15 border-purple-800/60 text-purple-300',
                  blue: 'bg-blue-900/15 border-blue-800/60 text-blue-300',
                  teal: 'bg-teal-900/15 border-teal-800/60 text-teal-300',
                  gray: 'bg-[#0a0a0f] border-gray-800 text-gray-400',
                };
                return (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-gray-700 w-5 text-[10px] text-right">{i + 1}</span>
                    <div className={`flex-1 px-3 py-1.5 rounded text-xs border ${colorMap[step.color] || colorMap.gray}`}>
                      {step.label}
                    </div>
                    <span className="text-[10px] text-gray-700 w-14">{step.note}</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex flex-wrap gap-3 text-[10px] text-gray-600">
              <span className="text-blue-400">● Request/Response</span>
              <span className="text-yellow-400">● DB Read/Write</span>
              <span className="text-green-400">● External API</span>
              <span className="text-purple-400">● Auth</span>
              <span className="text-teal-400">● Fixed</span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-800 mt-8 py-3 text-center text-[10px] text-gray-700">
        NOiSEMaKER Code Auditor · ADUSON Inc. · No changes without explicit approval
      </div>
    </div>
  );
}
