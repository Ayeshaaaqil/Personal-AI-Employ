---
name: scheduler
description: |
  Task scheduler for AI Employee. Schedule recurring tasks like daily briefings,
  weekly audits, and periodic checks. Supports cron (Linux/Mac) and Task Scheduler
  (Windows). Use for automated background operations.
---

# Scheduler Skill

Schedule recurring tasks for the AI Employee system.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  OS Scheduler   │────▶│  orchestrator.py │────▶│  Qwen Code      │
│  (cron/Task)    │     │  (scheduled run) │     │  (process)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Scheduled Tasks

| Task | Frequency | Time | Purpose |
|------|-----------|------|---------|
| Daily Briefing | Daily | 8:00 AM | Summarize pending items |
| Needs_Action Check | Every 30 min | All day | Process new items |
| Weekly Audit | Weekly | Monday 7 AM | Generate CEO Briefing |
| Dashboard Update | Hourly | All day | Refresh status counts |

## Windows Setup (Task Scheduler)

### Option 1: Using PowerShell Script

Create `scripts/setup-scheduler.ps1`:

```powershell
$taskName = "AI_Employee_Orchestrator"
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "orchestrator.py AI_Employee_Vault" `
    -WorkingDirectory "C:\Users\Dell\Documents\GitHub\Personal-AI-Employ"

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME `
    -LogonType S4U -RunLevel Highest

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Description "AI Employee Orchestrator - Runs continuously"

Write-Host "Task '$taskName' registered successfully!"
```

Run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-scheduler.ps1
```

### Option 2: Manual Setup

1. **Open Task Scheduler**
   - Press Win + R
   - Type: `taskschd.msc`
   - Press Enter

2. **Create Basic Task**
   - Right-click "Task Scheduler Library"
   - Select "Create Basic Task"
   - Name: "AI Employee Orchestrator"

3. **Configure Trigger**
   - Select "At startup"
   - Check "Repeat task every": 1 minute
   - Select "For a duration of": Indefinitely

4. **Configure Action**
   - Select "Start a program"
   - Program: `python.exe`
   - Arguments: `orchestrator.py AI_Employee_Vault`
   - Start in: `C:\Users\Dell\Documents\GitHub\Personal-AI-Employ`

5. **Advanced Settings**
   - Check "Run with highest privileges"
   - Check "Run whether user is logged on or not"
   - Check "Start task on AC power"
   - Check "Stop if running on batteries"

### Option 3: Daily Briefing Task

```powershell
$taskName = "AI_Employee_Daily_Briefing"
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "orchestrator.py AI_Employee_Vault --briefing" `
    -WorkingDirectory "C:\Users\Dell\Documents\GitHub\Personal-AI-Employ"

$trigger = New-ScheduledTaskTrigger -Daily -At 8am

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Description "Generate daily CEO briefing"
```

## Linux/Mac Setup (cron)

### Edit Crontab

```bash
crontab -e
```

### Add Entries

```cron
# AI Employee Orchestrator - run every minute
* * * * * cd /home/user/Personal-AI-Employ && python orchestrator.py AI_Employee_Vault >> logs/orchestrator.log 2>&1

# Daily Briefing - 8 AM every day
0 8 * * * cd /home/user/Personal-AI-Employ && python orchestrator.py AI_Employee_Vault --briefing >> logs/briefing.log 2>&1

# Weekly Audit - 7 AM every Monday
0 7 * * 1 cd /home/user/Personal-AI-Employ && python orchestrator.py AI_Employee_Vault --audit >> logs/audit.log 2>&1
```

## Usage

### Run Orchestrator Once

```bash
python orchestrator.py AI_Employee_Vault --once
```

### Run with Briefing

```bash
python orchestrator.py AI_Employee_Vault --briefing
```

### Run Continuous (default)

```bash
python orchestrator.py AI_Employee_Vault
```

## Scheduled Task: Daily Briefing

When triggered, generates a briefing file:

```markdown
---
type: daily_briefing
date: 2026-03-05
generated: 2026-03-05T08:00:00
---

# Daily Briefing - March 5, 2026

## Summary

- Pending Actions: 3
- Awaiting Approval: 1
- Completed Yesterday: 5

## Priority Items

1. Email from Client A - Invoice request
2. WhatsApp message - Pricing inquiry
3. File drop - Contract.pdf

## Today's Schedule

- [ ] Process all pending items
- [ ] Review approval requests
- [ ] Send follow-up emails

## Revenue Update

- This Week: $2,500
- This Month: $8,000
- Target: $10,000 (80% complete)
```

## Scheduled Task: Weekly Audit

Generates CEO Briefing every Monday:

```markdown
---
type: ceo_briefing
week: 2026-W10
generated: 2026-03-05T07:00:00
---

# CEO Weekly Briefing

## Executive Summary

Strong week with revenue ahead of target.

## Revenue

- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track

## Completed Tasks

- [x] Client A invoice sent and paid
- [x] Project Alpha milestone delivered
- [x] Weekly social media scheduled

## Bottlenecks

| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- Notion: No activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription?

### Upcoming Deadlines
- Project Alpha: Jan 15 (9 days)
- Quarterly tax: Jan 31 (25 days)
```

## Management Commands

### View Scheduled Tasks (Windows)

```powershell
# List all tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*AI_Employee*"}

# View task history
Get-ScheduledTaskInfo -TaskName "AI_Employee_Orchestrator"
```

### View Scheduled Tasks (Linux/Mac)

```bash
# List cron jobs
crontab -l

# View system logs
grep CRON /var/log/syslog | grep orchestrator
```

### Disable Task

```powershell
# Windows
Disable-ScheduledTask -TaskName "AI_Employee_Orchestrator"

# Linux/Mac
crontab -r  # Remove all jobs
```

### Enable Task

```powershell
# Windows
Enable-ScheduledTask -TaskName "AI_Employee_Orchestrator"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check "Run whether user is logged on or not" |
| Python not found | Use full path: C:\Python312\python.exe |
| Permission denied | Run as administrator, check "Run with highest privileges" |
| Task runs but exits | Check working directory, add logging |

## Best Practices

1. **Log everything**: Redirect output to log files
2. **Set timeouts**: Prevent runaway processes
3. **Monitor failures**: Check Task Scheduler history
4. **Test first**: Run manually before scheduling
5. **Use AC power**: Don't run on battery for laptops

## Security Notes

- Store credentials in environment variables
- Don't store passwords in task configuration
- Review logs regularly for anomalies
- Use least-privilege principle
