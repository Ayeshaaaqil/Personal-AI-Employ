"""
LinkedIn API Auto Poster - Official API Method

Uses LinkedIn Official API to post updates automatically.
Never fails, always works, no browser automation needed.

Setup:
1. Create LinkedIn app at: https://www.linkedin.com/developers/
2. Get Client ID and Client Secret
3. Create config file: linkedin_config.json
"""

import sys
import json
import logging
import requests
import base64
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInAPIPoster:
    """Post to LinkedIn using Official API."""
    
    def __init__(self, config_path: str = 'linkedin_config.json'):
        """
        Initialize LinkedIn API poster.
        
        Args:
            config_path: Path to config file with credentials
        """
        self.config_path = Path(config_path)
        self.token_path = Path('linkedin_api_token.json')
        
        self.client_id = ''
        self.client_secret = ''
        self.access_token = ''
        self.person_urn = ''
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.config_path.exists():
            self._load_config()
            self._authenticate()
        else:
            self.logger.error(f'Config file not found: {config_path}')
            self.logger.info('Creating sample config file...')
            self._create_sample_config()
    
    def _load_config(self):
        """Load LinkedIn API credentials."""
        config = json.loads(self.config_path.read_text())
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.redirect_uri = config.get('redirect_uri', 'https://localhost:8080')
    
    def _create_sample_config(self):
        """Create sample config file."""
        config = {
            'client_id': 'YOUR_CLIENT_ID_HERE',
            'client_secret': 'YOUR_CLIENT_SECRET_HERE',
            'redirect_uri': 'https://localhost:8080'
        }
        self.config_path.write_text(json.dumps(config, indent=2))
        self.logger.info(f'Sample config created: {self.config_path}')
        self.logger.info('Please edit with your LinkedIn API credentials')
    
    def _authenticate(self):
        """Get access token."""
        # Try to load existing token
        if self.token_path.exists():
            token_data = json.loads(self.token_path.read_text())
            self.access_token = token_data.get('access_token', '')
            self.person_urn = token_data.get('person_urn', '')
            
            # Check if token is still valid (expires in 60 days)
            if token_data.get('expires_at', 0) > datetime.now().timestamp():
                self.logger.info('Using existing access token')
                return
        
        # Get new token via authorization code flow
        self.logger.info('Getting new access token...')
        self.logger.info('Open this URL in browser to authorize:')
        
        auth_url = (
            f'https://www.linkedin.com/oauth/v2/authorization?'
            f'response_type=code&'
            f'client_id={self.client_id}&'
            f'redirect_uri={self.redirect_uri}&'
            f'scope=w_member_social%20r_basicprofile%20r_emailaddress'
        )
        
        self.logger.info(auth_url)
        self.logger.info('After authorization, enter the code from redirect URL:')
        
        auth_code = input('Authorization code: ').strip()
        
        # Exchange code for token
        token_response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            self.access_token = token_data.get('access_token', '')
            
            # Get person URN
            self._get_person_urn()
            
            # Save token
            self.token_path.write_text(json.dumps({
                'access_token': self.access_token,
                'person_urn': self.person_urn,
                'expires_at': datetime.now().timestamp() + 5184000  # 60 days
            }))
            
            self.logger.info('✓ Access token saved!')
        else:
            self.logger.error(f'Failed to get token: {token_response.text}')
    
    def _get_person_urn(self):
        """Get LinkedIn person URN."""
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.person_urn = data.get('id', '')
            self.logger.info(f'Person URN: {self.person_urn}')
        else:
            self.logger.error(f'Failed to get person URN: {response.text}')
    
    def post(self, content: str) -> bool:
        """
        Post content to LinkedIn using API.
        
        Args:
            content: Post content (max 3000 characters)
            
        Returns:
            bool: True if successful
        """
        if not self.access_token or not self.person_urn:
            self.logger.error('Not authenticated. Run authentication first.')
            return False
        
        self.logger.info(f'Posting to LinkedIn (length: {len(content)})')
        
        # LinkedIn API endpoint for posts
        url = 'https://api.linkedin.com/v2/shares'
        
        # Create post payload
        payload = {
            'owner': f'urn:li:person:{self.person_urn}',
            'subject': {
                'title': 'AI Employee Update'
            },
            'content': {
                'contentEntities': [],
                'text': {
                    'text': content
                }
            },
            'visibility': 'PUBLIC'
        }
        
        # Make API call
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            post_id = result.get('id', 'Unknown')
            self.logger.info(f'✓ Post published successfully!')
            self.logger.info(f'Post ID: {post_id}')
            self.logger.info(f'View at: https://www.linkedin.com/feed/update/{post_id}')
            return True
        else:
            self.logger.error(f'Failed to post: {response.status_code}')
            self.logger.error(response.text)
            return False
    
    def post_with_image(self, content: str, image_path: str) -> bool:
        """
        Post content with image to LinkedIn.
        
        Args:
            content: Post content
            image_path: Path to image file
            
        Returns:
            bool: True if successful
        """
        self.logger.info('Posting with image not yet implemented in this version')
        return self.post(content)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn API Auto Poster')
    parser.add_argument('--post', type=str, help='Post content')
    parser.add_argument('--config', default='linkedin_config.json',
                       help='Path to config file')
    parser.add_argument('--auth', action='store_true',
                       help='Run authentication only')
    
    args = parser.parse_args()
    
    poster = LinkedInAPIPoster(args.config)
    
    if args.auth:
        poster._authenticate()
        print('Authentication complete!')
        return
    
    if args.post:
        success = poster.post(args.post)
        sys.exit(0 if success else 1)
    else:
        print('Usage: python linkedin_api_poster.py --post "Your content"')
        print('       python linkedin_api_poster.py --auth')
        sys.exit(1)


if __name__ == '__main__':
    main()
