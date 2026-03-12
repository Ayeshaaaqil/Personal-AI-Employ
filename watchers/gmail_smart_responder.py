"""
Gmail Smart Auto Responder - AI-powered email replies

Automatically reads emails, generates replies using AI, and sends them.
Configurable rules in Company_Handbook.md
"""

import sys
import logging
import base64
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.modify']


class GmailSmartResponder:
    """AI-powered Gmail auto responder."""
    
    def __init__(self, vault_path: str, credentials_path: str = None):
        """
        Initialize smart responder.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.credentials_path = Path(credentials_path) if credentials_path else Path('credentials.json')
        self.token_path = Path('token.json')
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.service = self._authenticate()
        
        # Load auto-reply rules from Company Handbook
        self.auto_reply_rules = self._load_rules()
        self.known_contacts = self._load_known_contacts()
    
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
    
    def _load_rules(self) -> dict:
        """Load auto-reply rules from Company Handbook."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        
        if not handbook_path.exists():
            return {}
        
        content = handbook_path.read_text(encoding='utf-8')
        
        # Simple rule parsing
        rules = {
            'auto_reply_subjects': ['test', 'hello', 'hi'],
            'auto_reply_keywords': ['ai employee', 'automation'],
            'no_reply_subjects': ['newsletter', 'unsubscribe', 'spam'],
        }
        
        # Parse from handbook (simple keyword extraction)
        if 'Auto Reply' in content:
            if 'test' in content.lower():
                rules['auto_reply_subjects'].append('test')
            if 'hello' in content.lower():
                rules['auto_reply_subjects'].append('hello')
        
        return rules
    
    def _load_known_contacts(self) -> list:
        """Load known contacts from Company Handbook."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        contacts = []
        
        if handbook_path.exists():
            content = handbook_path.read_text(encoding='utf-8')
            # Extract email addresses
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            contacts.extend(emails)
        
        return contacts
    
    def generate_reply(self, from_email: str, subject: str, body: str) -> str:
        """
        Generate appropriate reply based on email content.
        
        Args:
            from_email: Sender's email
            subject: Email subject
            body: Email body
            
        Returns:
            str: Generated reply
        """
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Rule 1: Test emails
        if 'test' in subject_lower or 'test' in body_lower:
            return f'''Hi there,

Thank you for testing AI Employee! ✅

This is an automated response to confirm that the email system is working correctly.

Best regards,
AI Employee
Automated Assistant'''
        
        # Rule 2: Greetings
        if any(greeting in subject_lower for greeting in ['hello', 'hi', 'hey']):
            return f'''Hello! 👋

Thank you for reaching out to AI Employee. I'm monitoring this inbox 24/7.

Your message has been received and logged. I'll process it shortly.

Best regards,
AI Employee
Automated Assistant'''
        
        # Rule 3: Known contacts
        if any(contact in from_email.lower() for contact in self.known_contacts):
            return f'''Hi,

Thank you for your email! ✅

I've received your message and it's been logged in my system. I'll respond within 24 hours.

Best regards,
AI Employee
Automated Assistant'''
        
        # Rule 4: AI Employee inquiries
        if 'ai employee' in body_lower or 'automation' in body_lower:
            return f'''Hello!

Thank you for your interest in AI Employee! 🤖

AI Employee is an autonomous assistant that can:
✅ Monitor emails 24/7
✅ Process LinkedIn messages
✅ Manage tasks and approvals
✅ Generate reports

Feel free to reach out with any questions!

Best regards,
AI Employee
Automated Assistant'''
        
        # Default reply for unknown emails
        return f'''Hello,

Thank you for your email. This is an automated acknowledgment from AI Employee.

Your message has been received and will be processed shortly.

Best regards,
AI Employee
Automated Assistant'''
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> bool:
        """Send email via Gmail API."""
        try:
            self.logger.info(f'Sending email to {to}...')
            
            from email.mime.text import MIMEText
            
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['from'] = 'AI Employee'
            message['subject'] = subject
            
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            self.logger.info(f'✓ Email sent! Message ID: {sent_message["id"]}')
            return True
            
        except Exception as e:
            self.logger.error(f'Error sending email: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def process_email(self, email_file: Path) -> bool:
        """
        Process a single email and send auto-reply.
        
        Args:
            email_file: Path to email action file
            
        Returns:
            bool: True if reply sent successfully
        """
        self.logger.info(f'Processing: {email_file.name}')
        
        # Read email file
        content = email_file.read_text(encoding='utf-8')
        
        # Extract email details
        from_email = ''
        subject = ''
        body = ''
        message_id = ''
        
        lines = content.split('\n')
        in_body = False
        
        for line in lines:
            if line.startswith('from:'):
                from_email = line.split(':', 1)[1].strip()
            elif line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
            elif line.startswith('message_id:'):
                message_id = line.split(':', 1)[1].strip()
            elif '## Email Content' in line:
                in_body = True
            elif in_body and line.startswith('##'):
                break
            elif in_body:
                body += line + '\n'
        
        if not from_email or not subject:
            self.logger.error(f'Could not extract email details from {email_file}')
            return False
        
        # Generate reply
        reply = self.generate_reply(from_email, subject, body)
        
        # Send reply
        reply_subject = f"Re: {subject}"
        success = self.send_email(
            to=from_email,
            subject=reply_subject,
            body=reply,
            in_reply_to=message_id
        )
        
        if success:
            # Move to Done
            dest = self.done / email_file.name
            email_file.rename(dest)
            self.logger.info(f'Moved to Done: {dest}')
            
            # Log
            self.log_action(email_file.name, from_email, subject, 'replied')
        
        return success
    
    def log_action(self, filename: str, from_email: str, subject: str, action: str):
        """Log email action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'email_auto_{today}.md'
        
        log_entry = f'''
## {datetime.now().isoformat()} - {filename}

**From:** {from_email}
**Subject:** {subject}
**Action:** {action}

'''
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            log_file.write_text(f'# Auto Email Log - {today}\n{log_entry}', encoding='utf-8')
    
    def process_all_emails(self) -> int:
        """Process all emails in Needs_Action folder."""
        if not self.needs_action.exists():
            return 0
        
        count = 0
        for email_file in self.needs_action.glob('EMAIL_*.md'):
            if self.process_email(email_file):
                count += 1
        
        return count
    
    def run_continuous(self, check_interval: int = 120):
        """Run continuously, checking for new emails."""
        self.logger.info(f'Starting Gmail Smart Responder (interval: {check_interval}s)')
        
        import time
        
        try:
            while True:
                processed = self.process_all_emails()
                if processed > 0:
                    self.logger.info(f'Processed {processed} emails')
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Smart Responder stopped')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Smart Auto Responder')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--credentials', default='../credentials.json',
                       help='Path to credentials.json')
    parser.add_argument('--interval', type=int, default=120,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault not found: {vault_path}')
        sys.exit(1)
    
    responder = GmailSmartResponder(str(vault_path), args.credentials)
    
    if args.once:
        count = responder.process_all_emails()
        print(f'Processed {count} emails, sent {count} replies')
    else:
        responder.run_continuous(args.interval)


if __name__ == '__main__':
    main()
