import json, os, requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"
OUTPUT_FILE = "your_articles.json"

def fetch_page(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# Step 1: Gather all article URLs
soup = fetch_page(ENTERTAINMENT_URL)
links = [a["href"] for a in soup.select("article a[href*='/entertainment/']")]
article_urls = [l if l.startswith("http") else BASE_URL + l for l in links]

# Step 2: Filter by author and extract metadata
new_articles = []
for url in article_urls:
    page = fetch_page(url)
    author = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author or author.get_text(strip=True) != AUTHOR_NAME:
        continue

    container = soup.find("a", href=url.replace(BASE_URL, ""))
    parent = container.find_parent("article") if container else None

    title = parent.select_one("h3").get_text(strip=True) if parent else page.title.string
    desc = parent.select_one("p").get_text(strip=True) if parent and parent.select_one("p") else ""
    img = parent.select_one("picture img")
    img_url = img["src"].split("?")[0] if img else ""

    new_articles.append({"title": title, "description": desc, "image": img_url, "url": url})

# Step 3: Load existing and append only unique
existing = []
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE) as f:
        existing = json.load(f)

added = [a for a in new_articles if not any(e["url"] == a["url"] for e in existing)]
if added:
    existing.extend(added)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Added {len(added)} new articles")
else:
    print("ℹ️ No new articles found")
