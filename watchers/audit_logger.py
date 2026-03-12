"""
Audit Logger - Comprehensive audit logging for AI Employee

Logs all actions, decisions, and state changes for compliance and debugging.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Comprehensive audit logging."""
    
    def __init__(self, vault_path: str):
        """
        Initialize audit logger.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.vault_path / 'Audit'
        
        # Ensure directories exist
        for folder in [self.logs_dir, self.audit_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Daily audit file
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.audit_file = self.audit_dir / f'{self.today}.jsonl'
    
    def log(self, event_type: str, actor: str, action: str, 
            target: str = None, parameters: Dict = None, 
            result: str = 'success', details: Any = None):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (action, decision, state_change, error)
            actor: Who/what performed the action (gmail_watcher, qwen_code, human)
            action: What action was performed
            target: What was acted upon
            parameters: Action parameters
            result: success, failed, pending
            details: Additional details
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'actor': actor,
            'action': action,
            'target': target,
            'parameters': parameters or {},
            'result': result,
            'details': details
        }
        
        # Write to daily audit file (JSONL format)
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Also log to standard logger
        log_msg = f"[{event_type}] {actor} -> {action}"
        if target:
            log_msg += f" on {target}"
        log_msg += f" [{result}]"
        
        if result == 'success':
            self.logger.info(log_msg)
        elif result == 'failed':
            self.logger.error(log_msg)
        else:
            self.logger.warning(log_msg)
    
    def log_action(self, actor: str, action: str, target: str, **kwargs):
        """Log an action."""
        self.log('action', actor, action, target, result='success', **kwargs)
    
    def log_decision(self, actor: str, decision: str, reasoning: str, **kwargs):
        """Log a decision."""
        self.log('decision', actor, decision, parameters={'reasoning': reasoning}, **kwargs)
    
    def log_error(self, actor: str, error: str, target: str = None, **kwargs):
        """Log an error."""
        self.log('error', actor, error, target, result='failed', **kwargs)
    
    def log_state_change(self, actor: str, from_state: str, to_state: str, target: str):
        """Log a state change."""
        self.log('state_change', actor, f'{from_state} -> {to_state}', target)
    
    def get_audit_trail(self, date: str = None, event_type: str = None, 
                       actor: str = None) -> list:
        """
        Get audit trail for querying.
        
        Args:
            date: Date to filter (YYYY-MM-DD)
            event_type: Filter by event type
            actor: Filter by actor
            
        Returns:
            List of audit entries
        """
        if not date:
            date = self.today
        
        audit_file = self.audit_dir / f'{date}.jsonl'
        
        if not audit_file.exists():
            return []
        
        entries = []
        with open(audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                
                # Apply filters
                if event_type and entry.get('event_type') != event_type:
                    continue
                if actor and entry.get('actor') != actor:
                    continue
                
                entries.append(entry)
        
        return entries
    
    def generate_daily_report(self, date: str = None) -> str:
        """
        Generate daily audit report.
        
        Args:
            date: Date to report (YYYY-MM-DD)
            
        Returns:
            Report content
        """
        if not date:
            date = self.today
        
        entries = self.get_audit_trail(date)
        
        if not entries:
            return f'# Daily Audit Report - {date}\n\nNo activity recorded.'
        
        # Aggregate stats
        stats = {
            'total': len(entries),
            'by_type': {},
            'by_actor': {},
            'by_result': {},
            'errors': []
        }
        
        for entry in entries:
            # Count by type
            event_type = entry.get('event_type', 'unknown')
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            stats['by_actor'][actor] = stats['by_actor'].get(actor, 0) + 1
            
            # Count by result
            result = entry.get('result', 'unknown')
            stats['by_result'][result] = stats['by_result'].get(result, 0) + 1
            
            # Collect errors
            if entry.get('result') == 'failed':
                stats['errors'].append(entry)
        
        # Generate report
        report = f'''# Daily Audit Report - {date}

## Summary

| Metric | Count |
|--------|-------|
| Total Events | {stats['total']} |
| Actions | {stats['by_type'].get('action', 0)} |
| Decisions | {stats['by_type'].get('decision', 0)} |
| Errors | {stats['by_type'].get('error', 0)} |

## By Actor

| Actor | Events |
|-------|--------|
'''
        
        for actor, count in stats['by_actor'].items():
            report += f'| {actor} | {count} |\n'
        
        report += f'''
## Results

| Result | Count |
|--------|-------|
| Success | {stats['by_result'].get('success', 0)} |
| Failed | {stats['by_result'].get('failed', 0)} |
| Pending | {stats['by_result'].get('pending', 0)} |

## Errors

'''
        
        if stats['errors']:
            for error in stats['errors']:
                report += f'''### {error.get('timestamp', 'Unknown')}

- **Actor:** {error.get('actor', 'Unknown')}
- **Action:** {error.get('action', 'Unknown')}
- **Target:** {error.get('target', 'Unknown')}
- **Details:** {error.get('details', 'N/A')}

'''
        else:
            report += '_No errors recorded today ✓_\n'
        
        return report


class ErrorRecovery:
    """Error recovery and graceful degradation."""
    
    def __init__(self, vault_path: str, audit_logger: AuditLogger = None):
        """
        Initialize error recovery.
        
        Args:
            vault_path: Path to Obsidian vault
            audit_logger: Audit logger instance
        """
        self.vault_path = Path(vault_path)
        self.audit = audit_logger or AuditLogger(str(vault_path))
        self.error_counts = {}
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def should_retry(self, error_key: str) -> bool:
        """
        Check if an operation should be retried.
        
        Args:
            error_key: Unique key for this error type
            
        Returns:
            True if should retry
        """
        count = self.error_counts.get(error_key, 0)
        return count < self.max_retries
    
    def record_error(self, error_key: str):
        """
        Record an error for retry tracking.
        
        Args:
            error_key: Unique key for this error type
        """
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        self.audit.log_error(
            'error_recovery',
            f'Error {error_key} (count: {self.error_counts[error_key]})'
        )
    
    def reset_error_count(self, error_key: str):
        """
        Reset error count after successful operation.
        
        Args:
            error_key: Unique key for this error type
        """
        if error_key in self.error_counts:
            del self.error_counts[error_key]
    
    def graceful_degradation(self, component: str, fallback_action: str):
        """
        Implement graceful degradation when component fails.
        
        Args:
            component: Failed component name
            fallback_action: Fallback action to take
        """
        self.audit.log(
            'state_change',
            'error_recovery',
            f'Degraded mode: {component}',
            parameters={'fallback': fallback_action}
        )
        
        # Create alert file
        alerts_dir = self.vault_path / 'Alerts'
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = alerts_dir / f'DEGRADED_{component}_{timestamp}.md'
        
        content = f'''---
type: degradation_alert
component: {component}
created: {datetime.now().isoformat()}
status: active
---

# Component Degradation Alert

**Component:** {component}

**Status:** Operating in degraded mode

**Fallback Action:** {fallback_action}

---

## Resolution

1. Fix the underlying issue with {component}
2. Restart the component
3. Move this file to /Done when resolved

---

*Generated by Error Recovery System*
'''
        
        alert_file.write_text(content, encoding='utf-8')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Logger & Error Recovery')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault')
    parser.add_argument('--report', action='store_true',
                       help='Generate daily audit report')
    parser.add_argument('--query', type=str,
                       help='Query audit trail (JSON filter)')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    audit = AuditLogger(str(vault_path))
    
    if args.report:
        report = audit.generate_daily_report()
        print(report)
    
    elif args.query:
        try:
            filters = json.loads(args.query)
            entries = audit.get_audit_trail(**filters)
            print(json.dumps(entries, indent=2))
        except json.JSONDecodeError:
            print('Invalid JSON filter')
    
    else:
        print('Audit Logger & Error Recovery System')
        print('\nCommands:')
        print('  --report    Generate daily audit report')
        print('  --query \'{"event_type": "error"}\'   Query audit trail')


if __name__ == '__main__':
    main()
