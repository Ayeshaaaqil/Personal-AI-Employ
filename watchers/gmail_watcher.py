"""
Gmail Watcher - Monitors Gmail for new important/unread emails.

This watcher uses the Gmail API to continuously monitor your inbox
for new emails and creates actionable .md files in the Needs_Action folder.

Prerequisites:
1. credentials.json in project root
2. First-time auth: python gmail_watcher.py --auth
"""

import time
import logging
import json
import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from email import message_from_bytes

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher using Gmail API.
    
    Monitors inbox for new unread/important emails and creates
    action files in Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to credentials.json (default: ./credentials.json)
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path) if credentials_path else Path('credentials.json')
        self.token_path = Path('token.json')  # Auto-generated OAuth token
        
        # Keywords that indicate high priority
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 
                                   'pricing', 'quote', 'proposal', 'contract']
        
        # Load known contacts from Company_Handbook if exists
        self.known_contacts = self._load_known_contacts()
        
        # Initialize Gmail service
        self.service = self._authenticate()
    
    def _load_known_contacts(self) -> list:
        """Load known contacts from Company_Handbook.md."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        contacts = []
        
        if handbook_path.exists():
            content = handbook_path.read_text()
            # Simple extraction - look for email patterns
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            contacts.extend(emails)
        
        return contacts
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Credentials file not found: {self.credentials_path}\n'
                        'Please ensure credentials.json is in the project root.'
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0, open_browser=False)
            
            # Save token
            self.token_path.write_text(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_updates(self) -> list:
        """
        Check for new unread emails in inbox.
        
        Returns:
            list: List of new email messages
        """
        try:
            # Search for unread emails in inbox
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg and msg.get('id') and msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def create_action_file(self, message) -> Path:
        """
        Create a .md action file for the email.
        
        Args:
            message: Gmail message object
            
        Returns:
            Path: Path to the created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', '')
            
            # Extract body
            body = self._extract_body(msg)
            
            # Determine priority
            priority = self._determine_priority(from_email, subject, body)
            
            # Check if from known contact
            is_known = self._is_known_contact(from_email)
            
            # Create action file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_subject = self._sanitize_filename(subject)[:50]
            filename = f'EMAIL_{timestamp}_{safe_subject}.md'
            filepath = self.needs_action / filename
            
            content = f'''---
type: email
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
date_original: {date}
priority: {priority}
status: pending
is_known_contact: {str(is_known).lower()}
labels: {', '.join(msg.get('labelIds', []))}
---

# Email Received

**From:** {from_email}
**Subject:** {subject}
**Received:** {date}
**Priority:** {priority.upper()}

---

## Email Content

{body}

---

## Suggested Actions

- [ ] Read and understand the email
- [ ] Determine required response
- [ ] Draft reply (if needed)
- [ ] Mark as processed

## Quick Reply Template

Hi {from_email.split('@')[0]},

Thank you for your email regarding "{subject}".

[Your response here]

Best regards,
[Your Name]

---

*Created by Gmail Watcher at {datetime.now().isoformat()}*
'''
            
            filepath.write_text(content, encoding='utf-8')
            
            # Mark email as read
            self.service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.logger.info(f'Created action file: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _extract_body(self, msg) -> str:
        """Extract email body from message."""
        try:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = base64.urlsafe_b64decode(part['body']['data'])
                        return body_data.decode('utf-8', errors='ignore')
            
            # Fallback to snippet
            return msg.get('snippet', '')
            
        except Exception as e:
            self.logger.error(f'Error extracting body: {e}')
            return msg.get('snippet', '')
    
    def _determine_priority(self, from_email: str, subject: str, body: str) -> str:
        """Determine email priority based on content."""
        text = (subject + ' ' + body).lower()
        
        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in text:
                return 'high'
        
        # Check if from known contact
        if self._is_known_contact(from_email):
            return 'medium'
        
        return 'low'
    
    def _is_known_contact(self, from_email: str) -> bool:
        """Check if email is from a known contact."""
        # Extract just the email address if it's in "Name <email>" format
        import re
        match = re.search(r'<([^>]+)>', from_email)
        email = match.group(1) if match else from_email
        
        for known in self.known_contacts:
            if known.lower() in email.lower():
                return True
        return False
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        import re
        
        # Remove invalid filename characters for Windows
        # Invalid: < > : " / \ | ? *
        invalid_chars = r'[<>:"/\\|？*]'
        text = re.sub(invalid_chars, '', text)
        
        # Replace other problematic characters
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        
        # Remove emojis and special unicode
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Trim length
        text = text[:100]
        
        return text.strip()


def main():
    """Main entry point for Gmail Watcher."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--credentials', default='../credentials.json',
                       help='Path to credentials.json')
    parser.add_argument('--interval', type=int, default=120,
                       help='Check interval in seconds')
    parser.add_argument('--auth', action='store_true',
                       help='Run authentication only')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    if args.auth:
        # Just run authentication
        print('Running Gmail API authentication...')
        watcher = GmailWatcher(str(vault_path), args.credentials)
        print('Authentication successful! Token saved to token.json')
        return
    
    # Run watcher
    try:
        watcher = GmailWatcher(str(vault_path), args.credentials, args.interval)
        watcher.run()
    except FileNotFoundError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error starting Gmail Watcher: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
