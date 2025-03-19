import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"
JSON_FILE = "your_articles.json"
RSS_FILE = "feed.xml"

def fetch(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# --- Scrape logic omitted for brevity: build list `found_articles` same as before ---

# Load existing
existing = []
if os.path.exists(JSON_FILE):
    with open(JSON_FILE) as f: existing = json.load(f)

new = [a for a in found_articles if not any(e['url']==a['url'] for e in existing)]
if new:
    existing.extend(new)
    with open(JSON_FILE, "w") as f: json.dump(existing, f, indent=2)
    print(f"Added {len(new)} new articles")
else:
    print("No new articles")

# --- Build RSS ---
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "Tierney’s Takeaways"
SubElement(channel, "link").text = BASE_URL
SubElement(channel, "description").text = "Latest Hunter Tierney articles"

for item in existing:
    entry = SubElement(channel, "item")
    SubElement(entry, "title").text = item["title"]
    SubElement(entry, "link").text = item["url"]
    SubElement(entry, "description").text = item["description"]
    SubElement(entry, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

ElementTree(rss).write(RSS_FILE, encoding="utf-8", xml_declaration=True)
print(f"Generated {RSS_FILE}")
