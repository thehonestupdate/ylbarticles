import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"
JSON_FILE = "your_articles.json"
RSS_FILE = "feed.xml"

def fetch(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# Scrape article URLs
soup = fetch(ENTERTAINMENT_URL)
links = [a["href"] for a in soup.select("article a[href*='/entertainment/']")]
urls = [(l if l.startswith("http") else BASE_URL + l) for l in links]

# Filter by author & extract metadata
found = []
for url in urls:
    page = fetch(url)
    author = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author or author.text.strip() != AUTHOR_NAME:
        continue

    container = page.select_one("article") or page
    title = container.select_one("h3").get_text(strip=True)
    desc = container.select_one("p").get_text(strip=True) if container.select_one("p") else ""
    img = container.select_one("picture img")
    img_url = img["src"].split("?")[0] if img else ""
    found.append({"title": title, "description": desc, "image": img_url, "url": url})

# Load existing data
existing = []
if os.path.exists(JSON_FILE):
    with open(JSON_FILE) as f:
        existing = json.load(f)

# Append only new articles
new = [item for item in found if all(item["url"] != e["url"] for e in existing)]
if new:
    existing.extend(new)
    with open(JSON_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Added {len(new)} new articles")
else:
    print("ℹ️ No new articles")

# Build RSS feed.xml
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "Tierney’s Takeaways"
SubElement(channel, "link").text = BASE_URL
SubElement(channel, "description").text = "Latest articles by Hunter Tierney"

for article in existing:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = article["title"]
    SubElement(item, "link").text = article["url"]
    SubElement(item, "description").text = article["description"]
    SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

ElementTree(rss).write(RSS_FILE, encoding="utf-8", xml_declaration=True)
print(f"✅ Generated {RSS_FILE}")
