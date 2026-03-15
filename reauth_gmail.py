"""Re-authenticate Gmail API"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

print('=== Gmail API Re-Authentication ===')
print('Opening browser for authorization...')

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=56094, open_browser=True)

# Save token
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print('✓ Token saved to token.json!')

# Test connection
from googleapiclient.discovery import build
service = build('gmail', 'v1', credentials=creds)
profile = service.users().getProfile(userId='me').execute()
print(f'✓ Logged in as: {profile["emailAddress"]}')
print('=== Authentication Complete ===')
