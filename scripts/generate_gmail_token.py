"""
Gmail Token Generator - Creates token.json from credentials.json

This script automates the OAuth2 flow to generate a token.json file
that can be used by the Gmail Watcher without interactive login.

Usage:
    python scripts/generate_gmail_token.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scopes - read and modify emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def generate_token():
    """Generate Gmail API token from credentials.json"""
    
    creds_path = Path('credentials.json')
    token_path = Path('token.json')
    
    # Check if credentials exist
    if not creds_path.exists():
        print(f'❌ Error: credentials.json not found at {creds_path}')
        print('Please ensure credentials.json is in the project root.')
        return False
    
    print('[OK] Found credentials.json')
    print(f'  Project ID: {load_project_id(creds_path)}')
    
    # Check for existing token
    if token_path.exists():
        print(f'\n⚠ token.json already exists at {token_path}')
        response = input('Do you want to regenerate it? (y/n): ')
        if response.lower() != 'y':
            print('Keeping existing token.')
            return True
        token_path.unlink()
        print('Deleted old token.json')
    
    print('\n' + '='*60)
    print('GMAIL API AUTHENTICATION')
    print('='*60)
    print('\nThis will open a browser window for you to:')
    print('1. Login to your Google account')
    print('2. Grant Gmail API permissions')
    print('3. Save the authentication token')
    print('\nNOTE: The browser will open automatically.')
    print('      Complete the login, then the token will be saved.')
    print('\n' + '='*60)
    
    # Try to get input, but don't fail if not interactive
    try:
        input('\nPress Enter to open the browser...')
    except EOFError:
        print('\nNon-interactive mode detected. Opening browser automatically...')
    
    try:
        # Create flow and run local server
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_path,
            SCOPES
        )
        
        # This opens browser on localhost:8080
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            host='localhost'
        )
        
        # Save token
        token_path.write_text(creds.to_json())
        
        print('\n' + '='*60)
        print('SUCCESS!')
        print('='*60)
        print(f'\nToken saved to: {token_path.absolute()}')
        print('\nYou can now run the Gmail Watcher:')
        print('  cd watchers')
        print('  python gmail_watcher.py ../AI_Employee_Vault')
        print('\nThe token is valid for 1 hour and will auto-refresh.')
        print('='*60)
        
        return True
        
    except Exception as e:
        print(f'\nError during authentication: {e}')
        print('\nTroubleshooting:')
        print('1. Make sure credentials.json is valid')
        print('2. Check that Gmail API is enabled in Google Cloud Console')
        print('3. Try again with: python scripts/generate_gmail_token.py')
        return False


def load_project_id(creds_path: Path) -> str:
    """Load project ID from credentials file"""
    try:
        import json
        creds = json.loads(creds_path.read_text())
        return creds.get('installed', {}).get('project_id', 'Unknown')
    except:
        return 'Unknown'


def verify_token():
    """Verify that token.json is valid"""
    token_path = Path('token.json')
    
    if not token_path.exists():
        print('Error: token.json not found')
        return False
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Check if token is valid or can be refreshed
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print('Warning: Token expired but can be refreshed')
                creds.refresh(Request())
                token_path.write_text(creds.to_json())
                print('Token refreshed successfully')
                return True
            else:
                print('Error: Token is invalid and cannot be refreshed')
                return False
        
        print('Token is valid')
        print(f'  Expires: {creds.expiry}')
        return True
        
    except Exception as e:
        print(f'Error: Token verification failed: {e}')
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Gmail API token from credentials.json'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify existing token instead of generating new one'
    )
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_token()
    else:
        success = generate_token()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
