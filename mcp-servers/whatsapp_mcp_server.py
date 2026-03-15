"""
WhatsApp MCP Server - Business API Integration

This MCP server provides WhatsApp Business API integration for the AI Employee.
Supports sending messages, receiving messages, and managing contacts.

Setup:
1. Get WhatsApp Business API credentials from https://business.whatsapp.com
2. Add credentials to .env file
3. Run this server

Usage:
    python whatsapp_mcp_server.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppBusinessAPI:
    """WhatsApp Business API Client"""
    
    def __init__(self):
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.base_url = f'https://graph.facebook.com/v17.0/{self.phone_number_id}'
        
        # For demo/testing, use mock mode if no credentials
        self.mock_mode = not self.phone_number_id or not self.access_token
        
        if self.mock_mode:
            logger.warning("WhatsApp credentials not found. Running in MOCK mode.")
            logger.warning("Set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN in .env")
    
    def send_message(self, phone: str, message: str) -> Dict:
        """Send a WhatsApp message"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'message': f'Message would be sent to {phone}',
                'content': message[:50] + '...' if len(message) > 50 else message
            }
        
        try:
            url = f'{self.base_url}/messages'
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'message_id': response.json().get('messages', [{}])[0].get('id'),
                'phone': phone
            }
            
        except Exception as e:
            logger.error(f'Error sending WhatsApp message: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_template(self, phone: str, template_name: str, language: str = 'en', parameters: List = None) -> Dict:
        """Send a template message (for business-initiated conversations)"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'message': f'Template {template_name} would be sent to {phone}'
            }
        
        try:
            url = f'{self.base_url}/messages'
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language
                    }
                }
            }
            
            if parameters:
                data['template']['components'] = [{
                    'type': 'body',
                    'parameters': parameters
                }]
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'message_id': response.json().get('messages', [{}])[0].get('id'),
                'phone': phone
            }
            
        except Exception as e:
            logger.error(f'Error sending template: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_profile(self) -> Dict:
        """Get WhatsApp Business profile"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'profile': {
                    'name': 'AI Employee (Mock)',
                    'about': 'Automated assistant',
                    'verified': False
                }
            }
        
        try:
            url = f'https://graph.facebook.com/v17.0/{self.phone_number_id}'
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'profile': {
                    'name': data.get('name', 'Unknown'),
                    'about': data.get('about', ''),
                    'verified': data.get('verified', False)
                }
            }
            
        except Exception as e:
            logger.error(f'Error getting profile: {e}')
            return {
                'success': False,
                'error': str(e)
            }


class WhatsAppMCPServer:
    """WhatsApp MCP Server"""
    
    def __init__(self):
        self.api = WhatsAppBusinessAPI()
        self.vault_path = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle MCP request"""
        method = request.get('method', '')
        params = request.get('params', {})
        request_id = request.get('id', 1)
        
        logger.info(f'Handling method: {method}')
        
        try:
            if method == 'whatsapp/send':
                result = self.api.send_message(
                    phone=params.get('phone', ''),
                    message=params.get('message', '')
                )
            
            elif method == 'whatsapp/send_template':
                result = self.api.send_template(
                    phone=params.get('phone', ''),
                    template_name=params.get('template', ''),
                    language=params.get('language', 'en'),
                    parameters=params.get('parameters', [])
                )
            
            elif method == 'whatsapp/get_profile':
                result = self.api.get_profile()
            
            elif method == 'whatsapp/log_message':
                # Log incoming message to vault
                result = self.log_message(params)
            
            else:
                result = {
                    'success': False,
                    'error': f'Unknown method: {method}'
                }
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f'Error handling {method}: {e}')
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }
    
    def log_message(self, params: Dict) -> Dict:
        """Log incoming WhatsApp message to vault"""
        from_phone = params.get('from', 'Unknown')
        message = params.get('message', '')
        timestamp = params.get('timestamp', datetime.now().isoformat())
        
        filename = f'WHATSAPP_{from_phone}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        filepath = self.needs_action / filename
        
        content = f'''---
type: whatsapp
from: {from_phone}
received: {timestamp}
status: pending
---

# WhatsApp Message

**From:** {from_phone}
**Received:** {timestamp}

## Message Content

{message}

## Suggested Actions

- [ ] Reply to sender
- [ ] Mark as done
- [ ] Escalate if urgent
'''
        
        filepath.write_text(content, encoding='utf-8')
        
        return {
            'success': True,
            'file': str(filepath),
            'filename': filename
        }


def main():
    """Main entry point"""
    print("=" * 60)
    print("💬 WhatsApp MCP Server")
    print("=" * 60)
    print()
    
    server = WhatsAppMCPServer()
    
    print("Server running. Send JSON-RPC requests via stdin.")
    print("Example request:")
    print('{"method": "whatsapp/send", "params": {"phone": "+1234567890", "message": "Hello!"}, "id": 1}')
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Read requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {
                    'code': -32700,
                    'message': 'Parse error'
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == '__main__':
    main()
