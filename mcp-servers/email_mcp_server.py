"""
Email MCP Server - Gmail integration via MCP protocol

Provides tools for:
- Sending emails
- Reading emails
- Searching emails
- Managing labels
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailMCP')


class EmailMCPServer:
    """Email MCP Server for Gmail integration."""
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            token_path = Path('token.json')
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(token_path)
                self.service = build('gmail', 'v1', credentials=creds)
                logger.info('Gmail API authenticated')
            else:
                logger.warning('Gmail token not found. Run gmail_watcher.py --auth first')
        except Exception as e:
            logger.error(f'Authentication failed: {e}')
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> dict:
        """Send an email."""
        logger.info(f'Sending email to {to}')
        
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body, 'plain', 'utf-8')
        message['to'] = to
        message['from'] = 'AI Employee'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            sent = self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
            logger.info(f'Email sent: {sent["id"]}')
            return {'success': True, 'message_id': sent['id']}
        except Exception as e:
            logger.error(f'Failed to send: {e}')
            return {'success': False, 'error': str(e)}
    
    def read_email(self, message_id: str) -> dict:
        """Read an email by ID."""
        try:
            msg = self.service.users().messages().get(userId='me', id=message_id).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            return {
                'success': True,
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'snippet': msg.get('snippet', '')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_emails(self, query: str, max_results: int = 10) -> dict:
        """Search emails."""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return {
                'success': True,
                'count': len(messages),
                'messages': [{'id': m['id'], 'threadId': m['threadId']} for m in messages]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method', '')
    params = request.get('params', {})
    
    server = EmailMCPServer()
    
    if method == 'email/send':
        result = server.send_email(
            to=params.get('to', ''),
            subject=params.get('subject', ''),
            body=params.get('body', ''),
            in_reply_to=params.get('in_reply_to')
        )
    elif method == 'email/read':
        result = server.read_email(params.get('message_id', ''))
    elif method == 'email/search':
        result = server.search_emails(
            query=params.get('query', ''),
            max_results=params.get('max_results', 10)
        )
    else:
        result = {'success': False, 'error': f'Unknown method: {method}'}
    
    return {
        'jsonrpc': '2.0',
        'id': request.get('id'),
        'result': result
    }


def main():
    """Run MCP server (stdio mode)."""
    logger.info('Email MCP Server started')
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': str(e)}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    main()
