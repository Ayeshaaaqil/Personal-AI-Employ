# AI Employee - Bronze Tier

## Overview

This is the **Bronze Tier** implementation of the Personal AI Employee hackathon. It provides the foundational layer for autonomous task management.

## What's Included

### ✅ Bronze Tier Deliverables

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System monitoring)
- [x] Claude Code integration for reading/writing to vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] Agent Skill documentation (vault-operations)

## Project Structure

```
Personal-AI-Employ/
├── AI_Employee_Vault/       # Obsidian vault
│   ├── Dashboard.md         # Real-time status dashboard
│   ├── Company_Handbook.md  # Rules of engagement
│   ├── Business_Goals.md    # Business objectives
│   ├── Inbox/               # Drop folder for files
│   ├── Needs_Action/        # Items requiring attention
│   ├── Done/                # Completed items
│   ├── Pending_Approval/    # Awaiting human approval
│   ├── Approved/            # Approved actions
│   ├── Rejected/            # Rejected actions
│   ├── Plans/               # Action plans
│   ├── Briefings/           # CEO briefings
│   ├── Accounting/          # Financial records
│   ├── Logs/                # Activity logs
│   └── Invoices/            # Generated invoices
├── watchers/
│   ├── base_watcher.py      # Abstract base class
│   ├── filesystem_watcher.py # File system monitor
│   └── requirements.txt     # Python dependencies
├── orchestrator.py          # Master process manager
└── BRONZE_README.md         # This file
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

### 2. Verify Qwen Code Installation

```bash
qwen --version
```

If not installed, install Qwen Code CLI according to the official documentation.

### 3. Open Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder

## Usage

### Start the File Watcher

The file watcher monitors the `Inbox` folder for new files.

```bash
# From project root
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault
```

Or with custom paths:
```bash
python filesystem_watcher.py /path/to/AI_Employee_Vault
```

### Start the Orchestrator

The orchestrator checks for new items and triggers Qwen Code.

```bash
# From project root
python orchestrator.py AI_Employee_Vault
```

### Test the Workflow

1. **Drop a file** in the `AI_Employee_Vault/Inbox` folder
2. **Watcher detects** the file and creates a metadata `.md` file in `Needs_Action`
3. **Orchestrator triggers** Qwen Code to process the item
4. **Qwen creates** a Plan.md with action steps
5. **Review and approve** any actions in `Pending_Approval`
6. **Move approved files** to `Approved` folder
7. **Orchestrator executes** and moves to `Done`

## Configuration

### Company Handbook

Edit `Company_Handbook.md` to customize:

- Communication rules
- Financial approval thresholds
- Working hours
- Escalation rules

### Business Goals

Edit `Business_Goals.md` to set:

- Revenue targets
- Active projects
- Client information
- Service rates

## Running in Background (Windows)

### Using PowerShell

```powershell
# Start watcher in background
Start-Process python -ArgumentList "watchers\filesystem_watcher.py AI_Employee_Vault" -WindowStyle Hidden

# Start orchestrator in background
Start-Process python -ArgumentList "orchestrator.py AI_Employee_Vault" -WindowStyle Hidden
```

### Using Task Scheduler

For persistent background operation, create scheduled tasks:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At logon
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `watchers\filesystem_watcher.py AI_Employee_Vault`

## Testing Checklist

- [ ] File watcher starts without errors
- [ ] Dropping a file in Inbox creates metadata in Needs_Action
- [ ] Claude Code is triggered by orchestrator
- [ ] Plan.md files are created
- [ ] Approval workflow works (Pending_Approval → Approved → Done)
- [ ] Dashboard updates with recent activity
- [ ] Logs are created in Logs folder

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:

1. Gmail Watcher for email monitoring
2. WhatsApp Watcher for message monitoring
3. MCP server for sending emails
4. Human-in-the-loop approval workflow
5. Scheduled tasks (cron/Task Scheduler)

## Troubleshooting

### Watcher not detecting files

- Ensure the Inbox folder path is correct
- Check file permissions
- Verify watchdog is installed: `pip show watchdog`

### Claude Code not responding

- Verify installation: `qwen --version`
- Check API key is configured
- Review Qwen Code documentation

### Files not moving between folders

- Ensure destination folders exist
- Check file is not open in another program
- Verify file permissions

## Support

- Hackathon documentation: `hackathon 0.md`
- Agent Skills: `.qwen/skills/`
- Research meetings: Wednesdays 10:00 PM on Zoom

---

*Bronze Tier Complete! 🥉*
