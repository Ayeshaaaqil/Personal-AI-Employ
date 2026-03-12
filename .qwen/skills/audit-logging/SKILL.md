---
name: audit-logging
description: |
  Comprehensive audit logging for AI Employee. Logs all actions, decisions,
  and state changes for compliance and debugging. Includes error recovery.
---

# Audit Logging Skill

Complete audit trail and error recovery system.

## Quick Reference

### Generate Daily Report

```bash
python watchers\audit_logger.py ../AI_Employee_Vault --report
```

### Query Audit Trail

```bash
python watchers\audit_logger.py ../AI_Employee_Vault --query '{"event_type": "error"}'
```

## Features

- ✅ Action logging
- ✅ Decision logging
- ✅ Error tracking
- ✅ State change tracking
- ✅ Daily reports
- ✅ Error recovery
- ✅ Graceful degradation

## Audit Log Location

Logs saved to: `AI_Employee_Vault/Audit/YYYY-MM-DD.jsonl`

## Log Format

```json
{
  "timestamp": "2026-03-06T15:30:00",
  "event_type": "action",
  "actor": "gmail_watcher",
  "action": "email_received",
  "target": "client@example.com",
  "result": "success"
}
```

## Error Recovery

Automatic retry with exponential backoff:
- Max retries: 3
- Delay: 5 seconds
- Graceful degradation on failure
