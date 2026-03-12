"""
Gmail Auto Responder - Automatically reply to emails

This script checks for approved email replies and sends them automatically.
Use with the approval workflow.
"""

import sys
import logging
import base64
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly']


class GmailAutoResponder:
    """Automatically send approved email replies."""
    
    def __init__(self, vault_path: str, credentials_path: str = None):
        """
        Initialize auto responder.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json
        """
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.credentials_path = Path(credentials_path) if credentials_path else Path('credentials.json')
        self.token_path = Path('token.json')
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0, open_browser=False)
            
            self.token_path.write_text(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def check_approved_emails(self) -> list:
        """Check for approved email replies."""
        if not self.approved.exists():
            return []
        
        approved = []
        for file in self.approved.glob('APPROVE_EMAIL_*.md'):
            approved.append(file)
        
        return approved
    
    def extract_email_details(self, filepath: Path) -> dict:
        """Extract email details from approval file."""
        content = filepath.read_text(encoding='utf-8')
        
        details = {
            'to': '',
            'subject': '',
            'body': '',
            'in_reply_to': ''
        }
        
        # Parse YAML frontmatter
        in_content = False
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_content:
                    in_content = True
                else:
                    break
            elif in_content:
                if line.startswith('to:'):
                    details['to'] = line.split(':', 1)[1].strip()
                elif line.startswith('subject:'):
                    details['subject'] = line.split(':', 1)[1].strip()
                elif line.startswith('in_reply_to:'):
                    details['in_reply_to'] = line.split(':', 1)[1].strip()
        
        # Extract body from markdown content
        body_start = False
        body_lines = []
        for line in lines:
            if '## Email Body' in line or '## Content' in line or '## Reply' in line:
                body_start = True
                continue
            elif body_start:
                if line.startswith('---') or line.startswith('##'):
                    break
                body_lines.append(line)
        
        details['body'] = '\n'.join(body_lines).strip()
        
        # If no body section found, look for quoted text
        if not details['body']:
            for line in lines:
                if line.startswith('>') and not line.startswith('---'):
                    details['body'] = line[1:].strip()
                    break
        
        return details
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> bool:
        """
        Send email via Gmail API.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            in_reply_to: Message ID to reply to
            
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info(f'Sending email to {to}...')
            
            # Create message
            from email.mime.text import MIMEText
            from email.header import Header
            
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['from'] = 'AI Employee'
            message['subject'] = subject
            
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            self.logger.info(f'Email sent! Message ID: {sent_message["id"]}')
            return True
            
        except Exception as e:
            self.logger.error(f'Error sending email: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def send_approved_emails(self) -> int:
        """Send all approved emails."""
        approved = self.check_approved_emails()
        
        if not approved:
            return 0
        
        self.logger.info(f'Found {len(approved)} approved emails to send')
        
        sent_count = 0
        for filepath in approved:
            self.logger.info(f'Processing: {filepath.name}')
            
            details = self.extract_email_details(filepath)
            
            if not details['to'] or not details['body']:
                self.logger.error(f'Could not extract email details from {filepath}')
                continue
            
            if self.send_email(
                to=details['to'],
                subject=details['subject'],
                body=details['body'],
                in_reply_to=details.get('in_reply_to')
            ):
                sent_count += 1
                
                # Move to Done
                dest = self.done / filepath.name
                filepath.rename(dest)
                self.logger.info(f'Moved to Done: {dest}')
                
                # Log
                self.log_action(filepath.name, 'sent', details)
        
        return sent_count
    
    def log_action(self, filename: str, status: str, details: dict):
        """Log email action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'email_{today}.md'
        
        log_entry = f'''
## {datetime.now().isoformat()} - {filename}

**Status:** {status}
**To:** {details.get('to', 'N/A')}
**Subject:** {details.get('subject', 'N/A')}

'''
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            log_file.write_text(f'# Email Log - {today}\n{log_entry}', encoding='utf-8')
    
    def run_once(self) -> int:
        """Send approved emails once."""
        return self.send_approved_emails()
    
    def run_continuous(self, check_interval: int = 60):
        """Run continuously."""
        self.logger.info(f'Starting Gmail Auto Responder (interval: {check_interval}s)')
        
        import time
        
        try:
            while True:
                self.run_once()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Auto Responder stopped')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Auto Responder')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--credentials', default='../credentials.json',
                       help='Path to credentials.json')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault not found: {vault_path}')
        sys.exit(1)
    
    responder = GmailAutoResponder(str(vault_path), args.credentials)
    
    if args.once:
        sent = responder.run_once()
        print(f'Sent {sent} emails')
    else:
        responder.run_continuous(args.interval)


if __name__ == '__main__':
    main()
