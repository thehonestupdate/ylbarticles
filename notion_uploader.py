import json
import requests
import os

# Load articles.json
with open("articles.json", "r") as f:
    articles = json.load(f)

# Get API Key & Notion Database ID from GitHub Secrets
NOTION_API_KEY = os.getenv("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")
NOTION_DATABASE_ID = "1bba2b92b8148068b66ce0404a2c9a86"  # Replace with your Notion Database ID

# Notion API URL
NOTION_URL = f"https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Send each article to Notion
for article in articles:
    title = article["title"]
    url = article["url"]
    description = article["description"]
    image = article["image"]

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "Description": {"rich_text": [{"text": {"content": description}}]},
            "Image": {"url": image}
        }
    }

    response = requests.post(NOTION_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"✅ Added: {title}")
    else:
        print(f"❌ Failed to add: {title} | Response: {response.text}")
