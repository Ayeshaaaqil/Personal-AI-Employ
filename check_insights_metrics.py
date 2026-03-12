"""Check available Facebook Page Insights metrics"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# Common valid metrics for Facebook Pages
valid_metrics = [
    "page_impressions",
    "page_impressions_unique",
    "page_impressions_paid",
    "page_impressions_organic",
    "page_engaged_users",
    "page_post_engagements",
    "page_posts_impressions",
    "page_posts_impressions_unique",
    "page_consumptions",
    "page_consumptions_unique",
    "page_clicks",
    "page_clicks_unique",
    "page_views_total",
    "page_views_unique",
    "page_fans",
    "page_fan_adds",
    "page_fan_removes",
    "page_likes",
    "page_unlikes",
    "page_followers",
]

print("Testing available metrics for your page...\n")

for metric in valid_metrics[:10]:  # Test first 10
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/insights"
    params = {
        'metric': metric,
        'access_token': ACCESS_TOKEN,
        'since': '2026-03-01',
        'until': '2026-03-31'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            print(f"[OK] {metric}: AVAILABLE")
        else:
            print(f"[NO DATA] {metric}: Valid but no data")
    else:
        print(f"[INVALID] {metric}: {response.json().get('error', {}).get('message', '')[:60]}")
