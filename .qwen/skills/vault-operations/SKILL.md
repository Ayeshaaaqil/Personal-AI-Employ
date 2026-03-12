---
name: vault-operations
description: |
  Obsidian vault operations for AI Employee. Read, write, and manage
  files in the AI Employee vault. Use for processing Needs_Action items,
  creating plans, updating dashboard, and managing approval workflows.
---

# Vault Operations Skill

This skill provides file system operations for the AI Employee vault.

## Quick Reference

### Read Files

```bash
# Read a specific file
claude read AI_Employee_Vault/Needs_Action/FILE_*.md

# List all pending actions
claude "List files in AI_Employee_Vault/Needs_Action"
```

### Write Files

```bash
# Create a plan file
claude "Create a Plan.md in AI_Employee_Vault/Plans with steps to process the pending items"

# Update dashboard
claude "Update the Dashboard.md with recent activity"
```

### Move Files

```bash
# Move completed items to Done
claude "Move FILE_*.md from Needs_Action to Done after processing"

# Move approval request to Approved
claude "Move the approval file from Pending_Approval to Approved"
```

## Workflow: Process Pending Actions

1. **Read** all files in `/Needs_Action`
2. **Read** `Company_Handbook.md` for rules
3. **Create** `Plan.md` with action steps
4. **Request approval** for sensitive actions
5. **Execute** approved actions
6. **Log** results to `/Logs`
7. **Update** `Dashboard.md`
8. **Move** completed items to `/Done`

## Workflow: Approval Request

When a sensitive action is detected:

1. **Create** approval file in `/Pending_Approval`:

```markdown
---
type: approval_request
action: [action_type]
created: [timestamp]
status: pending
---

## Action Required

[Description of the action]

## To Approve

Move this file to /Approved folder.

## To Reject

Move this file to /Rejected folder.
```

2. **Wait** for human to move file to `/Approved`
3. **Execute** the action
4. **Log** the result

## File Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time status
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Objectives & metrics
├── Inbox/                 # Drop folder for files
├── Needs_Action/          # Items requiring attention
├── Plans/                 # Action plans
├── Done/                  # Completed items
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved actions ready to execute
├── Rejected/              # Rejected actions
├── Accounting/            # Financial records
├── Briefings/             # CEO briefings
├── Logs/                  # Activity logs
└── Invoices/              # Generated invoices
```

## Best Practices

1. **Always read** Company_Handbook.md before making decisions
2. **Create plans** before taking action
3. **Request approval** for sensitive actions (payments > $50, new contacts)
4. **Log everything** to the Logs folder
5. **Update Dashboard** after each action
6. **Move files** to appropriate folders after processing

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't read files | Check file permissions and path |
| Claude not responding | Run `claude --version` to verify installation |
| Files not moving | Ensure destination folders exist |
| Dashboard not updating | Check file is not locked by another process |
