# WhatsApp Integration Skill

**Tier:** Silver
**Type:** Watcher + MCP Server
**Platform:** WhatsApp Web

---

## Overview

This skill enables your AI Employee to monitor WhatsApp messages and send responses automatically. It uses Playwright for browser automation and follows the watcher pattern.

---

## When to Use

Use this skill when you need to:
- Monitor WhatsApp for important messages
- Auto-flag urgent messages (invoice, payment, urgent, etc.)
- Send WhatsApp messages via AI Employee
- Create action items from WhatsApp conversations

---

## Installation

### Prerequisites

```bash
# Ensure Playwright is installed
pip install playwright
playwright install chromium
```

### Files

- `watchers/whatsapp_watcher.py` - Monitors WhatsApp Web
- `watchers/whatsapp_mcp_server.py` - Sends messages

---

## Setup

### 1. First-Time Login

```bash
# Test connection (will show QR code for first-time login)
python watchers/whatsapp_mcp_server.py --test
```

**Important:** Keep the browser window open and scan the QR code with your WhatsApp mobile app.

### 2. Run WhatsApp Watcher

```bash
# Continuous monitoring
python watchers/whatsapp_watcher.py AI_Employee_Vault

# Debug mode (single check)
python watchers/whatsapp_watcher.py AI_Employee_Vault --debug
```

### 3. Send Test Message

```bash
# Send message to contact
python watchers/whatsapp_mcp_server.py --action send_message --contact "John Doe" --message "Hello from AI Employee!"

# Send message to phone number
python watchers/whatsapp_mcp_server.py --action send_message_to_number --phone "+923001234567" --message "Test message"
```

---

## Configuration

### Environment Variables (.env)

```bash
# WhatsApp session path (optional)
WHATSAPP_SESSION_PATH=~/.whatsapp-session

# Keywords to monitor (optional)
WHATSAPP_KEYWORDS=urgent,invoice,payment,help,asap
```

### Watcher Configuration

```python
watcher = WhatsAppWatcher(
    vault_path="AI_Employee_Vault",
    session_path="whatsapp-session",  # Optional
    check_interval=30,  # Seconds between checks
    keywords=["urgent", "invoice", "payment"]  # Keywords to filter
)
```

---

## Quick Reference

### Monitor WhatsApp
```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault
```

### Send Message
```bash
python watchers/whatsapp_mcp_server.py --action send_message --contact "Name" --message "Text"
```

### Test Connection
```bash
python watchers/whatsapp_mcp_server.py --test
```

### Debug Mode
```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault --debug
```

---

## Output Format

When WhatsApp Watcher detects an important message, it creates a file in `Needs_Action/`:

```markdown
---
type: whatsapp_message
from: John Doe
received: 2026-03-08T18:00:00
platform: WhatsApp
priority: high
status: pending
keywords: urgent, payment
---

# WhatsApp Message

**From:** John Doe
**Received:** 2026-03-08 18:00:00

---

## Message Content

Hi, I need urgent help with the payment. Can you send the invoice?

---

## Suggested Actions

- [ ] Read and understand the message
- [ ] Determine if response is needed
- [ ] Draft response if required
- [ ] Move to Done folder after processing
```

---

## Troubleshooting

### QR Code Keeps Appearing

**Problem:** WhatsApp keeps asking to scan QR code

**Solution:**
1. Make sure you're logged in on your phone
2. Keep the browser window open during first login
3. Check session folder exists: `~/.whatsapp-session`

### No Messages Detected

**Problem:** Watcher runs but detects no messages

**Solution:**
1. Ensure you have unread messages in WhatsApp
2. Check keywords match your message content
3. Run in debug mode to see what's detected

### Message Not Sending

**Problem:** MCP server fails to send message

**Solution:**
1. Ensure WhatsApp Web is logged in
2. Check contact name matches exactly
3. Use phone number format with country code

### Browser Crashes

**Problem:** Playwright browser crashes frequently

**Solution:**
```bash
# Update Playwright
pip install --upgrade playwright
playwright install chromium --force
```

---

## Security Considerations

1. **Session Privacy:** The session folder contains authentication data. Keep it secure.
2. **Rate Limiting:** Don't send too many messages too quickly (WhatsApp may ban)
3. **Terms of Service:** Ensure compliance with WhatsApp's terms
4. **Backup:** Regularly backup your session folder

---

## Integration with AI Employee

### Orchestrator Integration

Add to `orchestrator.py`:

```python
# Start WhatsApp watcher
subprocess.Popen([
    sys.executable,
    'watchers/whatsapp_watcher.py',
    'AI_Employee_Vault'
])
```

### Approval Workflow

For sensitive messages (payments, invoices):
1. Watcher creates file in `Needs_Action/`
2. AI Employee processes and suggests response
3. Creates approval request in `Pending_Approval/`
4. User moves to `Approved/` to send
5. MCP server sends the message

---

## Examples

### Example 1: Monitor for Invoice Requests

```bash
# Run watcher with custom keywords
python watchers/whatsapp_watcher.py AI_Employee_Vault --keywords invoice bill payment due
```

### Example 2: Send Bulk Messages

```python
# Python script
from whatsapp_mcp_server import WhatsAppMCPServer

server = WhatsAppMCPServer()

contacts = ["John", "Jane", "Bob"]
message = "Reminder: Meeting tomorrow at 10 AM"

for contact in contacts:
    result = server.send_message(contact, message)
    print(f"Sent to {contact}: {result['success']}")
```

### Example 3: Auto-Responder

```python
# Auto-respond to urgent messages
from pathlib import Path
from whatsapp_mcp_server import WhatsAppMCPServer

server = WhatsAppMCPServer()
needs_action = Path("AI_Employee_Vault/Needs_Action")

for md_file in needs_action.glob("WHATSAPP_*.md"):
    content = md_file.read_text()
    
    if "urgent" in content.lower():
        # Extract contact and send response
        server.send_message(
            contact="Unknown",
            message="Thank you for your message. We'll respond shortly."
        )
```

---

## Performance

| Metric | Value |
|--------|-------|
| Check Interval | 30 seconds (configurable) |
| Message Detection | < 5 seconds |
| Send Latency | 10-15 seconds |
| Session Persistence | Yes |
| Headless Mode | Supported |

---

## Related Skills

- **gmail-watcher** - Email monitoring
- **linkedin-mcp** - LinkedIn integration
- **facebook-integration** - Facebook/Messenger
- **approval-workflow** - Human-in-the-loop

---

## Resources

- [WhatsApp Web](https://web.whatsapp.com)
- [Playwright Docs](https://playwright.dev/python)
- [Hackathon Blueprint](../hackathon%200.md)

---

*Last Updated: 2026-03-08*
