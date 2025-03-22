import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Google Form POST endpoint
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfKby6yb-nf7mh8pl09nhh-1hBbWOpoMtTckBboKQdCMWFs9Q/formResponse"

# Field mapping based on your prefilled link
FORM_FIELDS = {
    "title": "entry.2088210590",
    "description": "entry.1957164180",
    "image": "entry.1419895096",
    "url": "entry.335710612",
    "date": "entry.1788674821"
}

BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"

# Track submitted articles (local state file)
SEEN_FILE = "seen_urls.txt"

def fetch(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# Load previously submitted URLs
seen = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(line.strip() for line in f.readlines())

# Fetch entertainment article URLs
soup = fetch(ENTERTAINMENT_URL)
urls = [
    (a["href"] if a["href"].startswith("http") else BASE_URL + a["href"])
    for a in soup.select("article a[href*='/entertainment/']")
]

new_articles = []
for url in urls:
    if url in seen:
        continue

    page = fetch(url)
    author_el = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author_el or author_el.get_text(strip=True) != AUTHOR_NAME:
        continue

    container = page.select_one("article") or page
    title_el = container.select_one("h3")
    if not title_el:
        continue

    title = title_el.get_text(strip=True)
    desc = container.select_one("p").get_text(strip=True) if container.select_one("p") else ""
    image = container.select_one("picture img")["src"].split("?")[0] if container.select_one("picture img") else ""
    date = datetime.utcnow().strftime("%Y-%m-%d")

    data = {
        FORM_FIELDS["title"]: title,
        FORM_FIELDS["description"]: desc,
        FORM_FIELDS["image"]: image,
        FORM_FIELDS["url"]: url,
        FORM_FIELDS["date"]: date
    }

    res = requests.post(FORM_URL, data=data)
    if res.status_code == 200:
        print(f"✅ Submitted: {title}")
        new_articles.append(url)
    else:
        print(f"❌ Failed to submit {url} – Status {res.status_code}")

# Save newly submitted URLs
if new_articles:
    with open(SEEN_FILE, "a") as f:
        for url in new_articles:
            f.write(url + "\n")
