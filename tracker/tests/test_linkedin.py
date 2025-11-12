#!/usr/bin/env python
"""
Test script to inspect LinkedIn page structure and validate selectors.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_linkedin_selectors():
    """Test LinkedIn selectors and show actual HTML structure."""

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to LinkedIn jobs search
        search_query = "software engineer"
        location = "Remote"
        url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location={location}&f_TPR=r604800&sortBy=DD"

        print(f"Navigating to: {url}")
        driver.get(url)

        time.sleep(3)

        # Save page source for inspection
        with open('/tmp/linkedin_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("\nPage source saved to /tmp/linkedin_page.html")

        # Try to find job cards with different selectors
        print("\n" + "="*60)
        print("TESTING DIFFERENT SELECTORS:")
        print("="*60)

        selectors_to_test = [
            ("base-card", By.CLASS_NAME),
            ("base-search-card", By.CLASS_NAME),
            ("job-search-card", By.CLASS_NAME),
            ("jobs-search__results-list", By.CLASS_NAME),
            ("li.jobs-search-results__list-item", By.CSS_SELECTOR),
            ("div.base-card", By.CSS_SELECTOR),
            ("div.job-search-card", By.CSS_SELECTOR),
        ]

        for selector, by_type in selectors_to_test:
            try:
                elements = driver.find_elements(by_type, selector)
                print(f"\n✓ Found {len(elements)} elements with: {selector}")

                if elements and len(elements) > 0:
                    print(f"  First element HTML preview:")
                    print(f"  {elements[0].get_attribute('outerHTML')[:200]}...")
            except Exception as e:
                print(f"\n✗ Error with selector '{selector}': {e}")

        # Try to find specific elements within the first card
        print("\n" + "="*60)
        print("TESTING ELEMENTS WITHIN FIRST JOB CARD:")
        print("="*60)

        # Try to get the first job card
        job_card = None
        for selector, by_type in selectors_to_test:
            try:
                elements = driver.find_elements(by_type, selector)
                if elements and len(elements) > 0:
                    job_card = elements[0]
                    print(f"\nUsing selector: {selector}")
                    break
            except:
                continue

        if job_card:
            # Test different title selectors
            title_selectors = [
                "h3.base-search-card__title",
                "h3",
                "a.base-card__full-link",
                "span.sr-only",
                "h3.job-search-card__title",
            ]

            print("\nTitle selectors:")
            for sel in title_selectors:
                try:
                    elem = job_card.find_element(By.CSS_SELECTOR, sel)
                    print(f"  ✓ {sel}: '{elem.text[:60]}...'")
                except Exception as e:
                    print(f"  ✗ {sel}: Not found")

            # Test company selectors
            company_selectors = [
                "h4.base-search-card__subtitle",
                "h4",
                "a.hidden-nested-link",
                "span.job-search-card__company-name",
            ]

            print("\nCompany selectors:")
            for sel in company_selectors:
                try:
                    elem = job_card.find_element(By.CSS_SELECTOR, sel)
                    print(f"  ✓ {sel}: '{elem.text[:60]}...'")
                except:
                    print(f"  ✗ {sel}: Not found")

            # Test location selectors
            location_selectors = [
                "span.job-search-card__location",
                "div.base-search-card__metadata",
                "span",
            ]

            print("\nLocation selectors:")
            for sel in location_selectors:
                try:
                    elems = job_card.find_elements(By.CSS_SELECTOR, sel)
                    if elems:
                        print(f"  ✓ {sel}: '{elems[0].text[:60]}...'")
                except:
                    print(f"  ✗ {sel}: Not found")

        else:
            print("\n⚠ Could not find any job cards to inspect!")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_linkedin_selectors()
