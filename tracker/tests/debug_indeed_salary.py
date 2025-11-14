"""
Debug script to inspect Indeed job cards and test salary extraction.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

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
    url = f"https://www.indeed.com/jobs?q={search_query}&l={location}&sort=date"

    print(f"Navigating to: {url}\n")
    driver.get(url)

    # Wait for job cards to load
    time.sleep(3)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon")))

    # Find all job cards
    job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

    print(f"Found {len(job_cards)} job cards\n")
    print("=" * 80)

    # Inspect first 5 job cards in detail
    for i, card in enumerate(job_cards[:5], 1):
        print(f"\n{'='*80}")
        print(f"JOB CARD #{i}")
        print(f"{'='*80}\n")

        # Extract basic info
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
            title = title_elem.text
            print(f"Title: {title}")
        except:
            print("Title: NOT FOUND")

        try:
            company_elem = card.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
            company = company_elem.text
            print(f"Company: {company}")
        except:
            print("Company: NOT FOUND")

        try:
            location_elem = card.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']")
            location = location_elem.text
            print(f"Location: {location}")
        except:
            print("Location: NOT FOUND")

        # Try to find salary using various selectors
        print("\n--- Testing salary selectors ---")

        salary_selectors = [
            "div.salary-snippet-container",
            "div[data-testid='attribute_snippet_testid']",
            ".salary-snippet",
            "div.metadata.salary-snippet-container",
            "[class*='salary']",
            "[data-testid*='salary']",
            "div.metadata",
        ]

        found_salary = False
        for selector in salary_selectors:
            try:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        text = elem.text.strip()
                        if text and ('$' in text or any(c.isdigit() for c in text)):
                            print(f"\nSelector: '{selector}'")
                            print(f"  Text: '{text}'")
                            print(f"  Class: {elem.get_attribute('class')}")
                            print(f"  ✓ Potential salary data!")
                            found_salary = True
                            break
                    if found_salary:
                        break
            except Exception as e:
                pass

        if not found_salary:
            print("\n✗ No salary information found for this job")

        # Get card HTML snippet
        print("\n--- Card HTML Snippet (first 800 chars) ---")
        card_html = card.get_attribute('outerHTML')
        print(card_html[:800])

        print("\n" + "=" * 80)

    # Test navigating to a job detail page to check for salary there
    print("\n\n" + "=" * 80)
    print("Testing salary extraction from JOB DETAIL PAGE")
    print("=" * 80 + "\n")

    try:
        # Get first job URL and navigate to it
        first_card = job_cards[0]
        link_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
        job_url = link_elem.get_attribute('href')

        print(f"Navigating to job detail page: {job_url}\n")
        driver.get(job_url)

        # Wait for detail page to load
        time.sleep(3)

        # Wait for page to fully load
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass

        # Extract title from detail page - try multiple selectors
        title = None
        title_selectors = [
            "h1.jobsearch-JobInfoHeader-title",
            "h1[class*='jobsearch']",
            "h1",
            "[data-testid='jobsearch-JobInfoHeader-title']"
        ]

        for selector in title_selectors:
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text
                if title:
                    print(f"Job Title: {title}")
                    break
            except:
                continue

        if not title:
            print("Could not extract title")
            # Print current URL to debug
            print(f"Current URL: {driver.current_url}")
            # Check if we got redirected or blocked
            if "indeed.com/jobs" not in driver.current_url and "indeed.com/viewjob" not in driver.current_url:
                print("⚠ Page may have been blocked or redirected")

        # Try to extract salary using various selectors
        print("\n--- Testing salary selectors on detail page ---\n")

        salary_selectors = [
            "#salaryInfoAndJobType",
            "div#salaryGuide",
            "[data-testid='jobsearch-JobMetadataHeader-salary']",
            "div.jobsearch-JobMetadataHeader-item",
            "span.css-19j1a75",
            "[class*='salary']",
            "[class*='compensation']",
            "[id*='salary']",
        ]

        found_salary_on_detail = False
        for selector in salary_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Selector: '{selector}'")
                    print(f"Found {len(elements)} elements:")
                    for elem in elements:
                        text = elem.text.strip()
                        if text:
                            print(f"  Text: '{text}'")
                            # Check if it looks like salary (contains $ and numbers)
                            if '$' in text or 'year' in text.lower() or 'hour' in text.lower():
                                print(f"  ✓ Potential salary data!")
                                found_salary_on_detail = True
                    print()
            except Exception as e:
                pass

        if not found_salary_on_detail:
            print("✗ No salary information found on detail page either")

        # Try to find salary in page source using regex
        print("\n--- Searching page source for salary patterns ---")
        page_source = driver.page_source
        import re

        # Various salary patterns
        patterns = [
            r'\$[\d,]+(?:\.\d+)?(?:\s*(?:-|to)\s*\$[\d,]+(?:\.\d+)?)?(?:\s+(?:a|an|per)\s+(?:year|hour|month|week))?',
            r'[\d,]+K?\s*(?:-|to)\s*[\d,]+K?\s+(?:a|an|per)\s+(?:year|hour)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"\nPattern '{pattern}' found matches:")
                unique_matches = list(set(matches))[:10]  # Show first 10 unique
                for match in unique_matches:
                    print(f"  - {match}")

    except Exception as e:
        print(f"Error navigating to detail page: {e}")

finally:
    if driver:
        driver.quit()

print("\n\nDebug complete!")
