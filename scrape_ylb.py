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
sheet = client.open(SHEET_NAME).worksheet('Sheet1')  # Access 'Sheet1'

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
    author_el = page.select_one("span.text-sm.font-medium.text-gray-900")
    if not author_el or author_el.get_text(strip=True) != AUTHOR_NAME:
        print(f"Debugging: Skipping article – author mismatch: {url}")
        continue

    title_el = page.select_one("h1.text-4xl.font-extrabold")
    img_el = page.select_one("img.h-full.w-full.object-cover.object-center")
    desc_el = page.find("meta", attrs={"name": "description"})

    if not title_el:
        print(f"Debugging: Skipping article – no title found: {url}")
        continue

    title = title_el.get_text(strip=True)
    desc = desc_el["content"] if desc_el else ""
    image = img_el["src"].split("?")[0] if img_el and img_el.has_attr("src") else ""
    date = datetime.utcnow().strftime("%Y-%m-%d")

    # Debugging: Print data before appending
    print(f"Debugging: Title: {title}")
    print(f"Description: {desc}")
    print(f"Image: {image}")
    print(f"URL: {url}")
    print(f"Date: {date}")
    print("------------------------------------------------------")

    try:
        # Append data to Google Sheets
        sheet.append_row([title, desc, image, url, date])
        print(f"✅ Added to sheet: {title}")
        new_articles.append(url)
    except Exception as e:
        print(f"❌ Failed to add {title} to sheet – {e}")

# Save the URLs we've processed to avoid processing them again in the future
if new_articles:
    with open(SEEN_FILE, "a") as f:
        for url in new_articles:
            f.write(url + "\n")
