import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Constants
BASE_URL = "https://www.yourlifebuzz.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment/"
AUTHOR_NAME = "Hunter Tierney"
OUTPUT_FILE = "your_articles.json"

# Set up Selenium
options = Options()
options.add_argument("--headless")  # No UI
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# Open Entertainment page
driver.get(ENTERTAINMENT_URL)
time.sleep(5)  # Ensure page loads

# Extract article links
article_links = []
articles = driver.find_elements(By.TAG_NAME, "article")

print(f"✅ Found {len(articles)} articles on the page.")

for index, article in enumerate(articles):
    try:
        # Extract first <a> tag inside each <article> (Primary Link)
        link_element = article.find_element(By.CSS_SELECTOR, "a[href*='/entertainment/']")
        link = link_element.get_attribute("href")

        if link and link.startswith("/"):
            link = BASE_URL + link  # Convert relative URL to full URL
        article_links.append(link)

    except Exception as e:
        print(f"❌ Error extracting link from article {index+1}: {e}")

# Print extracted URLs
print("\n🔗 **Extracted Article Links:**")
for idx, link in enumerate(article_links, 1):
    print(f"{idx}. {link}")

print(f"\n✅ Total Article Links Found: {len(article_links)}")

# ✅ Visit each article to check for the author's name in <span class="text-sm font-medium text-gray-900">
your_articles = []

for article_url in article_links:
    driver.get(article_url)
    time.sleep(3)  # Allow content to load

    try:
        author_element = driver.find_element(By.CSS_SELECTOR, "span.text-sm.font-medium.text-gray-900")
        author_text = author_element.text.strip()

        if author_text == AUTHOR_NAME:
            print(f"✔ Found article by {AUTHOR_NAME}: {article_url}")
            your_articles.append(article_url)
        else:
            print(f"❌ Not your article ({author_text}): {article_url}")

    except:
        print(f"⚠️ Could not find author info: {article_url}")

# ✅ Now go back to Entertainment page & extract metadata for YOUR articles
your_articles_data = []

driver.get(ENTERTAINMENT_URL)
time.sleep(5)  # Reload page

for article_url in your_articles:
    try:
        # Find the article element by matching the link
        article = driver.find_element(By.CSS_SELECTOR, f"a[href='{article_url.replace(BASE_URL, '')}']")
        parent_article = article.find_element(By.XPATH, "./ancestor::article")

        # Extract title
        title_element = parent_article.find_element(By.TAG_NAME, "h3")
        title = title_element.text.strip() if title_element else "No Title"

        # Extract meta description
        desc_element = parent_article.find_element(By.TAG_NAME, "p")
        description = desc_element.text.strip() if desc_element else "No Description"

        # Extract image URL
        try:
            image_element = parent_article.find_element(By.CSS_SELECTOR, "picture img")
            image_url = image_element.get_attribute("src") if image_element else "No Image"
            clean_image_url = image_url.split('?')[0]
        except:
            image_url = "No Image"

        # Store data
        your_articles_data.append({
            "title": title,
            "description": description,
            "image": clean_image_url,
            "url": article_url
        })

    except Exception as e:
        print(f"❌ Error extracting metadata for {article_url}: {e}")

# ✅ Print the final list of your articles
print("\n📌 **Your Articles:**")
for article in your_articles_data:
    print(f"{article['title']} - {article['url']}")

# ✅ Save your articles with title, description, and image
with open(OUTPUT_FILE, "w") as f:
    json.dump(your_articles_data, f, indent=4)

print(f"\n💾 Articles saved to {OUTPUT_FILE}")

# Close the browser
driver.quit()
