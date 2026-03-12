"""
Facebook MCP Server - Facebook Graph API Integration

Provides tools for:
- Posting to Facebook
- Reading page insights
- Managing comments
- Sending messages

Usage:
    python mcp-servers/facebook_mcp_server.py
"""

import sys
import json
import logging
import requests
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FacebookMCP')


class FacebookMCPServer:
    """Facebook MCP Server for Graph API integration."""

    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')

        if not self.access_token:
            logger.warning('Facebook access token not found. Configure in .env')
        else:
            logger.info(f'Facebook configuration loaded (Page: {self.page_id})')

    def post(self, message: str, link: str = None) -> dict:
        """Post to Facebook page."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = f'https://graph.facebook.com/v18.0/{self.page_id}/feed'
        params = {
            'message': message,
            'access_token': self.access_token
        }
        
        if link:
            params['link'] = link
        
        try:
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                logger.info(f'Post created: {result.get("id")}')
                return {
                    'success': True,
                    'post_id': result.get('id'),
                    'url': f'https://facebook.com/{result.get("id")}'
                }
            else:
                logger.error(f'Post failed: {response.text}')
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f'Error: {e}')
            return {'success': False, 'error': str(e)}
    
    def post_photo(self, message: str, photo_url: str) -> dict:
        """Post photo to Facebook page."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = f'https://graph.facebook.com/v18.0/{self.page_id}/photos'
        params = {
            'url': photo_url,
            'caption': message,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                return {'success': True, 'photo_id': result.get('id')}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_insights(self, metric: str = 'page_impressions') -> dict:
        """Get page insights."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = f'https://graph.facebook.com/v18.0/{self.page_id}/insights'
        params = {
            'metric': metric,
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_comments(self, post_id: str) -> dict:
        """Get comments on a post."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = f'https://graph.facebook.com/v18.0/{post_id}/comments'
        params = {
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return {'success': True, 'comments': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def reply_comment(self, post_id: str, message: str) -> dict:
        """Reply to a comment."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = f'https://graph.facebook.com/v18.0/{post_id}/comments'
        params = {
            'message': message,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                return {'success': True, 'comment_id': result.get('id')}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method', '')
    params = request.get('params', {})
    
    server = FacebookMCPServer()
    
    if method == 'facebook/post':
        result = server.post(
            message=params.get('message', ''),
            link=params.get('link')
        )
    elif method == 'facebook/post_photo':
        result = server.post_photo(
            message=params.get('message', ''),
            photo_url=params.get('photo_url', '')
        )
    elif method == 'facebook/get_insights':
        result = server.get_insights(params.get('metric', 'page_impressions'))
    elif method == 'facebook/get_comments':
        result = server.get_comments(params.get('post_id', ''))
    elif method == 'facebook/reply_comment':
        result = server.reply_comment(
            params.get('post_id', ''),
            params.get('message', '')
        )
    else:
        result = {'success': False, 'error': f'Unknown method: {method}'}
    
    return {'jsonrpc': '2.0', 'id': request.get('id'), 'result': result}


def main():
    """Run MCP server (stdio mode)."""
    logger.info('Facebook MCP Server started')
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': str(e)}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    main()
