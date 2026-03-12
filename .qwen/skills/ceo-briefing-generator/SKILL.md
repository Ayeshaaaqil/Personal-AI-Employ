---
name: ceo-briefing-generator
description: |
  Weekly CEO Briefing generator for AI Employee. Automatically audits
  business transactions, tasks, and generates comprehensive reports.
---

# CEO Briefing Generator Skill

Automated weekly business audit and reporting.

## Quick Reference

### Generate Briefing

```bash
python watchers\ceo_briefing_generator.py ../AI_Employee_Vault --once
```

### Schedule Weekly

Add to Task Scheduler:
```bash
python watchers\ceo_briefing_generator.py ../AI_Employee_Vault --weekly
```

## Briefing Contents

- Executive Summary
- Revenue Summary (weekly, MTD, trends)
- Completed Tasks
- Bottlenecks Identified
- Proactive Suggestions
- Upcoming Deadlines
- Key Metrics

## Output Location

Briefings saved to: `AI_Employee_Vault/Briefings/YYYY-W##_CEO_Briefing.md`

## Sample Briefing

```markdown
# CEO Weekly Briefing

## Executive Summary
Excellent week! Revenue at 85% of monthly goal.

## Revenue
- This Week: $3,500
- MTD: $8,500
- Goal: $10,000 (85%)

## Completed Tasks
- [x] Client invoices sent
- [x] Project milestones delivered

## Bottlenecks
- ⚠️ 3 invoices pending payment

## Suggestions
- 💡 Follow up on pending invoices
```
