---
name: approval-workflow
description: |
  Human-in-the-Loop (HITL) approval workflow for AI Employee. Manages sensitive
  actions that require human approval before execution. Uses file-based approval
  system with Pending_Approval, Approved, and Rejected folders.
---

# Approval Workflow Skill

Human-in-the-Loop approval system for sensitive actions.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Qwen Code      │────▶│ Pending_Approval │────▶│    Human        │
│  (creates req)  │     │  (wait state)    │     │  (reviews)      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌──────────────────┐     ┌───────▼────────┐
                        │    Rejected      │◀────│  Move file     │
                        │  (ignored)       │     │  decision      │
                        └──────────────────┘     └───────┬────────┘
                                                         │
                        ┌──────────────────┐     ┌───────▼────────┐
                        │     Approved     │────▶│  Orchestrator  │
                        │  (execute)       │     │  (runs action) │
                        └──────────────────┘     └─────────────────┘
```

## Approval Thresholds

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email replies | Known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |
| API calls | Read-only | Write, delete, transfer |

## Approval Request Format

When Qwen Code detects a sensitive action:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123
amount: 1500.00
created: 2026-03-05T12:00:00
expires: 2026-03-06T12:00:00
status: pending
priority: normal
---

# Approval Required: Send Email

## Action Details

**Type:** Send Email
**To:** client@example.com
**Subject:** Invoice #123
**Amount:** $1,500.00

## Content

```
Dear Client,

Please find attached invoice #123 for $1,500.00.

Payment is due within 30 days.

Best regards,
Your Name
```

## Why This Requires Approval

- Email contains financial information (invoice)
- Amount exceeds $100 threshold
- External recipient

## To Approve

Move this file to: `Pending_Approval/` → `Approved/`

## To Reject

Move this file to: `Pending_Approval/` → `Rejected/`

## To Modify

1. Edit this file with changes
2. Move to `Approved/`

---

*Created by AI Employee at 2026-03-05T12:00:00*
*Expires at 2026-03-06T12:00:00 (24 hours)*
```

## Workflow Steps

### Step 1: Qwen Creates Approval Request

```
Qwen detects sensitive action
    ↓
Creates: Pending_Approval/APPROVE_send_email_client.md
    ↓
Updates Dashboard: "Awaiting Approval: 1"
    ↓
Logs action to Logs/YYYY-MM-DD.md
```

### Step 2: Human Reviews

```
Human opens Obsidian
    ↓
Navigates to Pending_Approval/
    ↓
Reads approval request
    ↓
Reviews action details
```

### Step 3: Human Decides

**Option A: Approve**
```bash
move AI_Employee_Vault\Pending_Approval\APPROVE_*.md AI_Employee_Vault\Approved\
```

**Option B: Reject**
```bash
move AI_Employee_Vault\Pending_Approval\APPROVE_*.md AI_Employee_Vault\Rejected\
```

**Option C: Modify and Approve**
```bash
# Edit the file with changes
notepad AI_Employee_Vault\Pending_Approval\APPROVE_*.md

# Then move to Approved
move AI_Employee_Vault\Pending_Approval\APPROVE_*.md AI_Employee_Vault\Approved\
```

### Step 4: Orchestrator Executes

```
Orchestrator detects file in Approved/
    ↓
Reads action details
    ↓
Executes action (send email, make payment, etc.)
    ↓
Logs result to Logs/YYYY-MM-DD.md
    ↓
Moves file to Done/
    ↓
Updates Dashboard
```

## Approval Request Types

### Email Approval

```markdown
---
type: approval_request
action: send_email
to: recipient@example.com
subject: Important Update
---
```

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Vendor Name
reference: Invoice #123
---
```

### Social Media Post

```markdown
---
type: approval_request
action: social_post
platform: LinkedIn
content: Excited to announce...
scheduled_time: 2026-03-05T14:00:00
---
```

### File Operation

```markdown
---
type: approval_request
action: file_delete
path: /path/to/file.txt
reason: Cleanup old files
---
```

## Notification Options

### Email Notification

Configure in `Company_Handbook.md`:

```markdown
## Approval Notifications

When approval is required:
- Send email to: your.email@example.com
- Subject: "[AI Employee] Approval Required: {action_type}"
- Include: Link to vault file
```

### Desktop Notification

```bash
# Windows
powershell -Command "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(0, 'AI Employee', 'Approval required', 'Info')"
```

### WhatsApp Notification

```markdown
---
type: notification
channel: whatsapp
to: +1234567890
message: "AI Employee: Approval required for {action_type}. Check vault."
---
```

## Expiration Handling

If approval expires without action:

1. **Move to Rejected/** automatically
2. **Log** expiration event
3. **Notify** human of expired approval
4. **Update** Dashboard

```markdown
---
expired: true
expired_at: 2026-03-06T12:00:00
original_action: send_email
---

# Approval Expired

This approval request expired without action.

To re-request, run the workflow again.
```

## Audit Trail

All approval actions are logged:

```markdown
# Log for 2026-03-05

## 2026-03-05T12:00:00 - APPROVE_send_email_client

**Status:** created
**Actor:** qwen_code
**Target:** client@example.com

## 2026-03-05T12:15:00 - APPROVE_send_email_client

**Status:** approved
**Actor:** human (Dell)

## 2026-03-05T12:15:30 - APPROVE_send_email_client

**Status:** executed
**Actor:** orchestrator
**Result:** success
```

## Dashboard Integration

The Dashboard shows pending approvals:

```markdown
## Pending Approvals

- [FILE] APPROVE_send_email_client (created 15 min ago)
- [FILE] APPROVE_payment_vendor (created 1 hour ago)
- [FILE] APPROVE_social_post (expires in 2 hours)
```

## Commands

### List Pending Approvals

```bash
dir AI_Employee_Vault\Pending_Approval\*.md
```

### View Approval Details

```bash
type AI_Employee_Vault\Pending_Approval\APPROVE_*.md
```

### Bulk Approve (for trusted actions)

```bash
# WARNING: Only use for low-risk actions
move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
```

### Bulk Reject

```bash
move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Rejected\
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not moving | Check file is not open in another program |
| Orchestrator not executing | Check Approved/ folder permissions |
| Duplicate approvals | Clear old files from Rejected/ |
| Expired approvals | Re-run the workflow to create new request |

## Best Practices

1. **Review daily**: Check Pending_Approval at least once per day
2. **Set reminders**: Use calendar for time-sensitive approvals
3. **Keep audit trail**: Never delete from Rejected/ without review
4. **Update thresholds**: Adjust approval limits as trust grows
5. **Document decisions**: Add comments when rejecting

## Security Notes

- Never auto-approve payments to new recipients
- Always require approval for file deletions
- Review approval logs weekly
- Rotate approval thresholds quarterly
