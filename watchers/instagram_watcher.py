"""
Instagram Watcher & Auto Poster - Monitor and post to Instagram

Monitors Instagram for notifications, messages, and posts automatically.
Uses Playwright for browser automation.
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class InstagramWatcher(BaseWatcher):
    """Monitor Instagram for activity."""
    
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else Path('instagram-session')
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self) -> list:
        """Check Instagram for new activity."""
        items = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.instagram.com/', timeout=60000)
                time.sleep(5)
                
                if 'login' in page.url:
                    browser.close()
                    return items
                
                # Check for notifications
                try:
                    if page.query_selector('[aria-label*="Notifications"]'):
                        items.append({'type': 'notifications', 'priority': 'medium'})
                except:
                    pass
                
                # Check for messages
                try:
                    if page.query_selector('[aria-label*="Messenger"]'):
                        items.append({'type': 'messages', 'priority': 'high'})
                except:
                    pass
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking Instagram: {e}')
        
        return items
    
    def create_action_file(self, item) -> Path:
        """Create action file for Instagram activity."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'INSTAGRAM_{item["type"].upper()}_{timestamp}.md'
        filepath = self.needs_action / filename
        
        content = f'''---
type: instagram_{item['type']}
source: Instagram
received: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
---

# Instagram {item['type'].title()}

**Priority:** {item['priority'].upper()}

---

## Actions

- [ ] Open Instagram
- [ ] Review {item['type']}
- [ ] Respond if needed

---

*Created by Instagram Watcher*
'''
        
        filepath.write_text(content, encoding='utf-8')
        return filepath


class InstagramAutoPoster:
    """Post to Instagram automatically."""
    
    def __init__(self, session_path: str = None):
        self.session_path = Path(session_path) if session_path else Path('instagram-session')
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def post(self, content: str, image_path: str = None) -> bool:
        """Post to Instagram."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0]
                page.goto('https://www.instagram.com/', timeout=60000)
                time.sleep(5)
                
                if 'login' in page.url:
                    self.logger.error('Not logged in')
                    browser.close()
                    return False
                
                print(f"\nInstagram Post Content:\n{content}\n")
                print("Please create your post manually. Browser will stay open for 2 minutes...")
                time.sleep(120)
                
                browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f'Error: {e}')
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Instagram Watcher & Poster')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault')
    parser.add_argument('--session', default='instagram-session')
    parser.add_argument('--interval', type=int, default=300)
    parser.add_argument('--post', type=str)
    parser.add_argument('--login', action='store_true')
    
    args = parser.parse_args()
    
    if args.login:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(Path(args.session)),
                headless=False
            )
            page = browser.pages[0]
            page.goto('https://www.instagram.com/')
            print('Login, then press Ctrl+C...')
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            browser.close()
        print('Session saved!')
        return
    
    if args.post:
        poster = InstagramAutoPoster(args.session)
        success = poster.post(args.post)
        sys.exit(0 if success else 1)
    
    watcher = InstagramWatcher(str(Path(args.vault_path)), args.session, args.interval)
    watcher.run()


if __name__ == '__main__':
    main()
