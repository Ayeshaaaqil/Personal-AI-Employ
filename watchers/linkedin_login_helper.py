"""
LinkedIn Login Helper

This script helps you login to LinkedIn and save the session.
Run this once to authenticate, then the MCP server will use the saved session.

Usage:
    python linkedin_login_helper.py
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def login_to_linkedin():
    """Open LinkedIn login and save session"""
    session_path = Path('linkedin-session')
    
    print("=" * 60)
    print("💼 LinkedIn Login Helper")
    print("=" * 60)
    print()
    print("This will open a browser to login to LinkedIn.")
    print("Your session will be saved for future use.")
    print()
    print("INSTRUCTIONS:")
    print("1. A browser window will open")
    print("2. Login to LinkedIn with your credentials")
    print("3. Wait for your feed to load completely")
    print("4. You should see your LinkedIn homepage")
    print("5. Keep browser open for 10 seconds after login")
    print("6. Browser will close automatically")
    print()
    
    input("Press Enter to open browser...")
    
    with sync_playwright() as p:
        print("Launching browser...")
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,  # Visible browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({'width': 1280, 'height': 800})
        
        print("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/login', timeout=120000)
        
        print("")
        print("Login page loaded!")
        print("Please login to your LinkedIn account...")
        print("Waiting 90 seconds for you to login and see your feed...")
        print("")
        
        # Wait for user to login
        for i in range(90, 0, -1):
            time.sleep(1)
            if i % 10 == 0:
                print(f"  {i} seconds remaining...")
        
        print("")
        print("Closing browser...")
        browser.close()
    
    # Check if session was saved
    cookies_file = session_path / 'Default' / 'Cookies'
    if cookies_file.exists():
        print("")
        print("✅ LinkedIn session saved successfully!")
        print(f"   Session path: {session_path.absolute()}")
        print("")
        print("You can now use LinkedIn MCP server:")
        print("  python mcp-servers/linkedin_mcp_server.py")
    else:
        print("")
        print("⚠️  Session may not have been saved properly.")
        print("   Please try again and make sure to:")
        print("   1. Login successfully")
        print("   2. Wait for your feed to load")
        print("   3. Stay logged in for at least 10 seconds")
    
    print("=" * 60)


if __name__ == '__main__':
    login_to_linkedin()
