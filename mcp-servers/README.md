# MCP Servers - Gold Tier

This folder contains MCP (Model Context Protocol) servers for external integrations.

## Available Servers

| Server | Purpose | Status |
|--------|---------|--------|
| `facebook_mcp_server.py` | Facebook Graph API | ✅ Complete |
| `odoo_mcp_server.py` | Odoo ERP Integration | ✅ Complete |
| `email_mcp_server.py` | Gmail API (in watchers/) | ✅ |
| `linkedin_mcp_server.py` | LinkedIn API (in watchers/) | ✅ |
| `audit_mcp_server.py` | Audit Logging (in watchers/) | ✅ |

---

## Setup

### Step 1: Configure Facebook

Create `facebook_config.json` in project root:

```json
{
  "access_token": "your_facebook_access_token",
  "page_id": "your_facebook_page_id"
}
```

Or add to `.env`:

```env
FACEBOOK_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

### Step 2: Configure Odoo

Create or edit `odoo_config.json`:

```json
{
  "url": "http://localhost:8069",
  "db": "odoo",
  "username": "admin",
  "api_key": "",
  "use_mock": true
}
```

---

## Usage

### Run Facebook MCP Server

```bash
cd mcp-servers
python facebook_mcp_server.py
```

### Run Odoo MCP Server

```bash
cd mcp-servers
python odoo_mcp_server.py
```

---

## MCP Methods

### Facebook MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `facebook/post` | `message`, `link` | `{success, post_id, url}` |
| `facebook/post_photo` | `message`, `photo_url` | `{success, photo_id}` |
| `facebook/get_insights` | `metric` | `{success, data}` |
| `facebook/get_comments` | `post_id` | `{success, comments}` |
| `facebook/reply_comment` | `post_id`, `message` | `{success, comment_id}` |

### Odoo MCP

| Method | Parameters | Returns |
|--------|------------|---------|
| `odoo/create_invoice` | `customer`, `amount`, `description` | `{success, invoice}` |
| `odoo/get_invoices` | `status`, `customer` | `{success, invoices, count}` |
| `odoo/update_invoice` | `invoice_number`, `status` | `{success, invoice}` |
| `odoo/get_summary` | - | `{success, summary}` |
| `odoo/create_customer` | `name`, `email`, `phone` | `{success, customer}` |
| `odoo/get_customers` | - | `{success, customers}` |

---

## Testing

### Test Facebook MCP

```python
import subprocess
import json

proc = subprocess.Popen(
    ['python', 'facebook_mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Test post
request = {
    "method": "facebook/post",
    "params": {
        "message": "Test post from AI Employee!"
    },
    "id": 1
}

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

response = json.loads(proc.stdout.readline())
print(response)

proc.terminate()
```

### Test Odoo MCP

```python
import subprocess
import json

proc = subprocess.Popen(
    ['python', 'odoo_mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Create invoice
request = {
    "method": "odoo/create_invoice",
    "params": {
        "customer": "Test Client",
        "amount": 1500,
        "description": "Consulting services"
    },
    "id": 1
}

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

response = json.loads(proc.stdout.readline())
print(response)

proc.terminate()
```

---

## Integration with AI Assistant

Add to your MCP configuration file:

**File:** `~/.config/claude-code/mcp.json` or `mcp-config.json`

```json
{
  "mcpServers": {
    "facebook": {
      "command": "python",
      "args": ["C:/.../mcp-servers/facebook_mcp_server.py"],
      "env": {}
    },
    "odoo": {
      "command": "python",
      "args": ["C:/.../mcp-servers/odoo_mcp_server.py"],
      "env": {}
    }
  }
}
```

---

## Troubleshooting

### Facebook Authentication Error

```bash
# Check token is valid
curl "https://graph.facebook.com/v18.0/me?access_token=YOUR_TOKEN"

# If invalid, generate new token from Facebook Developer Dashboard
```

### Odoo Connection Error

```bash
# Check Odoo is running
python watchers\odoo_integration.py --status

# Use mock mode if Odoo not available
# Edit odoo_config.json: "use_mock": true
```

---

## File Structure

```
mcp-servers/
├── facebook_mcp_server.py    # Facebook Graph API
├── odoo_mcp_server.py        # Odoo ERP Integration
└── README.md                 # This file
```

---

**MCP Servers are ready for Gold Tier!** 🎉
