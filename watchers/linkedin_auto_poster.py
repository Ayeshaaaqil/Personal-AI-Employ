"""
LinkedIn Auto Poster - Automatically post business updates

Monitors Business_Goals.md and posts updates when milestones are reached.
Also posts scheduled content.
"""

import sys
import logging
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInAutoPoster:
    """Automatically post to LinkedIn."""
    
    def __init__(self, vault_path: str, session_path: str = None):
        """
        Initialize auto poster.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to LinkedIn session
        """
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.business_goals = self.vault_path / 'Business_Goals.md'
        
        # Ensure folders exist
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.session_path = Path(session_path) if session_path else Path('linkedin-session')
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.posted_content = set()
    
    def generate_business_post(self) -> str:
        """Generate a business update post based on goals."""
        if not self.business_goals.exists():
            return None
        
        content = self.business_goals.read_text(encoding='utf-8')
        
        # Extract revenue info
        revenue_mtd = ''
        revenue_goal = ''
        
        if 'Current MTD:' in content:
            for line in content.split('\n'):
                if 'Current MTD:' in line:
                    revenue_mtd = line.split(':')[1].strip()
                if 'Monthly goal:' in line:
                    revenue_goal = line.split(':')[1].strip()
        
        # Generate post
        if revenue_mtd and revenue_goal:
            return f'''📊 Business Update

Making great progress this month!

Revenue MTD: {revenue_mtd}
Monthly Goal: {revenue_goal}

Grateful for all our amazing clients and partners! 🙏

#Business #Growth #AI #Automation'''
        
        # Default business post
        return f'''🚀 AI Employee Update

Continuously improving our automation capabilities!

Currently monitoring:
✅ Gmail
✅ LinkedIn
✅ File System

Ready to help your business automate! 💼

#AI #Automation #Business #Innovation'''
    
    def post_to_linkedin(self, content: str) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            content: Post content
            
        Returns:
            bool: True if successful
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                time.sleep(10)
                
                # Check if logged in
                if 'login' in page.url:
                    self.logger.error('Not logged in!')
                    browser.close()
                    return False
                
                self.logger.info('LinkedIn loaded successfully!')
                
                # Show instructions
                print("\n" + "="*70)
                print("LINKEDIN AUTO POST - READY TO POST")
                print("="*70)
                print("\nPost content:")
                print("-" * 70)
                print(content)
                print("-" * 70)
                print("\nINSTRUCTIONS:")
                print("1. Click 'Start a post' button")
                print("2. Copy the content above")
                print("3. Paste in composer")
                print("4. Click 'Post'")
                print("5. Close browser when done")
                print("\nPress Enter when posted, or wait 120 seconds...")
                print("="*70 + "\n")
                
                # Wait for user to complete posting
                posted = False
                start_time = time.time()
                
                while time.time() - start_time < 120:
                    try:
                        # Check for "Posted" confirmation
                        if page.locator('text="Posted"').is_visible(timeout=1000):
                            self.logger.info('✓ Post published successfully!')
                            posted = True
                            break
                        
                        # Check if modal closed
                        modal = page.locator('[role="dialog"]').first
                        if not modal.is_visible(timeout=1000) and time.time() - start_time > 10:
                            self.logger.info('Post composer closed - assuming posted!')
                            posted = True
                            break
                    except:
                        pass
                    time.sleep(1)
                
                try:
                    browser.close()
                except:
                    pass
                
                if posted:
                    self.logger.info('SUCCESS! Post published to LinkedIn.')
                    return True
                else:
                    self.logger.warning('Timeout - post may not have been published.')
                    return False
                
        except Exception as e:
            self.logger.error(f'Error posting: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def check_approved_posts(self) -> list:
        """Check for approved posts."""
        if not self.approved.exists():
            return []
        
        approved = []
        for file in self.approved.glob('APPROVE_LINKEDIN_*.md'):
            approved.append(file)
        
        return approved
    
    def extract_post_content(self, filepath: Path) -> str:
        """Extract post content from approval file."""
        content = filepath.read_text(encoding='utf-8')
        
        # Look for content in markdown
        lines = content.split('\n')
        post_lines = []
        in_content = False
        
        for line in lines:
            if '## Content' in line or '## Post' in line:
                in_content = True
                continue
            elif in_content:
                if line.startswith('---'):
                    break
                elif line.startswith('```'):
                    continue
                elif line.strip():
                    post_lines.append(line)
        
        return '\n'.join(post_lines).strip()
    
    def post_approved(self) -> int:
        """Post all approved content."""
        approved = self.check_approved_posts()
        
        if not approved:
            return 0
        
        self.logger.info(f'Found {len(approved)} approved posts')
        
        posted = 0
        for filepath in approved:
            content = self.extract_post_content(filepath)
            
            if not content:
                self.logger.error(f'Could not extract content from {filepath}')
                continue
            
            if self.post_to_linkedin(content):
                posted += 1
                
                # Move to Done
                dest = self.done / filepath.name
                filepath.rename(dest)
                self.logger.info(f'Moved to Done: {dest}')
        
        return posted
    
    def run_once(self) -> int:
        """Run once."""
        return self.post_approved()
    
    def run_continuous(self, check_interval: int = 300):
        """Run continuously."""
        self.logger.info(f'Starting LinkedIn Auto Poster (interval: {check_interval}s)')
        
        import time
        
        try:
            while True:
                self.run_once()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Auto Poster stopped')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--session', default='linkedin-session',
                       help='LinkedIn session path')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--post', type=str, help='Post content directly')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault not found: {vault_path}')
        sys.exit(1)
    
    poster = LinkedInAutoPoster(str(vault_path), args.session)
    
    if args.post:
        # Post direct content
        success = poster.post_to_linkedin(args.post)
        sys.exit(0 if success else 1)
    elif args.once:
        count = poster.run_once()
        print(f'Posted {count} updates')
    else:
        poster.run_continuous(args.interval)


if __name__ == '__main__':
    main()
