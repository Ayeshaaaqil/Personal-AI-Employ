---
name: whatsapp-watcher
description: |
  WhatsApp monitoring watcher using Playwright. Monitors WhatsApp Web for
  new messages containing priority keywords and creates action files.
  Use for automatic message processing and lead capture workflows.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web and create actionable items for the AI Employee.

## Prerequisites

1. **Install Playwright:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Install Dependencies:**
   ```bash
   pip install playwright
   ```

3. **WhatsApp Web Account:**
   - Have WhatsApp Web session ready
   - Keep phone connected to internet

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WhatsApp Web   │────▶│ WhatsApp Watcher │────▶│  Needs_Action/  │
│  (via browser)  │     │  (Playwright)    │     │  (action files) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Configuration

Create `watchers/whatsapp_config.json`:

```json
{
  "check_interval_seconds": 30,
  "session_path": "C:\\path\\to\\whatsapp-session",
  "keywords_priority": ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote"],
  "business_hours": {
    "start": "08:00",
    "end": "20:00"
  },
  "known_contacts": ["+1234567890", "+0987654321"]
}
```

## Usage

### Start Watcher

```bash
cd watchers
python whatsapp_watcher.py ../AI_Employee_Vault
```

### First Run (Login to WhatsApp Web)

```bash
# This will open a browser for QR code scanning
python whatsapp_watcher.py ../AI_Employee_Vault --login
```

## Action File Format

When a priority message is detected:

```markdown
---
type: whatsapp_message
from: +1234567890
contact_name: John Doe
received: 2026-03-05T12:30:00
priority: high
keywords: [invoice, urgent]
status: pending
---

## Message Content

"Hi, can you send me the invoice for January? It's urgent."

## Chat Context

Last 3 messages from this contact:
- [12:28] Hi, are you there?
- [12:29] I need the invoice
- [12:30] Hi, can you send me the invoice for January? It's urgent.

## Suggested Actions

- [ ] Reply to message
- [ ] Send invoice
- [ ] Mark as processed

## Quick Reply Template

Hi John! Yes, I'll send you the invoice right away. Please check your email in the next few minutes.
```

## Keyword Detection

| Keyword | Priority | Auto-Action |
|---------|----------|-------------|
| urgent, asap | High | Immediate notification |
| invoice, payment | High | Forward to accounting |
| pricing, quote | Medium | Create lead file |
| help | High | Escalate to human |
| thanks, thank you | Low | Log only |

## Integration with Orchestrator

1. **Watcher detects** message with keyword
2. **Creates** action file in `Needs_Action/`
3. **Orchestrator triggers** Qwen Code
4. **Qwen reads** Company_Handbook for rules
5. **Qwen creates** response draft
6. **Human approves** via WhatsApp MCP
7. **Message sent** via browser automation

## Example Flow

```
WhatsApp message: "Need pricing info ASAP"
    ↓
whatsapp_watcher.py detects keywords
    ↓
Creates: Needs_Action/WHATSAPP_john_doe.md
    ↓
Orchestrator triggers Qwen Code
    ↓
Qwen reads message + Company_Handbook
    ↓
Qwen creates: Plans/PLAN_pricing_response.md
    ↓
Qwen creates: Pending_Approval/APPROVE_whatsapp_reply.md
    ↓
Human moves file to Approved/
    ↓
Playwright sends WhatsApp reply
    ↓
File moved to Done/
```

## Session Management

### Save Session
```bash
# Session is automatically saved to session_path
# Reuses browser context for faster startup
```

### Clear Session
```bash
python whatsapp_watcher.py --clear-session
```

### Check Session Status
```bash
python whatsapp_watcher.py --session-status
```

## Error Handling

| Error | Recovery |
|-------|----------|
| QR code expired | Re-run with --login flag |
| Session invalid | Clear session and re-authenticate |
| Browser crash | Auto-restart with new browser instance |
| Network error | Retry after 30 seconds |

## Security Notes

- Store session data outside the vault
- Never commit session files to git
- Log out from WhatsApp Web when not in use
- Review sent messages in Dashboard

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not showing | Check browser is not headless for login |
| Messages not detected | Verify keywords in config |
| Session keeps expiring | Check phone connectivity |
| Browser won't start | Run: playwright install chromium |

## Testing

```bash
# Test WhatsApp connection
python watchers/whatsapp_watcher.py --test

# View last processed messages
python watchers/whatsapp_watcher.py --last 5
```

## WhatsApp Web Limitations

- Requires phone to be connected to internet
- Session expires after ~30 days of inactivity
- Rate limited by WhatsApp (avoid spam)
- Terms of Service: Use for business purposes only

## Alternative: WhatsApp Business API

For production use, consider:

1. **WhatsApp Business API** (official)
   - More reliable
   - No browser automation needed
   - Requires business verification

2. **Twilio WhatsApp API**
   - Easier setup
   - Pay per conversation
   - Official partner
