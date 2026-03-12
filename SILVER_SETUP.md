# Silver Tier Setup Guide

## Prerequisites Completed

✅ Bronze Tier complete
✅ Qwen Code as the brain
✅ credentials.json for Gmail API in project root
✅ token.json generated (Gmail OAuth token)

## Quick Start

```bash
# Generate Gmail token (already done!)
python scripts/generate_gmail_token.py

# Run Gmail Watcher
cd watchers
python gmail_watcher.py ../AI_Employee_Vault

# Run LinkedIn Watcher (after login)
python linkedin_watcher.py ../AI_Employee_Vault

# Run Orchestrator
python orchestrator.py AI_Employee_Vault
```

### 1. Gmail Watcher

**Status:** ✅ Ready to use (token.json generated)

**Setup:**

The Gmail API token has already been generated from your credentials.json!

Token location: `token.json`

**Run Gmail Watcher:**
```bash
cd watchers
python gmail_watcher.py ../AI_Employee_Vault
```

**Regenerate token if needed:**
```bash
python scripts/generate_gmail_token.py
```

**Verify token:**
```bash
python scripts/generate_gmail_token.py --verify
```

### 2. LinkedIn Watcher

**Status:** ✅ Created, needs login

**Setup:**

```bash
# 1. Install Playwright (if not done)
pip install playwright
playwright install chromium

# 2. Login to LinkedIn (opens browser)
cd watchers
python linkedin_watcher.py --login
```

**What happens during login:**
1. Browser opens to LinkedIn login page
2. You login to your LinkedIn account
3. Session is saved to `linkedin-session/` folder
4. Close browser when done

**Run LinkedIn Watcher:**
```bash
python linkedin_watcher.py ../AI_Employee_Vault
```

### 3. LinkedIn Poster

**Status:** ✅ Created

**Post immediately:**
```bash
python linkedin_poster.py --post "Your post content here"
```

**Schedule post:**
```bash
python linkedin_poster.py --post "Your content" --schedule "2026-03-06T14:00:00"
```

**Login to LinkedIn for posting:**
```bash
python linkedin_poster.py --login
```

## Running All Watchers

### Option 1: Multiple Terminals

```bash
# Terminal 1 - File Watcher
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault

# Terminal 2 - Gmail Watcher
python gmail_watcher.py ../AI_Employee_Vault

# Terminal 3 - LinkedIn Watcher
python linkedin_watcher.py ../AI_Employee_Vault

# Terminal 4 - Orchestrator
python orchestrator.py AI_Employee_Vault
```

### Option 2: Windows Task Scheduler

```powershell
# Create scheduled task for orchestrator
powershell -ExecutionPolicy Bypass -File scripts\setup-scheduler.ps1
```

## Testing

### Test Gmail Watcher

```bash
# Send yourself a test email with subject "Test"
# Wait 2 minutes (check interval)
# Check AI_Employee_Vault/Needs_Action/ for EMAIL_*.md file
```

### Test LinkedIn Watcher

```bash
# Check for notifications manually first
# Then run watcher
python linkedin_watcher.py ../AI_Employee_Vault --interval 60
# Check AI_Employee_Vault/Needs_Action/ for LINKEDIN_*.md files
```

### Test LinkedIn Poster

```bash
# Test post
python linkedin_poster.py --post "Testing AI Employee Silver Tier! #AI #Automation"
```

## Troubleshooting

### Gmail Watcher Issues

**Error: Credentials not found**
```bash
# Make sure credentials.json is in project root
dir credentials.json
```

**Error: Token expired**
```bash
# Delete old token and re-authenticate
del token.json
python gmail_watcher.py --auth
```

### LinkedIn Watcher Issues

**Error: Browser won't start**
```bash
# Reinstall Chromium
playwright install chromium
```

**Error: Session expired**
```bash
# Clear session and re-login
rmdir /s /q linkedin-session
python linkedin_watcher.py --login
```

### LinkedIn Poster Issues

**Error: Can't find post button**
- Make sure you're logged in to LinkedIn
- Run `python linkedin_poster.py --login` first
- LinkedIn may have updated UI - check selectors

## File Structure

```
Personal-AI-Employ/
├── credentials.json         # Gmail API credentials (YOU HAVE THIS)
├── token.json              # Gmail OAuth token (AUTO-GENERATED)
├── linkedin-session/       # LinkedIn browser session (AUTO-GENERATED)
├── watchers/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py     # ✅ NEW
│   ├── linkedin_watcher.py  # ✅ NEW
│   ├── linkedin_poster.py   # ✅ NEW
│   └── requirements.txt
├── AI_Employee_Vault/
│   ├── Needs_Action/
│   │   ├── EMAIL_*.md       # From Gmail
│   │   └── LINKEDIN_*.md    # From LinkedIn
│   └── ...
└── .qwen/skills/
    ├── gmail-watcher/
    ├── linkedin-mcp/
    └── ...
```

## Next Steps

1. **Complete Gmail Auth:**
   ```bash
   cd watchers
   python gmail_watcher.py --auth
   ```

2. **Complete LinkedIn Login:**
   ```bash
   python linkedin_watcher.py --login
   ```

3. **Test the Flow:**
   - Send yourself a test email
   - Wait for watcher to detect it
   - Check Needs_Action folder
   - Orchestrator should trigger Qwen Code

4. **Post to LinkedIn:**
   ```bash
   python linkedin_poster.py --post "Excited to share my AI Employee project! #AI #Automation"
   ```

## Silver Tier Checklist

- [ ] Gmail Watcher authenticated
- [ ] Gmail Watcher running
- [ ] LinkedIn Watcher logged in
- [ ] LinkedIn Watcher running
- [ ] Orchestrator running
- [ ] Test email detected and processed
- [ ] Test LinkedIn notification detected
- [ ] Test LinkedIn post published

---

*Silver Tier implementation complete! 🥈*
