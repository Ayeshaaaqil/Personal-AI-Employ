"""
Orchestrator - Master process that manages the AI Employee system.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending actions
3. Manages the approval workflow
4. Updates the Dashboard with recent activity
"""

import subprocess
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the approval workflow.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        for dir_path in [self.needs_action, self.approved, self.pending_approval, self.done, self.plans, self.logs]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)

        # Track processed files
        self.processed_files = set()
    
    def check_needs_action(self) -> list:
        """
        Check for new files in Needs_Action folder.
        
        Returns:
            list: List of new markdown files to process
        """
        new_files = []
        
        if not self.needs_action.exists():
            return new_files
        
        for file in self.needs_action.glob('*.md'):
            if file.name not in self.processed_files:
                new_files.append(file)
        
        return new_files
    
    def check_approved(self) -> list:
        """
        Check for approved action files ready for execution.
        
        Returns:
            list: List of approved files to execute
        """
        if not self.approved.exists():
            return []
        
        return list(self.approved.glob('*.md'))
    
    def trigger_qwen(self, context: str) -> bool:
        """
        Trigger Qwen Code to process pending actions.

        Args:
            context: Context/prompt for Qwen

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info('Triggering Qwen Code...')

        prompt = f'''You are the AI Employee. Process the pending actions in the vault.

Context: {context}

Follow these rules:
1. Read all files in /Needs_Action
2. Create a Plan.md file with the steps to handle each item
3. For sensitive actions (payments, new contacts), create approval request files in /Pending_Approval
4. For auto-approved actions, proceed and log the results
5. Update the Dashboard.md with recent activity
6. Move completed items to /Done

Remember the Company_Handbook.md rules when making decisions.'''

        try:
            # Run Qwen Code with the prompt
            # Use shell=True on Windows to properly find the command
            import platform
            use_shell = platform.system() == 'Windows'
            
            result = subprocess.run(
                ['qwen', '--prompt', prompt],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=use_shell
            )

            if result.returncode == 0:
                self.logger.info('Qwen Code completed successfully')
                return True
            else:
                self.logger.error(f'Qwen Code error: {result.stderr}')
                return False

        except subprocess.TimeoutExpired:
            self.logger.error('Qwen Code timed out after 5 minutes')
            return False
        except FileNotFoundError as e:
            self.logger.error(f'Qwen Code not found: {e}')
            self.logger.error('Try running: where qwen (Windows) or which qwen (Linux/Mac)')
            return False
        except Exception as e:
            self.logger.error(f'Error triggering Qwen Code: {e}')
            return False
    
    def execute_approved_action(self, filepath: Path) -> bool:
        """
        Execute an approved action.
        
        Args:
            filepath: Path to the approved action file
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f'Executing approved action: {filepath.name}')
        
        # Read the approval file to determine action type
        content = filepath.read_text()
        
        # Log the execution
        self.log_action(filepath.name, 'executed', content)
        
        # Move to Done
        dest = self.done / filepath.name
        shutil.move(str(filepath), str(dest))
        
        self.logger.info(f'Action completed: {filepath.name} -> Done/')
        return True
    
    def log_action(self, action: str, status: str, details: str):
        """
        Log an action to the logs folder.
        
        Args:
            action: Action name
            status: Status (success, failed, pending)
            details: Action details
        """
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.md'
        
        log_entry = f'''
## {datetime.now().isoformat()} - {action}

**Status:** {status}

**Details:**
```
{details[:500]}...  # Truncate if too long
```

'''
        
        if log_file.exists():
            with open(log_file, 'a') as f:
                f.write(log_entry)
        else:
            log_file.write_text(f'# Log for {today}\n{log_entry}')
    
    def update_dashboard(self, action: str = None, status: str = None):
        """
        Update the Dashboard.md with recent activity and current status.

        Args:
            action: Action description (optional)
            status: Action status (optional)
        """
        if not self.dashboard.exists():
            return

        content = self.dashboard.read_text()
        
        # Count items in each folder
        pending_count = len(list(self.needs_action.glob('*.md')))
        approval_count = len(list(self.pending_approval.glob('*.md'))) if self.pending_approval.exists() else 0
        done_count = len(list(self.done.glob('*.md')))
        
        # Update Quick Status table
        import re
        
        # Build the new status table with correct counts
        new_status_table = f'''| Pending Actions | {pending_count} |
| Awaiting Approval | {approval_count} |
| Completed Today | {done_count} |
| Revenue This Week | $0 |'''
        
        # Match the table with flexible whitespace
        content = re.sub(
            r'\| Pending Actions\s*\|.*\|\n\| Awaiting Approval\s*\|.*\|\n\| Completed Today\s*\|.*\|\n\| Revenue This Week\s*\|.*\|',
            new_status_table,
            content
        )

        # Add to recent activity section if action provided
        if action and status:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            activity_line = f'- [{timestamp}] {action} ({status})\n'
            
            if '## Recent Activity' in content:
                lines = content.split('\n')
                new_lines = []
                inserted = False
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line == '## Recent Activity' and not inserted:
                        new_lines.append('')
                        new_lines.append(activity_line)
                        inserted = True
                
                if inserted:
                    # Add remaining lines
                    new_lines.extend(lines[i+1:])
                    content = '\n'.join(new_lines)

        # Update Pending Approvals section
        if self.pending_approval.exists():
            approval_files = list(self.pending_approval.glob('*.md'))
            if approval_files:
                approvals_list = ''
                for f in approval_files:
                    approvals_list += f'- [FILE] {f.stem}\n'
                
                # Replace entire Pending Approvals section
                content = re.sub(
                    r'## Pending Approvals\n\n.*?(?=\n## |\Z)',
                    f'## Pending Approvals\n\n{approvals_list}\n',
                    content,
                    flags=re.DOTALL
                )
            else:
                content = re.sub(
                    r'## Pending Approvals\n\n.*?(?=\n## |\Z)',
                    '## Pending Approvals\n\n_No pending approvals_\n\n',
                    content,
                    flags=re.DOTALL
                )

        self.dashboard.write_text(content, encoding='utf-8')
        self.logger.info('Dashboard updated')
    
    def run_once(self) -> int:
        """
        Run one iteration of the orchestrator.
        
        Returns:
            int: Number of actions processed
        """
        actions_processed = 0
        
        # Check for approved actions first
        approved_files = self.check_approved()
        for filepath in approved_files:
            if self.execute_approved_action(filepath):
                self.update_dashboard(filepath.stem, 'completed')
                actions_processed += 1
        
        # Check for new items needing action
        new_files = self.check_needs_action()
        if new_files:
            self.logger.info(f'Found {len(new_files)} new items in Needs_Action')

            # Trigger Qwen to process
            context = f'Found {len(new_files)} new items: {", ".join(f.name for f in new_files)}'
            if self.trigger_qwen(context):
                for f in new_files:
                    self.processed_files.add(f.name)
                    self.update_dashboard(f.stem, 'processing_started')
                    actions_processed += 1
        
        return actions_processed
    
    def run_continuous(self, check_interval: int = 30):
        """
        Run the orchestrator continuously.
        
        Args:
            check_interval: Seconds between checks
        """
        self.logger.info(f'Starting Orchestrator (check interval: {check_interval}s)')
        self.logger.info(f'Vault: {self.vault_path}')
        
        import time
        
        try:
            while True:
                self.run_once()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')


if __name__ == '__main__':
    import sys
    
    # Default vault path
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    
    # Allow custom vault path via command line
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    orchestrator = Orchestrator(str(vault_path))
    
    # Run in continuous mode
    orchestrator.run_continuous(check_interval=30)
