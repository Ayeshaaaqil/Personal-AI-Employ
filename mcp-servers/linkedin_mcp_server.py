"""
LinkedIn MCP Server - Web Automation

This MCP server provides LinkedIn integration via Playwright browser automation.
Supports posting updates, sending messages, and monitoring engagement.

Setup:
1. Install playwright: pip install playwright
2. Install browsers: playwright install chromium
3. Run login script first: python linkedin_login.py
4. Run this server

Usage:
    python linkedin_mcp_server.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInAutomation:
    """LinkedIn Automation via Playwright"""
    
    def __init__(self, session_path: str = None):
        self.session_path = Path(session_path) if session_path else Path('linkedin-session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Check if session exists
        self.has_session = (self.session_path / 'Default' / 'Cookies').exists()
        
        if not self.has_session:
            logger.warning("No LinkedIn session found. Run linkedin_login.py first!")
    
    def post_update(self, text: str) -> Dict:
        """Post an update to LinkedIn"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com/', timeout=60000)
                
                # Check if logged in
                if 'login' in page.url.lower():
                    browser.close()
                    return {
                        'success': False,
                        'error': 'Not logged in. Please run linkedin_login.py first.'
                    }
                
                # Click on "Start a post"
                try:
                    page.click('div[role="button"][aria-label*="post"]', timeout=5000)
                except:
                    # Try alternative selector
                    try:
                        page.click('button:has-text("Start a post")', timeout=5000)
                    except:
                        browser.close()
                        return {
                            'success': False,
                            'error': 'Could not find post button'
                        }
                
                # Wait for modal and type message
                try:
                    text_area = page.wait_for_selector('div[role="textbox"]', timeout=5000)
                    text_area.fill(text)
                    
                    # Click Post button
                    post_button = page.wait_for_selector('button:has-text("Post")', timeout=5000)
                    post_button.click()
                    
                    # Wait for confirmation
                    page.wait_for_timeout(3000)
                    
                    browser.close()
                    
                    return {
                        'success': True,
                        'message': 'Post published successfully',
                        'content': text[:50] + '...' if len(text) > 50 else text
                    }
                    
                except Exception as e:
                    browser.close()
                    return {
                        'success': False,
                        'error': f'Error posting: {str(e)}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Browser error: {str(e)}'
            }
    
    def send_message(self, recipient_name: str, message: str) -> Dict:
        """Send a message to a connection"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/', timeout=60000)
                
                if 'login' in page.url.lower():
                    browser.close()
                    return {
                        'success': False,
                        'error': 'Not logged in'
                    }
                
                # Search for recipient
                search_box = page.wait_for_selector('input[aria-label*="Search"]', timeout=5000)
                search_box.fill(recipient_name)
                page.wait_for_timeout(2000)
                
                # Click on first result
                try:
                    first_result = page.wait_for_selector('button.app-aware-link', timeout=5000)
                    first_result.click()
                    page.wait_for_timeout(3000)
                    
                    # Click Message button
                    try:
                        message_button = page.wait_for_selector('button:has-text("Message")', timeout=5000)
                        message_button.click()
                        page.wait_for_timeout(2000)
                        
                        # Type and send message
                        message_box = page.wait_for_selector('div[role="textbox"]', timeout=5000)
                        message_box.fill(message)
                        
                        send_button = page.wait_for_selector('button:has-text("Send")', timeout=5000)
                        send_button.click()
                        
                        browser.close()
                        
                        return {
                            'success': True,
                            'message': f'Message sent to {recipient_name}',
                            'recipient': recipient_name
                        }
                        
                    except:
                        browser.close()
                        return {
                            'success': False,
                            'error': 'Could not send message (may not be connected)'
                        }
                        
                except:
                    browser.close()
                    return {
                        'success': False,
                        'error': f'Could not find {recipient_name}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_profile_info(self) -> Dict:
        """Get current user profile info"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/mynetwork/', timeout=60000)
                
                if 'login' in page.url.lower():
                    browser.close()
                    return {
                        'success': False,
                        'error': 'Not logged in'
                    }
                
                # Get page title as basic info
                title = page.title()
                
                browser.close()
                
                return {
                    'success': True,
                    'profile': {
                        'title': title,
                        'session_valid': True
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class LinkedInMCPServer:
    """LinkedIn MCP Server"""
    
    def __init__(self):
        self.automation = LinkedInAutomation()
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
            if method == 'linkedin/post':
                result = self.automation.post_update(
                    text=params.get('text', '')
                )
            
            elif method == 'linkedin/send_message':
                result = self.automation.send_message(
                    recipient_name=params.get('recipient', ''),
                    message=params.get('message', '')
                )
            
            elif method == 'linkedin/get_profile':
                result = self.automation.get_profile_info()
            
            elif method == 'linkedin/log_activity':
                result = self.log_activity(params)
            
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
    
    def log_activity(self, params: Dict) -> Dict:
        """Log LinkedIn activity to vault"""
        activity_type = params.get('type', 'unknown')
        content = params.get('content', '')
        timestamp = params.get('timestamp', datetime.now().isoformat())
        
        filename = f'LINKEDIN_{activity_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        filepath = self.needs_action / filename
        
        md_content = f'''---
type: linkedin
activity: {activity_type}
timestamp: {timestamp}
status: pending
---

# LinkedIn Activity

**Type:** {activity_type}
**Time:** {timestamp}

## Content

{content}

## Actions

- [ ] Review activity
- [ ] Respond if needed
- [ ] Mark as done
'''
        
        filepath.write_text(md_content, encoding='utf-8')
        
        return {
            'success': True,
            'file': str(filepath),
            'filename': filename
        }


def main():
    """Main entry point"""
    print("=" * 60)
    print("💼 LinkedIn MCP Server")
    print("=" * 60)
    print()
    
    server = LinkedInMCPServer()
    
    print("Server running. Send JSON-RPC requests via stdin.")
    print("Example request:")
    print('{"method": "linkedin/post", "params": {"text": "Hello LinkedIn!"}, "id": 1}')
    print()
    print("Prerequisites:")
    print("1. Run: python watchers/linkedin_login.py (to login)")
    print("2. Ensure session is saved in linkedin-session/")
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
