"""
WhatsApp MCP Server for AI Employee - Silver Tier

Sends WhatsApp messages via WhatsApp Web automation.
Use this MCP server to send messages through the AI Employee system.

Features:
- Send WhatsApp messages via Web
- Session persistence for faster sending
- Support for text messages
- Human-in-the-loop approval workflow

Usage:
    python whatsapp_mcp_server.py
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppMCPServer:
    """
    WhatsApp MCP Server
    
    Provides MCP (Model Context Protocol) interface for sending WhatsApp messages
    """
    
    def __init__(self, session_path: Optional[str] = None):
        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path.home() / ".whatsapp-session"
        
        self.session_path.mkdir(exist_ok=True)
        
        logger.info(f"WhatsApp MCP Server initialized (session: {self.session_path})")
    
    def send_message(self, contact: str, message: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a contact
        
        Args:
            contact: Contact name or phone number
            message: Message text to send
            
        Returns:
            Result dictionary with status and details
        """
        result = {
            "success": False,
            "contact": contact,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Show browser for QR code scanning if needed
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    # Navigate to WhatsApp Web
                    logger.info("Loading WhatsApp Web...")
                    page.goto('https://web.whatsapp.com', timeout=60000)
                    
                    # Wait for chat list to load
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                        logger.info("WhatsApp Web loaded successfully")
                    except PlaywrightTimeout:
                        logger.warning("QR code scan required. Please scan QR code.")
                        # Wait for user to scan QR code
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                    
                    # Small delay for content to load
                    time.sleep(3)
                    
                    # Search for contact
                    logger.info(f"Searching for contact: {contact}")
                    search_box = page.query_selector('[data-testid="search"]')
                    
                    if search_box:
                        search_box.click()
                        time.sleep(1)
                        
                        # Clear search box and type contact name
                        from playwright.sync_api import Keyboard
                        # Select all and delete
                        page.keyboard.press('Control+A')
                        page.keyboard.press('Backspace')
                        
                        # Type contact name
                        page.keyboard.type(contact)
                        time.sleep(2)
                        
                        # Click on first result
                        first_chat = page.query_selector('div[role="row"]')
                        if first_chat:
                            first_chat.click()
                            time.sleep(2)
                            
                            # Find message input box
                            message_box = page.query_selector('[data-testid="draft-message"]')
                            
                            if message_box:
                                message_box.click()
                                time.sleep(1)
                                
                                # Type message
                                page.keyboard.type(message)
                                time.sleep(1)
                                
                                # Press Enter to send
                                page.keyboard.press('Enter')
                                time.sleep(2)
                                
                                logger.info(f"Message sent to {contact}")
                                
                                result["success"] = True
                                result["sent_at"] = datetime.now().isoformat()
                                
                            else:
                                result["error"] = "Message input box not found"
                                logger.error("Message input box not found")
                        else:
                            result["error"] = f"Contact not found: {contact}"
                            logger.error(f"Contact not found: {contact}")
                    else:
                        result["error"] = "Search box not found"
                        logger.error("Search box not found")
                    
                    browser.close()
                    
                except Exception as e:
                    logger.error(f"Error during message sending: {e}")
                    result["error"] = str(e)
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Playwright error: {e}")
            result["error"] = str(e)
        
        return result
    
    def send_message_to_number(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a phone number
        
        Args:
            phone_number: Phone number with country code (e.g., +923001234567)
            message: Message text to send
            
        Returns:
            Result dictionary with status and details
        """
        result = {
            "success": False,
            "phone_number": phone_number,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        try:
            # Clean phone number (remove +, -, spaces)
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Use WhatsApp click-to-chat link
            wa_url = f"https://web.whatsapp.com/send?phone={clean_number}"
            
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                try:
                    # Navigate to WhatsApp Web with phone number
                    logger.info(f"Opening chat with number: {phone_number}")
                    page.goto(wa_url, timeout=60000)
                    
                    # Wait for page to load
                    time.sleep(5)
                    
                    # Check if we need to handle "no chat exists" dialog
                    try:
                        # Look for message input box
                        message_box = page.wait_for_selector('[data-testid="draft-message"]', timeout=10000)
                        
                        if message_box:
                            message_box.click()
                            time.sleep(1)
                            
                            # Type message
                            page.keyboard.type(message)
                            time.sleep(1)
                            
                            # Press Enter to send
                            page.keyboard.press('Enter')
                            time.sleep(2)
                            
                            logger.info(f"Message sent to {phone_number}")
                            
                            result["success"] = True
                            result["sent_at"] = datetime.now().isoformat()
                        
                    except PlaywrightTimeout:
                        result["error"] = "Could not find message input. Number may not have WhatsApp."
                        logger.error("Message input not found for number")
                    
                    browser.close()
                    
                except Exception as e:
                    logger.error(f"Error during message sending: {e}")
                    result["error"] = str(e)
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Playwright error: {e}")
            result["error"] = str(e)
        
        return result
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test WhatsApp Web connection

        Returns:
            Connection status dictionary
        """
        result = {
            "connected": False,
            "session_exists": self.session_path.exists(),
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

        try:
            with sync_playwright() as p:
                # Launch browser with visible window for QR code scanning
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Show browser window
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ],
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    logger.info("Loading WhatsApp Web...")
                    # Navigate with networkidle wait
                    page.goto('https://web.whatsapp.com', timeout=120000, wait_until='networkidle')
                    
                    # Wait a bit for page to fully load
                    time.sleep(3)

                    # Check if chat list loads (logged in)
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                        result["connected"] = True
                        result["error"] = None
                        logger.info("WhatsApp Web connection test successful - Logged in!")
                    except PlaywrightTimeout:
                        # Check if QR code is displayed
                        qr_detected = page.query_selector('[data-testid="qr-image"]')
                        if qr_detected:
                            result["connected"] = False
                            result["error"] = "QR code detected. Please scan QR code with WhatsApp mobile app."
                            logger.warning("QR code scan required. Keep browser window open and scan QR code.")
                            logger.info("After scanning, close browser and run test again.")
                            
                            # Keep browser open for 2 minutes for QR scan
                            try:
                                logger.info("Waiting for QR code scan (120 seconds)...")
                                page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                                result["connected"] = True
                                result["error"] = None
                                logger.info("QR code scanned successfully!")
                            except PlaywrightTimeout:
                                logger.warning("QR code not scanned within timeout")
                        else:
                            result["connected"] = False
                            result["error"] = "WhatsApp Web loading issue. Check internet connection."
                            logger.warning("Could not detect chat list or QR code")

                    browser.close()

                except Exception as e:
                    logger.error(f"Error during connection test: {e}")
                    result["error"] = str(e)
                    if 'browser' in locals():
                        browser.close()

        except Exception as e:
            logger.error(f"Playwright error: {e}")
            result["error"] = str(e)

        return result


# MCP Server Protocol Implementation
def handle_mcp_request(request: Dict) -> Dict:
    """
    Handle MCP protocol request
    
    Args:
        request: MCP request dictionary
        
    Returns:
        MCP response dictionary
    """
    action = request.get("action")
    server = WhatsAppMCPServer()
    
    if action == "send_message":
        contact = request.get("contact")
        message = request.get("message")
        
        if not contact or not message:
            return {
                "success": False,
                "error": "contact and message are required"
            }
        
        return server.send_message(contact, message)
    
    elif action == "send_message_to_number":
        phone_number = request.get("phone_number")
        message = request.get("message")
        
        if not phone_number or not message:
            return {
                "success": False,
                "error": "phone_number and message are required"
            }
        
        return server.send_message_to_number(phone_number, message)
    
    elif action == "test_connection":
        return server.test_connection()
    
    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WhatsApp MCP Server")
    parser.add_argument("--action", type=str, help="Action to perform")
    parser.add_argument("--contact", type=str, help="Contact name")
    parser.add_argument("--phone", type=str, help="Phone number")
    parser.add_argument("--message", type=str, help="Message to send")
    parser.add_argument("--session", type=str, help="Session path")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--server", action="store_true", help="Run as MCP server")
    
    args = parser.parse_args()
    
    if args.test:
        server = WhatsAppMCPServer(session_path=args.session)
        result = server.test_connection()
        print(json.dumps(result, indent=2))
    
    elif args.action:
        request = {
            "action": args.action,
            "contact": args.contact,
            "phone_number": args.phone,
            "message": args.message
        }
        result = handle_mcp_request(request)
        print(json.dumps(result, indent=2))
    
    elif args.server:
        print("WhatsApp MCP Server running. Send requests via stdin.")
        # Simple server loop (for production, use proper MCP server framework)
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line)
                    result = handle_mcp_request(request)
                    print(json.dumps(result))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    print(json.dumps({"error": "Invalid JSON"}))
                    sys.stdout.flush()
        except KeyboardInterrupt:
            print("\nServer stopped")
    
    else:
        parser.print_help()
