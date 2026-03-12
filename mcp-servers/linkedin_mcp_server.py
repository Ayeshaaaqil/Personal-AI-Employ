"""
LinkedIn MCP Server - LinkedIn integration via API

Provides tools for:
- Posting updates
- Reading profile
- Sending messages
- Getting connections
"""

import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LinkedInMCP')


class LinkedInMCPServer:
    """LinkedIn MCP Server."""
    
    def __init__(self):
        self.access_token = None
        self.person_urn = None
        self._load_token()
    
    def _load_token(self):
        """Load LinkedIn API token."""
        token_path = Path('linkedin_api_token.json')
        if token_path.exists():
            import json
            token = json.loads(token_path.read_text())
            self.access_token = token.get('access_token')
            self.person_urn = token.get('person_urn')
            logger.info('LinkedIn API token loaded')
        else:
            logger.warning('LinkedIn token not found. Run linkedin_api_poster.py --auth first')
    
    def post(self, content: str) -> dict:
        """Post to LinkedIn."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        url = 'https://api.linkedin.com/v2/shares'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        payload = {
            'owner': f'urn:li:person:{self.person_urn}',
            'content': {
                'contentEntities': [],
                'text': {'text': content}
            },
            'visibility': 'PUBLIC'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                result = response.json()
                return {'success': True, 'post_id': result.get('id')}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_profile(self) -> dict:
        """Get LinkedIn profile."""
        if not self.access_token:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            response = requests.get(
                'https://api.linkedin.com/v2/me',
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            if response.status_code == 200:
                return {'success': True, 'profile': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method', '')
    params = request.get('params', {})
    
    server = LinkedInMCPServer()
    
    if method == 'linkedin/post':
        result = server.post(params.get('content', ''))
    elif method == 'linkedin/get_profile':
        result = server.get_profile()
    else:
        result = {'success': False, 'error': f'Unknown method: {method}'}
    
    return {'jsonrpc': '2.0', 'id': request.get('id'), 'result': result}


def main():
    """Run MCP server."""
    logger.info('LinkedIn MCP Server started')
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'id': None, 'error': {'message': str(e)}}), flush=True)


if __name__ == '__main__':
    main()
