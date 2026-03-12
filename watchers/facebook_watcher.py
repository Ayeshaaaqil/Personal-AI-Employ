"""
Facebook Watcher & Auto Poster - Monitor and post to Facebook

Monitors Facebook for activity using Graph API.
No browser automation needed - uses official Facebook API.
"""

import sys
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


class FacebookWatcher(BaseWatcher):
    """Monitor Facebook for activity using Graph API."""

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize Facebook watcher.

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)

        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = "https://graph.facebook.com/v18.0"

        if not self.access_token or not self.page_id:
            self.logger.warning('Facebook credentials not found. Configure in .env')

    def check_for_updates(self) -> list:
        """Check Facebook for new activity using Graph API."""
        items = []

        if not self.access_token:
            self.logger.warning('No access token configured')
            return items

        try:
            # Check for new posts/engagement
            url = f"{self.base_url}/{self.page_id}/posts"
            params = {
                'access_token': self.access_token,
                'limit': 5,
                'fields': 'id,message,created_time,likes.summary(true),comments.summary(true)'
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])

                # Check for recent engagement (last hour)
                one_hour_ago = datetime.now().timestamp() - 3600

                for post in posts:
                    created_time = datetime.fromisoformat(
                        post.get('created_time', '').replace('Z', '+00:00')
                    ).timestamp()

                    if created_time > one_hour_ago:
                        likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                        comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)

                        if likes > 0 or comments > 0:
                            items.append({
                                'type': 'engagement',
                                'post_id': post.get('id'),
                                'likes': likes,
                                'comments': comments,
                                'priority': 'high' if comments > 0 else 'medium'
                            })

            # Check for messages (page inbox)
            inbox_url = f"{self.base_url}/{self.page_id}/conversations"
            inbox_params = {
                'access_token': self.access_token,
                'fields': 'messages,updated_time,unread_count'
            }

            inbox_response = requests.get(inbox_url, params=inbox_params, timeout=30)

            if inbox_response.status_code == 200:
                inbox_data = inbox_response.json()
                conversations = inbox_data.get('data', [])

                for conv in conversations:
                    unread = conv.get('unread_count', 0)
                    if unread > 0:
                        items.append({
                            'type': 'messages',
                            'conversation_id': conv.get('id'),
                            'count': unread,
                            'priority': 'high'
                        })

        except Exception as e:
            self.logger.error(f'Error checking Facebook: {e}')

        return items

    def create_action_file(self, item) -> Path:
        """Create action file for Facebook activity."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'FACEBOOK_{item["type"].upper()}_{timestamp}.md'
        filepath = self.needs_action / filename

        if item['type'] == 'engagement':
            content = f'''---
type: facebook_engagement
source: Facebook Graph API
received: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
post_id: {item.get('post_id')}
likes: {item.get('likes')}
comments: {item.get('comments')}
---

# Facebook Engagement Alert

**Post ID:** {item.get('post_id')}
**Received:** {datetime.now().isoformat()}
**Priority:** {item['priority'].upper()}

---

## Engagement Summary

- **Likes:** {item.get('likes')}
- **Comments:** {item.get('comments')}

---

## Suggested Actions

- [ ] Review the post engagement
- [ ] Respond to comments if needed
- [ ] Thank users for likes (optional)
- [ ] Mark as processed

---

*Created by Facebook Watcher (Graph API)*
'''
        elif item['type'] == 'messages':
            content = f'''---
type: facebook_messages
source: Facebook Graph API
received: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
conversation_id: {item.get('conversation_id')}
unread_count: {item.get('count')}
---

# Facebook Messages Alert

**Conversation ID:** {item.get('conversation_id')}
**Received:** {datetime.now().isoformat()}
**Priority:** {item['priority'].upper()}

---

## Message Summary

- **Unread Messages:** {item.get('count')}

---

## Suggested Actions

- [ ] Open Facebook Messenger
- [ ] Review unread messages
- [ ] Respond promptly
- [ ] Mark as processed

---

*Created by Facebook Watcher (Graph API)*
'''
        else:
            content = f'''---
type: facebook_{item['type']}
source: Facebook Graph API
received: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
---

# Facebook Activity Alert

**Type:** {item['type']}
**Received:** {datetime.now().isoformat()}
**Priority:** {item['priority'].upper()}

---

## Summary

New Facebook activity detected

---

## Suggested Actions

- [ ] Open Facebook
- [ ] Review activity
- [ ] Respond if needed
- [ ] Mark as processed

---

*Created by Facebook Watcher (Graph API)*
'''

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filename}')
        return filepath


class FacebookAutoPoster:
    """Post to Facebook automatically using Graph API."""

    def __init__(self):
        """Initialize Facebook poster with Graph API."""
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = "https://graph.facebook.com/v18.0"
        self.logger = logging.getLogger(self.__class__.__name__)

        if not self.access_token:
            self.logger.warning('Facebook access token not found')

    def post(self, content: str, link: str = None) -> bool:
        """
        Post content to Facebook using Graph API.

        Args:
            content: Post content
            link: Optional link to share

        Returns:
            bool: True if successful
        """
        if not self.access_token:
            self.logger.error('No access token configured')
            return False

        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            params = {
                'message': content,
                'access_token': self.access_token
            }

            if link:
                params['link'] = link

            response = requests.post(url, data=params, timeout=30)

            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                self.logger.info(f'Post created successfully: {post_id}')
                print(f"\n[SUCCESS] Post created!")
                print(f"Post ID: {post_id}")
                print(f"URL: https://facebook.com/{post_id}")
                return True
            else:
                error = response.json()
                self.logger.error(f'Post failed: {error}')
                print(f"\n[ERROR] Post failed: {error}")
                return False

        except Exception as e:
            self.logger.error(f'Error posting to Facebook: {e}')
            print(f"\n[ERROR] {e}")
            return False

    def post_photo(self, content: str, photo_path: str) -> bool:
        """
        Post photo to Facebook using Graph API.

        Args:
            content: Caption for the photo
            photo_path: Path to photo file

        Returns:
            bool: True if successful
        """
        if not self.access_token:
            self.logger.error('No access token configured')
            return False

        try:
            url = f"{self.base_url}/{self.page_id}/photos"
            params = {
                'caption': content,
                'access_token': self.access_token
            }

            with open(photo_path, 'rb') as f:
                files = {'source': f}
                response = requests.post(url, data=params, files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                photo_id = result.get('id')
                self.logger.info(f'Photo posted successfully: {photo_id}')
                print(f"\n[SUCCESS] Photo posted!")
                print(f"Photo ID: {photo_id}")
                return True
            else:
                error = response.json()
                self.logger.error(f'Photo post failed: {error}')
                print(f"\n[ERROR] Photo post failed: {error}")
                return False

        except Exception as e:
            self.logger.error(f'Error posting photo: {e}')
            print(f"\n[ERROR] {e}")
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook Watcher & Poster (Graph API)')
    parser.add_argument('vault_path', nargs='?', default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds')
    parser.add_argument('--post', type=str, help='Post content')
    parser.add_argument('--post-photo', type=str, help='Post photo with caption')
    parser.add_argument('--link', type=str, help='Link to share with post')

    args = parser.parse_args()

    vault_path = Path(args.vault_path)

    if args.post:
        # Post to Facebook using Graph API
        poster = FacebookAutoPoster()
        success = poster.post(args.post, args.link)
        sys.exit(0 if success else 1)

    if args.post_photo:
        # Post photo to Facebook
        poster = FacebookAutoPoster()
        success = poster.post_photo(args.post_photo, args.link or '')
        sys.exit(0 if success else 1)

    # Run watcher
    watcher = FacebookWatcher(str(vault_path), args.interval)
    print(f'Starting Facebook Watcher (interval: {args.interval}s)')
    print('Monitoring for engagement and messages via Graph API...')
    watcher.run()


if __name__ == '__main__':
    main()
