---
name: email-mcp
description: |
  Email integration via Gmail MCP server. Send, draft, search, and manage emails.
  Use when tasks require sending email responses, creating drafts, or searching
  through email history. Requires Gmail API credentials setup.
---

# Email MCP Skill

Send and manage emails via Gmail MCP server.

## Prerequisites

1. **Gmail API Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Install Email MCP Server:**
   ```bash
   npm install -g @anthropic/email-mcp
   ```

3. **Configure MCP:**
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

## Server Lifecycle

### Start Server
```bash
npx @anthropic/email-mcp@latest
```

### Stop Server
```bash
# Close the terminal or press Ctrl+C
```

## Quick Reference

### Send Email

```bash
# Send an email
qwen "Send email to client@example.com with subject 'Invoice #123' and body 'Please find attached your invoice.'"
```

### Draft Email

```bash
# Create a draft for review
qwen "Create a draft email to client@example.com thanking them for their business"
```

### Search Emails

```bash
# Search for emails
qwen "Search for unread emails from important clients"
```

### Reply to Email

```bash
# Reply to an email
qwen "Reply to the last email from john@example.com confirming the meeting"
```

## Workflow: Send Email with Approval

For sensitive emails (new contacts, bulk sends, financial info):

1. **Create approval request** in `/Pending_Approval`:
   ```markdown
   ---
   type: approval_request
   action: send_email
   to: client@example.com
   subject: Invoice #123
   created: 2026-03-05T12:00:00
   status: pending
   ---
   
   ## Email to Send
   
   **To:** client@example.com
   **Subject:** Invoice #123
   **Body:** Please find attached your invoice for January 2026.
   
   ## To Approve
   Move this file to /Approved folder.
   ```

2. **Wait** for human to move file to `/Approved`

3. **Send email** using MCP

4. **Log** the result to `/Logs`

## Workflow: Auto-Reply to Known Contacts

For known contacts (from Company_Handbook):

1. **Read** email from Needs_Action
2. **Check** sender against known contacts
3. **Draft** polite acknowledgment
4. **Send** directly (no approval needed)
5. **Log** to Dashboard

## Email Templates

### Invoice Email
```
Subject: Invoice #{invoice_number} - {amount}

Dear {client_name},

Please find attached invoice #{invoice_number} for {amount}.

Payment is due within {days} days. If you have any questions, 
please don't hesitate to reach out.

Best regards,
{your_name}
```

### Meeting Confirmation
```
Subject: Meeting Confirmation - {date}

Hi {name},

This email confirms our meeting scheduled for {date} at {time}.

Looking forward to speaking with you.

Best regards,
{your_name}
```

### Follow-up Email
```
Subject: Following up on {topic}

Hi {name},

I wanted to follow up on our previous conversation about {topic}.

Please let me know if you need any additional information.

Best regards,
{your_name}
```

## Rules of Engagement

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Reply to known contact | Yes | No |
| Reply to new contact | No | Yes |
| Send invoice | Yes | No |
| Send proposal | No | Yes |
| Bulk email (>10 recipients) | No | Always |
| Email with attachment > 5MB | No | Always |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run OAuth flow, check credentials.json |
| Email not sending | Check Gmail API quota, verify recipient email |
| Draft not created | Ensure vault has write permissions |
| MCP server not found | Run: npm install -g @anthropic/email-mcp |

## Security Notes

- Never store email credentials in the vault
- Use environment variables for sensitive data
- Log all sent emails for audit purposes
- Respect Gmail API rate limits (250 quota units/day for free tier)
