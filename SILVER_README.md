# AI Employee - Silver Tier

## Overview

This is the **Silver Tier** implementation of the Personal AI Employee hackathon. It extends the Bronze Tier with multiple watchers, MCP servers, and automated scheduling.

## What's Included

### ✅ Silver Tier Deliverables

- [x] All Bronze Tier requirements
- [x] Two or more Watcher scripts (Gmail + WhatsApp + File System)
- [x] One working MCP server for external action (Email MCP)
- [x] Human-in-the-loop approval workflow
- [x] Basic scheduling via Task Scheduler (Windows) / cron (Linux/Mac)
- [x] All AI functionality implemented as Agent Skills

## Project Structure

```
Personal-AI-Employ/
├── AI_Employee_Vault/       # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Plans/
│   ├── Briefings/
│   ├── Accounting/
│   ├── Logs/
│   └── Invoices/
├── watchers/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py      # NEW: Silver Tier
│   ├── whatsapp_watcher.py   # NEW: Silver Tier
│   └── requirements.txt
├── orchestrator.py
├── scripts/
│   └── setup-scheduler.ps1   # NEW: Silver Tier
├── .qwen/skills/
│   ├── browsing-with-playwright/
│   ├── vault-operations/
│   ├── email-mcp/            # NEW: Silver Tier
│   ├── gmail-watcher/        # NEW: Silver Tier
│   ├── whatsapp-watcher/     # NEW: Silver Tier
│   ├── scheduler/            # NEW: Silver Tier
│   └── approval-workflow/    # NEW: Silver Tier
└── SILVER_README.md
```

## Agent Skills

### Bronze Tier Skills

| Skill | Purpose |
|-------|---------|
| `vault-operations` | Read/write/manage vault files |
| `browsing-with-playwright` | Browser automation |

### Silver Tier Skills (NEW)

| Skill | Purpose |
|-------|---------|
| `email-mcp` | Send/draft/search emails via Gmail |
| `gmail-watcher` | Monitor Gmail for new messages |
| `whatsapp-watcher` | Monitor WhatsApp Web for messages |
| `scheduler` | Schedule recurring tasks |
| `approval-workflow` | Human-in-the-loop approvals |

## Setup Instructions

### 1. Install Dependencies

```bash
# Watcher dependencies
cd watchers
pip install -r requirements.txt

# Playwright for WhatsApp
pip install playwright
playwright install chromium
```

### 2. Configure Gmail API (for Email MCP + Gmail Watcher)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to a secure location
6. First-time auth:
   ```bash
   python watchers/gmail_watcher.py --auth
   ```

### 3. Configure WhatsApp Web (for WhatsApp Watcher)

```bash
# First run - scan QR code
python watchers/whatsapp_watcher.py --login
```

### 4. Setup Task Scheduler (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-scheduler.ps1
```

### 5. Configure MCP Servers

Add to your MCP configuration:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "npx",
      "args": ["@anthropic/email-mcp@latest"],
      "env": {
        "GMAIL_CREDENTIALS": "C:\\path\\to\\credentials.json"
      }
    }
  ]
}
```

## Usage

### Start All Watchers

```bash
# Terminal 1: File Watcher
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault

# Terminal 2: Gmail Watcher
python gmail_watcher.py ../AI_Employee_Vault

# Terminal 3: WhatsApp Watcher
python whatsapp_watcher.py ../AI_Employee_Vault

# Terminal 4: Orchestrator
python orchestrator.py AI_Employee_Vault
```

### Start with Scheduler (Background)

```powershell
# Windows Task Scheduler handles this automatically
# Check status:
Get-ScheduledTask -TaskName "AI_Employee_Orchestrator"
```

## Workflows

### Email Response Workflow

```
Gmail receives email
    ↓
gmail_watcher.py detects
    ↓
Creates: Needs_Action/EMAIL_*.md
    ↓
Orchestrator triggers Qwen Code
    ↓
Qwen reads Company_Handbook
    ↓
Qwen creates approval request
    ↓
Human approves (move to Approved/)
    ↓
Email MCP sends response
    ↓
File moved to Done/
```

