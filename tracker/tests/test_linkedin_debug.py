#!/usr/bin/env python
"""Debug LinkedIn parsing."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.linkedin.com/jobs/search?keywords=software engineer&location=Remote")
time.sleep(3)

cards = driver.find_elements(By.CLASS_NAME, "base-card")
print(f"Found {len(cards)} cards\n")

for i, card in enumerate(cards[:3], 1):
    print(f"=== CARD {i} ===")

    # Title
    try:
        title = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").text
        print(f"Title: {title}")
    except Exception as e:
        print(f"Title error: {e}")

    # Company
    try:
        company = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a").text
        print(f"Company (nested link): '{company}'")
    except Exception as e:
        print(f"Company (nested link) error: {e}")
        try:
            company = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").text
            print(f"Company (h4 text): '{company}'")
        except Exception as e2:
            print(f"Company (h4) error: {e2}")

    # Location
    try:
        location = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location").text
        print(f"Location: '{location}'")
    except Exception as e:
        print(f"Location error: {e}")

    # URL
    try:
        link = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
        href = link.get_attribute('href')
        print(f"URL (base-card__full-link): {href}")
    except Exception as e:
        print(f"URL (base-card__full-link) error: {e}")
        try:
            link = card.find_element(By.CSS_SELECTOR, "a[href*='jobs/view']")
            href = link.get_attribute('href')
            print(f"URL (alternative): {href}")
        except Exception as e2:
            print(f"URL (alternative) error: {e2}")

    print()

driver.quit()
