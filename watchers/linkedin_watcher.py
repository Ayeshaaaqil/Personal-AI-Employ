"""
LinkedIn Watcher - Monitors LinkedIn for notifications and messages.

This watcher uses Playwright to monitor LinkedIn Web for:
- New connection requests
- Messages
- Comments on posts
- Job opportunities

Prerequisites:
1. playwright installed: pip install playwright
2. Chromium installed: playwright install chromium
3. LinkedIn account credentials
"""

import time
import logging
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInWatcher(BaseWatcher):
    """
    LinkedIn watcher using Playwright browser automation.
    
    Monitors LinkedIn for new notifications, messages, and engagement
    that may require action.
    """
    
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session (default: ./linkedin-session)
            check_interval: Seconds between checks (default: 300 - 5 minutes)
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else Path('linkedin-session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords that indicate business opportunities
        self.business_keywords = [
            'interested', 'proposal', 'project', 'opportunity',
            'hiring', 'freelance', 'contract', 'consulting',
            'budget', 'rate', 'pricing', 'quote', 'invoice'
        ]
        
        # Track processed notifications
        self.processed_notifications = set()
    
    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new notifications and messages.
        
        Returns:
            list: List of new items requiring action
        """
        items = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                try:
                    page.goto('https://www.linkedin.com/feed/', timeout=60000)
                    
                    # Wait for feed to load
                    try:
                        page.wait_for_selector('[data-id="feed"]', timeout=10000)
                    except PlaywrightTimeout:
                        # May need to login
                        self.logger.info('May need to login to LinkedIn')
                        items.append({
                            'type': 'login_required',
                            'message': 'Please login to LinkedIn manually',
                            'timestamp': datetime.now()
                        })
                        browser.close()
                        return items
                    
                    # Check for notifications
                    notifications = self._check_notifications(page)
                    items.extend(notifications)
                    
                    # Check for messages
                    messages = self._check_messages(page)
                    items.extend(messages)
                    
                    # Check for connection requests
                    connections = self._check_connections(page)
                    items.extend(connections)
                    
                except Exception as e:
                    self.logger.error(f'Error navigating LinkedIn: {e}')
                    items.append({
                        'type': 'error',
                        'message': f'LinkedIn navigation error: {str(e)}',
                        'timestamp': datetime.now()
                    })
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error in LinkedIn watcher: {e}')
        
        return items
    
    def _check_notifications(self, page) -> list:
        """Check for new notifications."""
        notifications = []
        
        try:
            # Click on notifications bell
            notification_btn = page.query_selector('a[data-id="tb_notifications"]')
            if notification_btn:
                # Get notification count
                badge = notification_btn.query_selector('.notification-badge')
                if badge:
                    count_text = badge.inner_text().strip()
                    try:
                        count = int(count_text)
                        if count > 0:
                            self.logger.info(f'Found {count} new notifications')
                            notifications.append({
                                'type': 'notifications',
                                'count': count,
                                'message': f'{count} new LinkedIn notifications',
                                'priority': 'medium',
                                'timestamp': datetime.now()
                            })
                    except ValueError:
                        pass
        except Exception as e:
            self.logger.debug(f'Could not check notifications: {e}')
        
        return notifications
    
    def _check_messages(self, page) -> list:
        """Check for new messages."""
        messages = []
        
        try:
            # Click on messaging icon
            messaging_btn = page.query_selector('a[data-id="tb_messaging"]')
            if messaging_btn:
                # Get message count
                badge = messaging_btn.query_selector('.notification-badge')
                if badge:
                    count_text = badge.inner_text().strip()
                    try:
                        count = int(count_text)
                        if count > 0:
                            self.logger.info(f'Found {count} new messages')
                            messages.append({
                                'type': 'messages',
                                'count': count,
                                'message': f'{count} new LinkedIn messages',
                                'priority': 'high',
                                'timestamp': datetime.now()
                            })
                    except ValueError:
                        pass
        except Exception as e:
            self.logger.debug(f'Could not check messages: {e}')
        
        return messages
    
    def _check_connections(self, page) -> list:
        """Check for new connection requests."""
        connections = []
        
        try:
            # Click on network icon
            network_btn = page.query_selector('a[data-id="tb_network"]')
            if network_btn:
                # Get connection request count
                badge = network_btn.query_selector('.notification-badge')
                if badge:
                    count_text = badge.inner_text().strip()
                    try:
                        count = int(count_text)
                        if count > 0:
                            self.logger.info(f'Found {count} new connection requests')
                            connections.append({
                                'type': 'connections',
                                'count': count,
                                'message': f'{count} new LinkedIn connection requests',
                                'priority': 'medium',
                                'timestamp': datetime.now()
                            })
                    except ValueError:
                        pass
        except Exception as e:
            self.logger.debug(f'Could not check connections: {e}')
        
        return connections
    
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file for the LinkedIn item.
        
        Args:
            item: LinkedIn notification/message item
            
        Returns:
            Path: Path to the created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        filename = f'LINKEDIN_{item_type.upper()}_{timestamp}.md'
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin_{item_type}
source: LinkedIn
received: {datetime.now().isoformat()}
priority: {item.get('priority', 'medium')}
status: pending
count: {item.get('count', 1)}
---

# LinkedIn {item_type.title()}

**Source:** LinkedIn
**Received:** {item.get('timestamp', datetime.now()).isoformat()}
**Priority:** {item.get('priority', 'medium').upper()}
**Count:** {item.get('count', 1)}

---

## Summary

{item.get('message', 'New LinkedIn activity detected')}

---

## Suggested Actions

'''
        
        # Add type-specific actions
        if item_type == 'messages':
            content += '''- [ ] Open LinkedIn Messaging
- [ ] Read new messages
- [ ] Draft and send response
- [ ] Mark as processed
'''
        elif item_type == 'connections':
            content += '''- [ ] Open LinkedIn Network tab
- [ ] Review connection requests
- [ ] Accept relevant connections
- [ ] Send welcome message to new connections
'''
        elif item_type == 'notifications':
            content += '''- [ ] Open LinkedIn Notifications
- [ ] Review notifications
- [ ] Respond to comments/mentions
- [ ] Mark as processed
'''
        else:
            content += '''- [ ] Review LinkedIn activity
- [ ] Take necessary action
- [ ] Mark as processed
'''
        
        # Add business opportunity detection
        if any(kw in item.get('message', '').lower() for kw in self.business_keywords):
            content += '''
## 🎯 Business Opportunity Detected

This notification may contain business-related keywords.
Consider prioritizing this item for potential leads.
'''
        
        content += f'''
---

## Quick Actions

### Send Connection Message Template

Hi [Name],

Thank you for connecting! I'm always interested in discussing new opportunities
and collaborations. Feel free to reach out if there's anything I can help with.

Best regards,
[Your Name]

### Respond to Message Template

Hi [Name],

Thanks for your message! I'd be happy to discuss this further.

[Your response]

Looking forward to hearing from you.

Best regards,
[Your Name]

---

*Created by LinkedIn Watcher at {datetime.now().isoformat()}*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filename}')
        return filepath
    
    def login_required(self) -> bool:
        """Check if LinkedIn login is required."""
        # Check if Default folder exists (contains session data)
        default_folder = self.session_path / 'Default'
        if not default_folder.exists():
            return True
        
        # Check for cookies file (indicates logged in session)
        cookies_file = default_folder / 'Cookies'
        if not cookies_file.exists():
            return True
        
        # Session exists
        return False


def main():
    """Main entry point for LinkedIn Watcher."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--session', default='linkedin-session',
                       help='Path to store browser session')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds')
    parser.add_argument('--login', action='store_true',
                       help='Open browser for manual login')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    if args.login:
        # Open browser for manual login
        print('Opening LinkedIn for login...')
        print('')
        print('IMPORTANT INSTRUCTIONS:')
        print('1. Login to your LinkedIn account')
        print('2. CHECK "Stay signed in" option')
        print('3. Wait for your LinkedIn FEED to load completely')
        print('4. You should see your home page with posts')
        print('5. THEN press Enter in this terminal')
        print('')

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(Path(args.session)),
                headless=False
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to login page first (loads faster)
            print('Opening LinkedIn login page...')
            page.goto('https://www.linkedin.com/login', timeout=30000)
            
            print('')
            print('Login page loaded!')
            print('Please login and CHECK "Stay signed in"')
            print('Wait for your FEED to load (you will see posts)')
            print('Then press Enter in this terminal...')
            print('')
            
            # Wait for user to press Enter
            try:
                input()
            except KeyboardInterrupt:
                pass

            # Close browser
            try:
                browser.close()
            except:
                pass
        
        # Verify session was saved
        cookies_file = Path(args.session) / 'Default' / 'Cookies'
        if cookies_file.exists():
            print('')
            print('Login session saved successfully!')
            print('You can now run: python linkedin_auto_post.py --post "Your post"')
        else:
            print('')
            print('Warning: Session may not have been saved.')
            print('Make sure you checked "Stay signed in" on LinkedIn.')
            print('Try logging in again if the auto poster fails.')
        return
    
    # Run watcher
    try:
        watcher = LinkedInWatcher(str(vault_path), args.session, args.interval)
        
        if watcher.login_required():
            print('LinkedIn login required. Run with --login flag first.')
            sys.exit(1)
        
        watcher.run()
    except Exception as e:
        print(f'Error starting LinkedIn Watcher: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
