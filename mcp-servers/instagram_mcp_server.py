"""
Instagram MCP Server - Business Integration

This MCP server provides Instagram Business API integration.
Supports posting photos, stories, and monitoring engagement.

Setup:
1. Get Instagram Business API credentials from Meta Developers
2. Add credentials to .env file
3. Run this server

Usage:
    python instagram_mcp_server.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InstagramBusinessAPI:
    """Instagram Business API Client"""
    
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.instagram_business_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        
        # For demo/testing, use mock mode if no credentials
        self.mock_mode = not self.access_token or not self.instagram_business_account_id
        
        if self.mock_mode:
            logger.warning("Instagram credentials not found. Running in MOCK mode.")
            logger.warning("Set INSTAGRAM_ACCESS_TOKEN in .env for live posting")
    
    def post_photo(self, image_url: str, caption: str = "") -> Dict:
        """Post a photo to Instagram"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'message': 'Photo would be posted to Instagram',
                'caption': caption[:50] + '...' if len(caption) > 50 else caption
            }
        
        try:
            # Step 1: Create media container
            url = f'https://graph.facebook.com/v17.0/{self.instagram_business_account_id}/media'
            params = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.access_token
            }
            
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            
            creation_data = response.json()
            creation_id = creation_data.get('id')
            
            # Step 2: Publish the media
            publish_url = f'https://graph.facebook.com/v17.0/{self.instagram_business_account_id}/media_publish'
            publish_params = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, params=publish_params, timeout=30)
            publish_response.raise_for_status()
            
            publish_data = publish_response.json()
            
            return {
                'success': True,
                'media_id': publish_data.get('id'),
                'caption': caption
            }
            
        except Exception as e:
            logger.error(f'Error posting to Instagram: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_story(self, image_url: str) -> Dict:
        """Post a story to Instagram"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'message': 'Story would be posted to Instagram'
            }
        
        try:
            # Similar to post_photo but for stories
            url = f'https://graph.facebook.com/v17.0/{self.instagram_business_account_id}/media'
            params = {
                'image_url': image_url,
                'media_type': 'STORY',
                'access_token': self.access_token
            }
            
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Story posted successfully'
            }
            
        except Exception as e:
            logger.error(f'Error posting story: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_insights(self) -> Dict:
        """Get Instagram account insights"""
        if self.mock_mode:
            return {
                'success': True,
                'mock': True,
                'insights': {
                    'followers_count': 1250,
                    'impressions': 5420,
                    'reach': 3890,
                    'profile_views': 245
                }
            }
        
        try:
            url = f'https://graph.facebook.com/v17.0/{self.instagram_business_account_id}'
            params = {
                'fields': 'followers_count,media_count,website',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'insights': data
            }
            
        except Exception as e:
            logger.error(f'Error getting insights: {e}')
            return {
                'success': False,
                'error': str(e)
            }


class InstagramMCPServer:
    """Instagram MCP Server"""
    
    def __init__(self):
        self.api = InstagramBusinessAPI()
        self.vault_path = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle MCP request"""
        method = request.get('method', '')
        params = request.get('params', {})
        request_id = request.get('id', 1)
        
        logger.info(f'Handling method: {method}')
        
        try:
            if method == 'instagram/post_photo':
                result = self.api.post_photo(
                    image_url=params.get('image_url', ''),
                    caption=params.get('caption', '')
                )
            
            elif method == 'instagram/post_story':
                result = self.api.post_story(
                    image_url=params.get('image_url', '')
                )
            
            elif method == 'instagram/get_insights':
                result = self.api.get_insights()
            
            elif method == 'instagram/log_activity':
                result = self.log_activity(params)
            
            else:
                result = {
                    'success': False,
                    'error': f'Unknown method: {method}'
                }
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f'Error handling {method}: {e}')
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }
    
    def log_activity(self, params: Dict) -> Dict:
        """Log Instagram activity to vault"""
        activity_type = params.get('type', 'post')
        content = params.get('content', '')
        timestamp = params.get('timestamp', datetime.now().isoformat())
        
        filename = f'INSTAGRAM_{activity_type.upper()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        filepath = self.needs_action / filename
        
        md_content = f'''---
type: instagram_{activity_type}
timestamp: {timestamp}
status: pending
---

# Instagram Activity

**Type:** {activity_type}
**Time:** {timestamp}

## Content

{content}

## Actions

- [ ] Review activity
- [ ] Respond to comments
- [ ] Mark as done
'''
        
        filepath.write_text(md_content, encoding='utf-8')
        
        return {
            'success': True,
            'file': str(filepath),
            'filename': filename
        }


def main():
    """Main entry point"""
    print("=" * 60)
    print("📸 Instagram MCP Server")
    print("=" * 60)
    print()
    
    server = InstagramMCPServer()
    
    print("Server running. Send JSON-RPC requests via stdin.")
    print("Example request:")
    print('{"method": "instagram/post_photo", "params": {"image_url": "https://...", "caption": "Hello!"}, "id": 1}')
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Read requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {
                    'code': -32700,
                    'message': 'Parse error'
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == '__main__':
    main()
