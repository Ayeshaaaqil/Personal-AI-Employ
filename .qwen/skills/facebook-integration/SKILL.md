---
name: facebook-integration
description: |
  Facebook integration for AI Employee. Monitor notifications, messages,
  and post updates automatically. Uses Playwright for browser automation.
---

# Facebook Integration Skill

Monitor and post to Facebook automatically.

## Quick Reference

### Login (First Time)

```bash
cd watchers
python facebook_watcher.py --login
```

### Run Watcher

```bash
python facebook_watcher.py ../AI_Employee_Vault
```

### Post to Facebook

```bash
python facebook_watcher.py ../AI_Employee_Vault --post "Your post content"
```

## Features

- ✅ Monitor notifications
- ✅ Monitor messages
- ✅ Auto-post updates
- ✅ Create action files for activity

## Workflow

```
Facebook activity detected
    ↓
Creates: Needs_Action/FACEBOOK_*.md
    ↓
Orchestrator triggers Qwen Code
    ↓
Qwen generates response
    ↓
Auto-post or save for approval
```
