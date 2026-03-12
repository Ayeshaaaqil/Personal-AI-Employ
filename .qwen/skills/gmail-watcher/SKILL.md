---
name: gmail-watcher
description: |
  Gmail monitoring watcher for AI Employee. Continuously monitors Gmail inbox
  for new important/unread emails and creates action files in Needs_Action.
  Use for automatic email processing and response workflows.
---

# Gmail Watcher Skill

Monitor Gmail and create actionable items for the AI Employee.

## Prerequisites

1. **Gmail API Setup:**
   - Enable Gmail API in Google Cloud Console
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to a secure location

2. **Install Dependencies:**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. **First-time Auth:**
   ```bash
   python watchers/gmail_watcher.py --auth
   ```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Gmail API     │────▶│  Gmail Watcher   │────▶│  Needs_Action/  │
│  (poll every    │     │  (Python script) │     │  (action files) │
│   2 minutes)    │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Configuration

Create `watchers/gmail_config.json`:

```json
{
  "check_interval_seconds": 120,
  "labels_to_monitor": ["INBOX", "IMPORTANT"],
  "only_unread": true,
  "keywords_priority": ["urgent", "asap", "invoice", "payment", "help"],
  "known_contacts": ["client@example.com", "partner@company.com"],
  "credentials_path": "C:\\path\\to\\credentials.json",
  "token_path": "C:\\path\\to\\token.json"
}
```

## Usage

### Start Watcher

```bash
cd watchers
python gmail_watcher.py ../AI_Employee_Vault
```

### Run with Custom Config

```bash
python gmail_watcher.py ../AI_Employee_Vault --config gmail_config.json
```

## Action File Format

When an email is detected, the watcher creates a file in `Needs_Action/`:

```markdown
---
type: email
from: John Doe <john@example.com>
subject: Urgent: Invoice Payment
received: 2026-03-05T12:30:00
priority: high
status: pending
labels: INBOX, IMPORTANT, UNREAD
---

## Email Content

{email body snippet}

## Attachments

- invoice_jan_2026.pdf (if any)

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to accounting
- [ ] Mark as processed

## Quick Reply Template

Hi John,

Thank you for your email. I've received your invoice and will process it shortly.

Best regards,
[Your Name]
```

## Priority Detection

| Condition | Priority | Action |
|-----------|----------|--------|
| From known contact + urgent keyword | High | Immediate action |
| From known contact | Medium | Queue for response |
| From unknown sender | Low | Flag for review |
| Contains "invoice" or "payment" | High | Forward to accounting |

## Integration with Orchestrator

1. **Watcher detects** new email
2. **Creates** action file in `Needs_Action/`
3. **Orchestrator triggers** Qwen Code
4. **Qwen reads** Company_Handbook for rules
5. **Qwen creates** Plan.md or approval request
6. **Human approves** if needed
7. **Email MCP sends** response

## Example Flow

```
New email from client@example.com
    ↓
Subject: "Urgent: Need invoice for January"
    ↓
gmail_watcher.py detects email
    ↓
Creates: Needs_Action/EMAIL_abc123.md
    ↓
Orchestrator triggers Qwen Code
    ↓
Qwen reads email + Company_Handbook
    ↓
Qwen creates: Plans/PLAN_invoice_response.md
    ↓
Qwen creates: Pending_Approval/APPROVE_email_response.md
    ↓
Human moves file to Approved/
    ↓
Email MCP sends response
    ↓
File moved to Done/
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Token expired | Auto-refresh or re-run auth |
| API quota exceeded | Wait and retry (exponential backoff) |
| Network error | Retry after 30 seconds |
| Invalid credentials | Alert user, pause operations |

## Security Notes

- Store credentials outside the vault
- Never commit token.json to git
- Use app-specific passwords if 2FA enabled
- Review sent emails in Dashboard

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Watcher not detecting emails | Check Gmail API is enabled |
| Auth error | Delete token.json and re-authenticate |
| Duplicate action files | Clear processed_ids cache |
| API quota exceeded | Reduce check frequency |

## Testing

```bash
# Test Gmail connection
python watchers/gmail_watcher.py --test

# View last processed emails
python watchers/gmail_watcher.py --last 5
```
