"""
Gmail Authentication Script - One-time setup

Run this script to authenticate Gmail API and generate token.json
"""

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def authenticate_gmail():
    """Authenticate Gmail API and save token."""
    creds = None
    
    # Check for existing token
    token_paths = ['token.json', 'watchers/token.json', Path.home() / 'token.json']
    
    for token_path in token_paths:
        token_file = Path(token_path)
        if token_file.exists():
            print(f'Found existing token at: {token_file}')
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            break
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('Refreshing expired token...')
            try:
                creds.refresh(Request())
                print('Token refreshed successfully!')
            except Exception as e:
                print(f'Token refresh failed: {e}')
                creds = None
        
        if not creds:
            print('\n=== Gmail API Authentication ===')
            print('Looking for credentials.json...')
            
            # Find credentials.json
            cred_paths = ['credentials.json', 'watchers/credentials.json']
            cred_file = None
            
            for path in cred_paths:
                if Path(path).exists():
                    cred_file = Path(path)
                    print(f'Found credentials.json at: {cred_file}')
                    break
            
            if not cred_file:
                print('ERROR: credentials.json not found!')
                print('Please create credentials.json in the project root.')
                return None
            
            print('\nStarting OAuth flow...')
            print('A browser window should open automatically.')
            print('If not, copy and paste the URL from the next line into your browser:\n')
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(cred_file), SCOPES)
                
                # Run local server for OAuth
                creds = flow.run_local_server(
                    port=56094,
                    open_browser=True,
                    authorization_prompt_message='Opening browser... Please authorize in the browser window.\nURL: {url}'
                )
                
                print('\n✓ Authorization successful!')
                
            except Exception as e:
                print(f'\n✗ Authorization error: {e}')
                print('\nManual authorization steps:')
                print('1. Run: python -m google_auth_oauthlib.flow from_client_secrets credentials.json "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.send"')
                return None
    
    # Save the credentials for the next run
    token_save_path = Path('token.json')
    
    with open(token_save_path, 'w') as token:
        token.write(creds.to_json())
    
    print(f'\n✓ Token saved to: {token_save_path.absolute()}')
    
    # Test the credentials
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f'\n✓ Gmail API connection successful!')
        print(f'  Logged in as: {profile["emailAddress"]}')
        return creds
    except Exception as e:
        print(f'\n✗ Gmail API test failed: {e}')
        return None


if __name__ == '__main__':
    from googleapiclient.discovery import build
    
    print('=' * 60)
    print('Gmail API Authentication')
    print('=' * 60)
    print()
    
    creds = authenticate_gmail()
    
    if creds:
        print('\n' + '=' * 60)
        print('SUCCESS! Gmail API is ready to use.')
        print('=' * 60)
        print('\nYou can now run:')
        print('  python gmail_watcher.py ../AI_Employee_Vault')
        print('  python gmail_smart_responder.py ../AI_Employee_Vault')
    else:
        print('\n' + '=' * 60)
        print('Authentication failed. Please try again.')
        print('=' * 60)
        sys.exit(1)
