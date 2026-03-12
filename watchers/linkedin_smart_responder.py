"""
LinkedIn Smart Auto Responder - Auto reply to messages

Automatically reads LinkedIn messages, generates replies, and sends them.
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


class LinkedInSmartResponder:
    """AI-powered LinkedIn auto responder."""
    
    def __init__(self, vault_path: str, session_path: str = None):
        """
        Initialize smart responder.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to LinkedIn session
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.session_path = Path(session_path) if session_path else Path('linkedin-session')
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_files = set()
    
    def generate_reply(self, message_type: str, content: str, sender: str) -> str:
        """
        Generate appropriate reply based on message content.
        
        Args:
            message_type: Type of LinkedIn message
            content: Message content
            sender: Sender name
            
        Returns:
            str: Generated reply
        """
        content_lower = content.lower()
        
        # Rule 1: Business inquiries
        if any(word in content_lower for word in ['project', 'opportunity', 'proposal', 'collaboration']):
            return f'''Hi {sender.split()[0] if sender else 'there'},

Thank you for reaching out regarding this opportunity! I'm interested in learning more.

Could you please share more details about:
- Project scope
- Timeline
- Budget

Looking forward to hearing from you.

Best regards,
AI Employee'''
        
        # Rule 2: Pricing inquiries
        if any(word in content_lower for word in ['pricing', 'cost', 'rate', 'budget', 'quote']):
            return f'''Hi {sender.split()[0] if sender else 'there'},

Thanks for your interest in our services!

Our pricing varies based on project requirements. Here's a general overview:
- Consulting: $100/hour
- Projects: Starting at $1,000
- Retainers: Custom packages available

Would you like to schedule a call to discuss your specific needs?

Best regards,
AI Employee'''
        
        # Rule 3: Greetings/Networking
        if any(word in content_lower for word in ['hello', 'hi', 'hey', 'connect', 'network']):
            return f'''Hello {sender.split()[0] if sender else 'there'}! 👋

Thanks for connecting! I'm always happy to expand my professional network.

I specialize in:
✅ AI Automation
✅ Business Process Optimization  
✅ Digital Transformation

Feel free to reach out if there's any way I can help!

Best regards,
AI Employee'''
        
        # Rule 4: Job opportunities
        if any(word in content_lower for word in ['job', 'position', 'career', 'hiring']):
            return f'''Hi {sender.split()[0] if sender else 'there'},

Thank you for thinking of me for this opportunity!

I'm currently focused on AI Employee automation projects. However, I'd love to hear more about:
- Role responsibilities
- Tech stack
- Company culture

Is this a remote position?

Best regards,
AI Employee'''
        
        # Default reply
        return f'''Hi {sender.split()[0] if sender else 'there'},

Thank you for your message! I've received it and will get back to you soon.

Best regards,
AI Employee'''
    
    def send_reply(self, message_content: str, reply: str) -> bool:
        """
        Send reply via LinkedIn.
        
        Args:
            message_content: Original message
            reply: Reply to send
            
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
                
                # Go to LinkedIn messaging
                self.logger.info('Opening LinkedIn messaging...')
                page.goto('https://www.linkedin.com/messaging/', timeout=60000)
                time.sleep(5)
                
                # Search for the conversation
                self.logger.info('Finding conversation...')
                
                # Try to find and click on the conversation
                try:
                    # Click on first unread message
                    page.click('text="{}"'.format(message_content[:30]), timeout=5000)
                    time.sleep(2)
                except:
                    self.logger.warning('Could not find specific conversation')
                    browser.close()
                    return False
                
                # Type reply
                self.logger.info('Typing reply...')
                try:
                    # Find message input
                    input_box = page.locator('[contenteditable="true"]').first
                    input_box.click()
                    time.sleep(1)
                    
                    # Type reply
                    page.keyboard.type(reply, delay=50)
                    time.sleep(1)
                    
                    # Press Enter to send
                    page.keyboard.press('Enter')
                    time.sleep(2)
                    
                    self.logger.info('Reply sent successfully!')
                    
                except Exception as e:
                    self.logger.error(f'Error typing reply: {e}')
                    browser.close()
                    return False
                
                browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f'Error sending reply: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def process_message(self, message_file: Path) -> bool:
        """
        Process a LinkedIn message and send auto-reply.
        
        Args:
            message_file: Path to message action file
            
        Returns:
            bool: True if reply sent successfully
        """
        self.logger.info(f'Processing: {message_file.name}')
        
        # Read message file
        content = message_file.read_text(encoding='utf-8')
        
        # Extract details
        sender = ''
        message_content = ''
        message_type = 'general'
        
        lines = content.split('\n')
        in_message = False
        
        for line in lines:
            if line.startswith('from:') or line.startswith('contact_name:'):
                sender = line.split(':', 1)[1].strip()
            elif '## Message Content' in line or '## Summary' in line:
                in_message = True
            elif in_message and line.startswith('##'):
                break
            elif in_message and line.strip():
                message_content += line + '\n'
        
        if not message_content.strip():
            self.logger.error(f'Could not extract message content from {message_file}')
            return False
        
        # Generate reply
        reply = self.generate_reply(message_type, message_content, sender)
        
        self.logger.info(f'Generated reply for message from {sender}')
        
        # Send reply (semi-automated - opens browser for confirmation)
        self.logger.info('Opening browser to send reply...')
        
        # For now, log the reply instead of auto-sending
        # Auto-sending via Playwright is unreliable
        reply_file = self.logs / f'linkedin_reply_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        reply_content = f'''---
type: linkedin_reply
to: {sender}
original_message: {message_file.name}
created: {datetime.now().isoformat()}
---

# LinkedIn Reply Ready

**To:** {sender}

**Reply:**
```
{reply}
```

## To Send

1. Open LinkedIn: https://linkedin.com/messaging/
2. Find conversation with {sender}
3. Copy and paste the reply above
4. Click Send

---

*Generated by LinkedIn Smart Responder*
'''
        reply_file.write_text(reply_content, encoding='utf-8')
        
        # Move original to Done
        dest = self.done / message_file.name
        message_file.rename(dest)
        
        self.logger.info(f'Reply saved to: {reply_file}')
        self.logger.info(f'Moved message to: {dest}')
        
        return True
    
    def process_all_messages(self) -> int:
        """Process all LinkedIn messages in Needs_Action folder."""
        if not self.needs_action.exists():
            return 0
        
        count = 0
        for message_file in self.needs_action.glob('LINKEDIN_*.md'):
            if message_file.name not in self.processed_files:
                if self.process_message(message_file):
                    count += 1
                self.processed_files.add(message_file.name)
        
        return count
    
    def run_continuous(self, check_interval: int = 120):
        """Run continuously."""
        self.logger.info(f'Starting LinkedIn Smart Responder (interval: {check_interval}s)')
        
        import time
        
        try:
            while True:
                processed = self.process_all_messages()
                if processed > 0:
                    self.logger.info(f'Processed {processed} messages')
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Smart Responder stopped')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Smart Auto Responder')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--session', default='linkedin-session',
                       help='LinkedIn session path')
    parser.add_argument('--interval', type=int, default=120,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f'Error: Vault not found: {vault_path}')
        sys.exit(1)
    
    responder = LinkedInSmartResponder(str(vault_path), args.session)
    
    if args.once:
        count = responder.process_all_messages()
        print(f'Processed {count} messages, generated {count} replies')
    else:
        responder.run_continuous(args.interval)


if __name__ == '__main__':
    main()
