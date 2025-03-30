import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "dev-access-454506-p1-769e1e9db6ec.json"
SHEET_NAME = "YLB RSS"
TARGET_SHEET_INDEX = 0  # Sheet1 = index 0

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet("Sheet1")  # Access 'Sheet1'

# Scraper setup
BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"
SEEN_FILE = "seen_urls.txt"

# Function to fetch the page content
def fetch(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# Load previously seen URLs to avoid duplicates
seen = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(line.strip() for line in f.readlines())

# Fetch article URLs from the entertainment section
soup = fetch(ENTERTAINMENT_URL)
urls = [
    (a["href"] if a["href"].startswith("http") else BASE_URL + a["href"])
    for a in soup.select("article a[href*='/entertainment/']")
]

# Debugging: Print all URLs fetched
print("Debugging: Fetched URLs:")
print(urls)
print("------------------------------------------------------")

new_articles = []
for url in urls:
    print(f"Debugging: Processing URL: {url}")

    if url in seen:
        print(f"Debugging: Already seen: {url}")
        continue

    page = fetch(url)

    # 1) Check if author is correct
    author_el = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author_el or author_el.get_text(strip=True) != AUTHOR_NAME:
        print(f"Debugging: Skipping article – author mismatch: {url}")
        continue

    # 2) Grab title, image, and description
    title_el = page.select_one("h1.text-4xl.font-extrabold")
    img_el = page.select_one("img.h-full.w-full.object-cover.object-center")
    desc_el = page.find("meta", attrs={"name": "description"})
    if not title_el:
        print(f"Debugging: Skipping article – no title found: {url}")
        continue

    title = title_el.get_text(strip=True)
    desc = desc_el["content"] if desc_el else ""
    image = img_el["src"].split("?")[0] if (img_el and img_el.has_attr("src")) else ""

    # 3) Find the date element: e.g. "Mar 20, 2025 · 5 min read"
    date_el = page.select_one("span.flex.items-center.gap-1.text-xs.font-medium.text-gray-400")
    if not date_el:
        print(f"Debugging: Skipping article – no date found: {url}")
        continue

    raw_text = date_el.get_text(strip=True)
    # 4) Extract just "Mar 20, 2025" (split at '·')
    date_part = raw_text.split("·")[0].strip()  # => "Mar 20, 2025"

    # 5) Parse into a Python date, then convert to "MM/DD/YYYY 0:00:00"
    try:
        parsed_date = datetime.strptime(date_part, "%b %d, %Y")
        date_str = parsed_date.strftime("%m/%d/%Y") + " 0:00:00"
    except ValueError:
        print(f"Debugging: Date parsing failed for text: '{raw_text}' in {url}")
        continue

    # Debugging: Print data before appending
    print(f"Debugging: Title: {title}")
    print(f"Description: {desc}")
    print(f"Image: {image}")
    print(f"URL: {url}")
    print(f"Date: {date_str}")
    print("------------------------------------------------------")

    # 6) Append the row to Google Sheets
    try:
        sheet.append_row(
            [title, desc, image, url, date_str],
            value_input_option="USER_ENTERED"  # Key for date/time detection
        )
        print(f"✅ Added to sheet: {title}")
        seen.add(url)  # ✅ Add to seen in memory

        # ✅ Immediately write to seen_urls.txt after adding
        with open(SEEN_FILE, "a") as f:
            f.write(url + "\n")

        new_articles.append(url)
    except Exception as e:
        print(f"❌ Failed to add {title} to sheet – {e}")

# Save the URLs we've processed to avoid duplicates
if new_articles:
    with open(SEEN_FILE, "a") as f:
        for url in new_articles:
            f.write(url + "\n")
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add seen_urls.txt
git commit -m "Update seen URLs"
git push
