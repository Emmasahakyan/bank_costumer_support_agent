from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import re

def clean_text(text):
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    text = "\n".join(unique_lines)
    text = re.sub(r' +', ' ', text)
    return text

def scrape_all_subpages(base_url):
    from urllib.parse import urlparse
    
    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    base_path = parsed.path.rstrip("/")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Step 1 - scrape main page
    driver.get(base_url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_text = clean_text(soup.get_text())
    
    # Step 2 - find only DIRECT subpage links
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # make full URL if relative
        if href.startswith("/"):
            href = f"{base_domain}{href}"
        # only keep links that START with base_url (direct subpages only)
        if href.startswith(base_url) and href != base_url and href != base_url + "/":
            links.add(href)
    
    print(f"  Found {len(links)} subpages")
    
    # Step 3 - scrape each subpage
    for link in links:
        print(f"  → scraping: {link}")
        try:
            driver.get(link)
            time.sleep(3)
            sub_soup = BeautifulSoup(driver.page_source, "html.parser")
            all_text += "\n" + clean_text(sub_soup.get_text())
        except Exception as e:
            print(f"failed: {link} — {e}")
    
    driver.quit()
    return all_text

banks = {
    "idbank": {
        "credits": "https://idbank.am/credits/",
        "deposits": "https://idbank.am/deposits/",
        "branches": "https://idbank.am/information/about/branches-and-atms/"
    },
    "fastbank": {
        "credits": "https://www.fastbank.am/hy/individual/loans",
        "deposits": "https://www.fastbank.am/hy/individual/deposits",
        "branches": "https://www.fastbank.am/hy/branches"
    },
    "ameriabank": {
        "credits": "https://ameriabank.am/personal/loans",
        "deposits": "https://ameriabank.am/personal/saving",
        "branches": "https://ameriabank.am/service-network"
    },
}

os.makedirs("data", exist_ok=True)

for bank_name, pages in banks.items():
    os.makedirs(f"data/{bank_name}", exist_ok=True)
    for topic, url in pages.items():
        print(f"Scraping {bank_name} - {topic}...")
        text = scrape_all_subpages(url)
        with open(f"data/{bank_name}/{topic}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved data/{bank_name}/{topic}.txt")

print("All done!")
