import gspread
import requests
import pandas as pd
import random
from bs4 import BeautifulSoup
from datetime import datetime
from google.oauth2.service_account import Credentials

# Define authentication scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load Google Sheets credentials
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

# Open Google Sheet
SHEET = CLIENT.open("Cyber Threat Intel Feed").sheet1  # Change if needed

# Rotate User-Agents to avoid being blocked
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
]

HEADERS = {"User-Agent": random.choice(USER_AGENTS)}

# -------------------------------
# ✅ Function: Fetch Latest CVEs (Fixed API)
# -------------------------------
def fetch_latest_cves():
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    response = requests.get(url, headers=HEADERS)
    
    print("\n🔹 Fetching CVE Data...")
    print(f"   🟢 API Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   🔍 Number of CVEs Found: {len(data.get('vulnerabilities', []))}")
        
        cve_entries = []
        for item in data["vulnerabilities"][:5]:  # Fetch the latest 5 CVEs
            cve_id = item["cve"]["id"]
            description = item["cve"]["descriptions"][0]["value"]
            link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            cve_entries.append([datetime.today().strftime('%Y-%m-%d'), "NVD", cve_id, "", description, link])
        
        return cve_entries
    
    print("❌ CVE API Failed - No Data Retrieved")
    return []

# -------------------------------
# ✅ Function: Scrape Cybersecurity News (Fixed Selectors)
# -------------------------------
def fetch_cyber_news():
    sources = [
        ("BleepingComputer", "https://www.bleepingcomputer.com/news/security/", "h4.bc_latestnews a", "meta[name='description']", "time"),
        ("The Hacker News", "https://thehackernews.com/", "article header h2 a", "meta[name='description']", "span.story-date"),
        ("Dark Reading", "https://www.darkreading.com/", "section.article-listing h3 a", "meta[name='description']", "time"),
        ("Krebs on Security", "https://krebsonsecurity.com/", "h2.post-title a", "meta[name='description']", "time"),
    ]

    news_entries = []
    today_date = datetime.today().strftime('%Y-%m-%d')

    print("\n🔹 Fetching Cybersecurity News...")

    for source, base_url, selector, description_selector, date_selector in sources:
        print(f"🔎 Attempting to connect to {source} ({base_url})...")

        try:
            response = requests.get(base_url, headers=HEADERS, timeout=10)
            print(f"   🟢 {source} - Status Code: {response.status_code}")

            if response.status_code == 403:
                print(f"   ❌ {source} is blocking requests (403 Forbidden). Skipping...")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select(selector)[:5]

            if not articles:
                print(f"   ❌ No Articles Found on {source}. Selector might be incorrect.")
                continue  
            
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get("href")

                if link and not link.startswith("http"):
                    link = base_url + link

                # Fetch article page to extract description and date
                description = "No description available."
                publication_date = "Unknown"
                article_response = requests.get(link, headers=HEADERS, timeout=10)

                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.text, "html.parser")

                    # Extract description
                    if "meta" in description_selector:
                        meta_tag = article_soup.select_one(description_selector)
                        if meta_tag and meta_tag.get("content"):
                            description = meta_tag["content"]
                    else:
                        desc_tag = article_soup.select_one(description_selector)
                        if desc_tag:
                            description = desc_tag.get_text(strip=True)

                    # Extract publication date
                    date_tag = article_soup.select_one(date_selector)
                    if date_tag:
                        publication_date = date_tag.get_text(strip=True)

                # 🔹 Print extracted data
                print(f"   ✅ {source} | {title} | 📅 {publication_date} | 🔗 {link}")

                # 🔹 Append data in the correct format
                news_entries.append([
                    today_date,  # Date Added
                    source,  # News Source
                    title,  # Article Title
                    publication_date,  # Article Publish Date
                    description,  # Short Description
                    link  # Article Link
                ])

        except requests.exceptions.Timeout:
            print(f"   ❌ {source} request timed out. Skipping...")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error on {source}: {e}")
            continue  

    return news_entries

# -------------------------------
# ✅ Function: Update Google Sheet
# -------------------------------
def update_google_sheet():
    cve_data = fetch_latest_cves()
    news_data = fetch_cyber_news()

    existing_data = SHEET.get_all_values()

    # 🔹 Ensure the correct headers are set
    if len(existing_data) == 0:
        SHEET.append_row(["Date Added", "Source", "Title", "Publication Date", "Description", "Link"])

    all_data = []

    # 🔹 Append CVE data
    for entry in cve_data:
        all_data.append(entry)  # (Date Added, Source, Title, Publication Date, Description, Link)

    # 🔹 Append cybersecurity news data
    for entry in news_data:
        all_data.append(entry)

    # 🔹 Add all rows at once (Better Performance)
    SHEET.append_rows(all_data)

    print("\n✅ Cyber Threat Intel Feed Successfully Updated in Google Sheets!\n")


# Run the update function
update_google_sheet()