### WhatsApp Lead Capture

```
WhatsApp message: "Need pricing info"
    ↓
whatsapp_watcher.py detects keywords
    ↓
Creates: Needs_Action/WHATSAPP_*.md
    ↓
Orchestrator triggers Qwen Code
    ↓
Qwen creates response draft
    ↓
Human approves via approval-workflow
    ↓
Playwright sends WhatsApp reply
    ↓
Lead logged to Business_Goals.md
```

### Scheduled Daily Briefing

```
Task Scheduler triggers at 8 AM
    ↓
orchestrator.py --briefing
    ↓
Qwen reads Needs_Action/, Done/, Accounting/
    ↓
Generates: Briefings/YYYY-MM-DD_Briefing.md
    ↓
Updates Dashboard.md
    ↓
Sends summary email (optional)
```

## Approval Workflow

### Pending Actions

When a sensitive action is detected:

1. **File created:** `Pending_Approval/APPROVE_*.md`
2. **Dashboard updated:** "Awaiting Approval: X"
3. **Human reviews** in Obsidian
4. **Human decides:**
   - Approve: Move to `Approved/`
   - Reject: Move to `Rejected/`
   - Modify: Edit then move to `Approved/`

### Approval Thresholds

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email to known contact | Yes | No |
| Email to new contact | No | Yes |
| Payment < $50 | Yes | No |
| Payment > $100 | No | Always |
| Social media post | Scheduled only | Replies/DMs |

## Testing Checklist

- [ ] Gmail Watcher detects new emails
- [ ] WhatsApp Watcher detects keyword messages
- [ ] File Watcher detects dropped files
- [ ] Orchestrator triggers Qwen Code
- [ ] Approval requests created in Pending_Approval/
- [ ] Moving to Approved/ executes action
- [ ] Dashboard updates with counts
- [ ] Scheduled tasks run automatically

## Troubleshooting

### Gmail Watcher Issues

| Issue | Solution |
|-------|----------|
| Not detecting emails | Check Gmail API quota |
| Auth error | Re-run: `gmail_watcher.py --auth` |
| Duplicate files | Clear processed_ids cache |

### WhatsApp Watcher Issues

| Issue | Solution |
|-------|----------|
| QR code expired | Re-run: `whatsapp_watcher.py --login` |
| Session invalid | Clear session: `--clear-session` |
| Browser crash | Reinstall: `playwright install chromium` |

### Scheduler Issues

| Issue | Solution |
|-------|----------|
| Task not running | Check "Run whether user is logged on" |
| Python not found | Use full path to python.exe |
| Permission denied | Run as administrator |

### Approval Workflow Issues

| Issue | Solution |
|-------|----------|
| File not moving | Close file in other programs |
| Not executing | Check Approved/ folder permissions |
| Duplicate approvals | Clear old Rejected/ files |

## Next Steps (Gold Tier)

To upgrade to Gold Tier, add:

1. **Xero Integration** - Accounting MCP server
2. **Social Media Posting** - Facebook, Instagram, Twitter MCP
3. **CEO Briefing** - Weekly automated business audit
4. **Error Recovery** - Graceful degradation
5. **Comprehensive Logging** - Full audit trail

## Skills Reference

- `vault-operations`: `.qwen/skills/vault-operations/SKILL.md`
- `email-mcp`: `.qwen/skills/email-mcp/SKILL.md`
- `gmail-watcher`: `.qwen/skills/gmail-watcher/SKILL.md`
- `whatsapp-watcher`: `.qwen/skills/whatsapp-watcher/SKILL.md`
- `scheduler`: `.qwen/skills/scheduler/SKILL.md`
- `approval-workflow`: `.qwen/skills/approval-workflow/SKILL.md`

---

*Silver Tier Complete! 🥈*
