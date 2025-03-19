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

# 1️⃣ Gather article URLs
soup = fetch(ENTERTAINMENT_URL)
urls = [
    (a["href"] if a["href"].startswith("http") else BASE_URL + a["href"])
    for a in soup.select("article a[href*='/entertainment/']")
]

found = []
for url in urls:
    page = fetch(url)
    author_el = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author_el or author_el.get_text(strip=True) != AUTHOR_NAME:
        continue

    container = page.select_one("article") or page
    title_el = container.select_one("h3")
    if not title_el:
        continue

    found.append({
        "title": title_el.get_text(strip=True),
        "description": (container.select_one("p").get_text(strip=True) if container.select_one("p") else ""),
        "image": (container.select_one("picture img")["src"].split("?")[0] if container.select_one("picture img") else ""),
        "url": url
    })

# 2️⃣ Load existing feed
existing = []
if os.path.exists(JSON_FILE):
    with open(JSON_FILE) as f:
        existing = json.load(f)

new = [item for item in found if all(item["url"] != e["url"] for e in existing)]
if new:
    existing.extend(new)
    with open(JSON_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Added {len(new)} new article(s)")
else:
    print("ℹ️ No new articles")

# 3️⃣ Build RSS
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "Tierney’s Takeaways"
SubElement(channel, "link").text = BASE_URL
SubElement(channel, "description").text = "Latest articles by Hunter Tierney"

for art in existing:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = art["title"]
    SubElement(item, "link").text = art["url"]
    SubElement(item, "description").text = art["description"]
    SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

ElementTree(rss).write(RSS_FILE, encoding="utf-8", xml_declaration=True)
print(f"✅ Generated {RSS_FILE}")
