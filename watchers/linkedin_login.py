"""
LinkedIn Login Helper - Manual login with longer timeout

This script opens LinkedIn login in a visible browser window.
After login, the session is saved automatically.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def login_linkedin():
    """Open LinkedIn login and save session."""
    session_path = Path('linkedin-session')
    
    print('=' * 60)
    print('LinkedIn Login')
    print('=' * 60)
    print()
    print('A browser window will open in 3 seconds...')
    print()
    print('INSTRUCTIONS:')
    print('1. Login to your LinkedIn account')
    print('2. CHECK "Stay signed in" option')
    print('3. Wait for your HOME FEED to load (you should see posts)')
    print('4. Keep the browser open for 10 seconds after feed loads')
    print('5. The script will close automatically')
    print()
    
    import time
    time.sleep(3)
    
    with sync_playwright() as p:
        print('Opening browser...')
        
        # Launch browser with visible window
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
        
        # Set larger viewport
        page.set_viewport_size({'width': 1280, 'height': 800})
        
        print('Navigating to LinkedIn...')
        
        try:
            # Go to LinkedIn home (will redirect to login if not logged in)
            page.goto('https://www.linkedin.com/feed/', timeout=120000)
            
            print('')
            print('Browser is open!')
            print('Please complete login if needed...')
            print('Waiting 60 seconds for you to login and check feed...')
            print('')
            
            # Wait 60 seconds for user to login
            for i in range(60, 0, -1):
                time.sleep(1)
                if i % 10 == 0:
                    print(f'  {i} seconds remaining...')
            
            print('')
            print('Closing browser...')
            
        except Exception as e:
            print(f'Error: {e}')
            print('Please try again.')
        
        finally:
            browser.close()
    
    # Check if session was saved
    cookies_file = session_path / 'Default' / 'Cookies'
    if cookies_file.exists():
        print('')
        print('✓ LinkedIn session saved successfully!')
        print(f'  Session path: {session_path.absolute()}')
        print('')
        print('You can now run LinkedIn watcher:')
        print('  python linkedin_watcher.py ../AI_Employee_Vault')
    else:
        print('')
        print('⚠ Session may not have been saved.')
        print('  Please try again and make sure to stay logged in.')
    
    print('=' * 60)

if __name__ == '__main__':
    login_linkedin()
