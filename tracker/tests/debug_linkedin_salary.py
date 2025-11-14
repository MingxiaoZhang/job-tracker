"""
Debug script to inspect LinkedIn job card HTML and find salary selectors.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sys

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = None
try:
    # Initialize Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    # Build search URL
    search_query = "software engineer"
    location = "Remote"
    url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location={location}&f_TPR=r604800&sortBy=DD"

    print(f"Navigating to: {url}\n")
    driver.get(url)

    # Wait for job cards to load
    time.sleep(3)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "base-card")))

    # Find all job cards
    job_cards = driver.find_elements(By.CLASS_NAME, "base-card")

    print(f"Found {len(job_cards)} job cards\n")
    print("=" * 80)

    # Get the first job URL and navigate to it
    print("\n" + "="*80)
    print("Testing salary extraction from JOB DETAIL PAGE")
    print("="*80 + "\n")

    try:
        # Get first job card link
        first_card = job_cards[1]  # Use second job (Wanderlog from your example)
        link_elem = first_card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
        job_url = link_elem.get_attribute('href')

        print(f"Navigating to job detail page: {job_url}\n")
        driver.get(job_url)

        # Wait for detail page to load
        time.sleep(3)

        # Extract title from detail page
        try:
            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-details-jobs-unified-top-card__job-title, h1.t-24")))
            title = (title_elem.get_attribute('innerText') or title_elem.text or "").strip()
            print(f"Job Title: {title}")
        except Exception as e:
            print(f"Could not extract title: {e}")

        # Try to extract salary using various selectors
        print("\n--- Testing salary selectors ---\n")

        salary_selectors = [
            # Based on your HTML example
            "div.job-details-fit-level-preferences button strong",
            "div.job-details-fit-level-preferences button",
            "div.job-details-fit-level-preferences",
            # Alternative selectors
            "[class*='salary']",
            "[class*='compensation']",
            "button.artdeco-button--muted strong",
            ".tvm__text--low-emphasis strong",
        ]

        for selector in salary_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Selector: '{selector}'")
                    print(f"Found {len(elements)} elements:")
                    for elem in elements:
                        text = (elem.get_attribute('innerText') or elem.text or "").strip()
                        if text:
                            print(f"  Text: '{text}'")
                            # Check if it looks like salary (contains $ and numbers)
                            if '$' in text or any(c.isdigit() for c in text):
                                print(f"  ✓ Potential salary data!")
                    print()
            except Exception as e:
                print(f"Error with selector '{selector}': {e}\n")

        # Get a snippet of the detail page HTML
        print("\n--- Detail Page HTML (searching for 'fit-level' or salary) ---")
        page_source = driver.page_source

        # Find sections that might contain salary
        if "job-details-fit-level-preferences" in page_source:
            print("✓ Found 'job-details-fit-level-preferences' in page!")
            start_idx = page_source.find("job-details-fit-level-preferences")
            snippet = page_source[start_idx:start_idx+1000]
            print(snippet)
        else:
            print("✗ 'job-details-fit-level-preferences' NOT found in page")

            # Try to find any salary-like text
            import re
            salary_pattern = r'\$\d+[K,\d]*(?:/yr|/year)?(?:\s*-\s*\$\d+[K,\d]*(?:/yr|/year)?)?'
            matches = re.findall(salary_pattern, page_source)
            if matches:
                print(f"\nFound potential salary patterns in page source:")
                for match in set(matches):
                    print(f"  - {match}")

    except Exception as e:
        print(f"Error navigating to detail page: {e}")

finally:
    if driver:
        driver.quit()

print("\n\nDebug complete!")
