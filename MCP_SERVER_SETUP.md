# MCP Server Setup Guide - Gold Tier

## Overview

Gold Tier includes 5 MCP (Model Context Protocol) servers for external integrations:

| Server | Purpose | Status |
|--------|---------|--------|
| `email_mcp_server.py` | Gmail API integration | ✅ |
| `linkedin_mcp_server.py` | LinkedIn API integration | ✅ |
| `facebook_mcp_server.py` | Facebook Graph API | ⚠️ Manual setup |
| `odoo_mcp_server.py` | Odoo ERP integration | ✅ |
| `audit_mcp_server.py` | Audit logging | ✅ |

---

## Quick Start

### Step 1: Configure Environment Variables

Edit `.env` file with your API credentials:

```bash
# Open .env file
notepad .env
```

Fill in:
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- etc.

### Step 2: Test MCP Servers

```bash
# Test Email MCP
python watchers\email_mcp_server.py

# Test LinkedIn MCP
python watchers\linkedin_mcp_server.py

# Test Odoo MCP
python watchers\odoo_mcp_server.py

# Test Audit MCP
python watchers\audit_mcp_server.py
```

Each server will start and wait for JSON-RPC requests via stdin.

---

## MCP Server Configuration

### For Qwen Code / Claude Code

Add to your AI assistant's MCP configuration:

**File:** `~/.config/claude-code/mcp.json` or `~/.qwen/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["C:/Users/Dell/Documents/GitHub/Personal-AI-Employ/watchers/email_mcp_server.py"],
      "env": {}
    },
    "linkedin": {
      "command": "python",
      "args": ["C:/Users/Dell/Documents/GitHub/Personal-AI-Employ/watchers/linkedin_mcp_server.py"],
      "env": {}
    },
    "odoo": {
      "command": "python",
      "args": ["C:/Users/Dell/Documents/GitHub/Personal-AI-Employ/watchers/odoo_mcp_server.py"],
      "env": {}
    },
    "audit": {
      "command": "python",
      "args": ["C:/Users/Dell/Documents/GitHub/Personal-AI-Employ/watchers/audit_mcp_server.py"],
      "env": {}
    }
  }
}
```

---

## Available MCP Methods

### Email MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `email/send` | `to`, `subject`, `body`, `in_reply_to` | `{success, message_id}` |
| `email/read` | `message_id` | `{success, from, to, subject, date, snippet}` |
| `email/search` | `query`, `max_results` | `{success, count, messages}` |

**Example Request:**
```json
{
  "method": "email/send",
  "params": {
    "to": "client@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached..."
  },
  "id": 1
}
```

### LinkedIn MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `linkedin/post` | `content` | `{success, post_id}` |
| `linkedin/get_profile` | - | `{success, profile}` |

### Odoo MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `odoo/create_invoice` | `customer`, `amount`, `description` | `{success, invoice}` |
| `odoo/get_invoices` | `status` | `{success, invoices}` |
| `odoo/get_summary` | - | `{success, summary}` |

### Audit MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `audit/log` | `event_type`, `actor`, `action`, `extra` | `{success, entry_id}` |
| `audit/query` | `filters` | `{success, entries, count}` |
| `audit/generate_report` | `date` | `{success, report}` |

---

## Testing MCP Servers Manually

### Test via Command Line

```bash
# Start server
python watchers\audit_mcp_server.py

# Send test request (type this JSON):
{"method": "audit/log", "params": {"event_type": "test", "actor": "user", "action": "test_action"}, "id": 1}
```

**Expected Response:**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"success": true, "entry_id": "2026-03-06T19:45:00.000000"}}
```

### Test via Python Script

```python
import subprocess
import json

# Start server
proc = subprocess.Popen(
    ['python', 'watchers/audit_mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "method": "audit/log",
    "params": {"event_type": "test", "actor": "test", "action": "test"},
    "id": 1
}

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
print(response)

proc.terminate()
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check Python path
python --version

# Check file exists
dir watchers\audit_mcp_server.py

# Check dependencies
pip install requests google-auth google-api-python-client
```

### Authentication Errors

```bash
# For Email MCP - re-authenticate Gmail
python scripts\generate_gmail_token.py --verify

# For LinkedIn MCP - re-authenticate
python watchers\linkedin_api_poster.py --auth
```

### MCP Not Responding

Check logs:
```bash
dir AI_Employee_Vault\Logs\
type AI_Employee_Vault\Audit\*.jsonl
```

---

## Production Deployment

### Run as Background Service (Windows)

Use NSSM (Non-Sucking Service Manager):

```bash
# Download NSSM from nssm.cc
# Install as service
nssm install EmailMCP python "C:\...\watchers\email_mcp_server.py"
nssm start EmailMCP
```

### Docker Deployment

Create `Dockerfile` for each MCP server:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY watchers/*.py .
RUN pip install requests google-auth google-api-python-client
CMD ["python", "email_mcp_server.py"]
```

---

## Security Notes

⚠️ **IMPORTANT:**

1. **Never commit `.env` file** - it contains secrets
2. **Use environment variables** for credentials
3. **Enable audit logging** for all MCP calls
4. **Rate limit** API calls to avoid quotas
5. **Validate all inputs** before processing

---

## Complete Example: Send Email via MCP

```python
import subprocess
import json

# Start Email MCP server
proc = subprocess.Popen(
    ['python', 'watchers/email_mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send email request
request = {
    "method": "email/send",
    "params": {
        "to": "client@example.com",
        "subject": "Test from MCP",
        "body": "Hello from AI Employee Gold Tier!"
    },
    "id": 1
}

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
print(f"Result: {response}")

proc.terminate()
```

---

**MCP Servers are ready for Gold Tier!** 🎉

For more info, see `GOLD_README.md`
