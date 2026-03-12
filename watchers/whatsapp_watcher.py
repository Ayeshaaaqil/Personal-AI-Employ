"""
WhatsApp Watcher for AI Employee - Silver Tier

Monitors WhatsApp Web for new messages and creates action files in Needs_Action folder.
Uses Playwright for browser automation.

Features:
- Monitor WhatsApp Web for unread messages
- Filter messages by keywords (urgent, invoice, payment, etc.)
- Create markdown action files in Needs_Action folder
- Session persistence for faster reconnection
- Human-in-the-loop for sensitive messages

Usage:
    python whatsapp_watcher.py AI_Employee_Vault
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Web Watcher
    
    Monitors WhatsApp Web for new messages and creates action files
    """
    
    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 30,
        keywords: Optional[List[str]] = None
    ):
        super().__init__(vault_path, check_interval)
        
        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path / "whatsapp-session"
        
        self.session_path.mkdir(exist_ok=True)
        
        # Keywords to filter important messages
        self.keywords = keywords or [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'money', 'bill', 'due', 'reminder', 'important',
            'meeting', 'call', 'deadline', 'tomorrow', 'today'
        ]
        
        # Track processed message IDs to avoid duplicates
        self.processed_messages = set()
        
        # WhatsApp Web selectors (may need updates as WA Web changes)
        self.selectors = {
            'chat_list': '[data-testid="chat-list"]',
            'chat': 'div[role="row"]',
            'unread_badge': '[aria-label*="unread"]',
            'message': 'div[role="row"]',
            'contact_name': 'span[dir="auto"]',
            'message_text': 'span[dir="auto"]',
            'search_box': '[data-testid="search"]'
        }
        
        logger.info(f"WhatsApp Watcher initialized (vault: {vault_path})")
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check WhatsApp Web for new unread messages
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                # Check if WhatsApp Web is already loaded
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    # Navigate to WhatsApp Web
                    page.goto('https://web.whatsapp.com', timeout=60000)
                    
                    # Wait for chat list to load (with timeout)
                    try:
                        page.wait_for_selector(self.selectors['chat_list'], timeout=30000)
                        logger.info("WhatsApp Web loaded successfully")
                    except PlaywrightTimeout:
                        logger.warning("WhatsApp Web timeout - QR code may need scanning")
                        browser.close()
                        return messages
                    
                    # Small delay for content to load
                    time.sleep(3)
                    
                    # Find all chats with unread messages
                    unread_chats = page.query_selector_all(self.selectors['unread_badge'])
                    
                    logger.info(f"Found {len(unread_chats)} unread chats")
                    
                    for chat in unread_chats:
                        try:
                            # Extract chat information
                            chat_data = self._extract_chat_data(page, chat)
                            
                            if chat_data and chat_data.get('id') not in self.processed_messages:
                                # Check if message contains important keywords
                                if self._is_important(chat_data.get('text', '')):
                                    messages.append(chat_data)
                                    self.processed_messages.add(chat_data['id'])
                                    logger.info(f"Important message from: {chat_data.get('contact', 'Unknown')}")
                            
                        except Exception as e:
                            logger.error(f"Error extracting chat: {e}")
                            continue
                    
                    browser.close()
                    
                except Exception as e:
                    logger.error(f"Error loading WhatsApp Web: {e}")
                    browser.close()
                    return messages
                    
        except Exception as e:
            logger.error(f"Playwright error: {e}")
        
        return messages
    
    def _extract_chat_data(self, page, chat_element) -> Optional[Dict]:
        """
        Extract chat data from a chat element
        
        Args:
            page: Playwright page object
            chat_element: Chat element selector
            
        Returns:
            Dictionary with chat information
        """
        try:
            # Get contact name
            contact_elem = chat_element.query_selector(self.selectors['contact_name'])
            contact = contact_elem.inner_text() if contact_elem else "Unknown"
            
            # Get message preview text
            message_elem = chat_element.query_selector(self.selectors['message_text'])
            message_text = message_elem.inner_text() if message_elem else ""
            
            # Generate unique ID
            message_id = f"wa_{contact}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                'id': message_id,
                'contact': contact,
                'text': message_text,
                'timestamp': datetime.now().isoformat(),
                'platform': 'whatsapp',
                'raw_element': chat_element
            }
            
        except Exception as e:
            logger.error(f"Error extracting chat data: {e}")
            return None
    
    def _is_important(self, message_text: str) -> bool:
        """
        Check if message contains important keywords
        
        Args:
            message_text: Message text to check
            
        Returns:
            True if important, False otherwise
        """
        text_lower = message_text.lower()
        return any(keyword in text_lower for keyword in self.keywords)
    
    def create_action_file(self, message: Dict) -> Path:
        """
        Create markdown action file in Needs_Action folder
        
        Args:
            message: Message dictionary
            
        Returns:
            Path to created file
        """
        content = f"""---
type: whatsapp_message
from: {message.get('contact', 'Unknown')}
received: {message.get('timestamp', datetime.now().isoformat())}
platform: WhatsApp
priority: high
status: pending
keywords: {', '.join([k for k in self.keywords if k in message.get('text', '').lower()])}
---

# WhatsApp Message

**From:** {message.get('contact', 'Unknown')}
**Received:** {message.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
**Platform:** WhatsApp Web

---

## Message Content

{message.get('text', 'No content available')}

---

## Suggested Actions

- [ ] Read and understand the message
- [ ] Determine if response is needed
- [ ] Draft response if required
- [ ] Move to Done folder after processing

---

## Notes

*This message was flagged as important based on keywords.*
*Review and respond appropriately.*

---

*Generated by AI Employee WhatsApp Watcher*
"""
        
        # Create filename
        contact_safe = message.get('contact', 'Unknown').replace(' ', '_')[:30]
        filename = f"WHATSAPP_{contact_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.needs_action / filename
        
        # Write file
        filepath.write_text(content)
        logger.info(f"Created action file: {filepath}")
        
        return filepath
    
    def run(self):
        """
        Run the WhatsApp watcher continuously
        """
        logger.info(f"Starting WhatsApp Watcher (checking every {self.check_interval}s)")
        
        try:
            while True:
                try:
                    # Check for new messages
                    messages = self.check_for_updates()
                    
                    # Create action files for new messages
                    for message in messages:
                        self.create_action_file(message)
                    
                    if messages:
                        logger.info(f"Processed {len(messages)} new messages")
                    
                except Exception as e:
                    logger.error(f"Error in watcher loop: {e}")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("WhatsApp Watcher stopped by user")
        except Exception as e:
            logger.error(f"Watcher crashed: {e}")
            raise


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WhatsApp Watcher")
    parser.add_argument("vault", type=str, help="Path to vault")
    parser.add_argument("--session", type=str, help="Session path")
    parser.add_argument("--interval", type=int, default=30, help="Check interval (seconds)")
    parser.add_argument("--keywords", type=str, nargs='+', help="Keywords to filter")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval,
        keywords=args.keywords
    )
    
    # Run watcher
    if args.debug:
        # Single check for testing
        messages = watcher.check_for_updates()
        print(f"Found {len(messages)} messages")
        for msg in messages:
            print(f"  - {msg.get('contact', 'Unknown')}: {msg.get('text', '')[:50]}")
    else:
        # Continuous monitoring
        watcher.run()
