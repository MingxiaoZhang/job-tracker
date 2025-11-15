"""
Quick test to verify job description extraction works.
Tests just one job from each scraper.
"""
import sys
sys.path.insert(0, '/home/michaelz524/tracker/tracker/src')

from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.indeed_scraper import IndeedScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
import time

print("="*80)
print("Quick Description Extraction Test")
print("="*80)

# Test 1: LinkedIn
print("\n[1/2] Testing LinkedIn description extraction...")
try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    # Use a known LinkedIn job URL
    test_url = "https://www.linkedin.com/jobs/view/4323948499"
    scraper = LinkedInScraper("software engineer", "Remote")

    salary, description = scraper._extract_salary_and_description_from_detail_page(driver, test_url)

    driver.quit()

    print(f"✓ Method executed successfully")
    print(f"  Salary: {salary if salary else 'None'}")
    print(f"  Description length: {len(description) if description else 0} characters")
    if description:
        print(f"  Description preview: {description[:150]}...")
        print("  ✅ LinkedIn description extraction WORKING")
    else:
        print("  ⚠️  No description found (might be due to page structure)")

except Exception as e:
    print(f"❌ LinkedIn test failed: {e}")

# Test 2: Indeed
print("\n[2/2] Testing Indeed description extraction...")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        page = context.new_page()

        # Test with a known Indeed job
        test_url = "https://www.indeed.com/viewjob?jk=9a713e1032ca15cf"
        page.goto(test_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)

        scraper = IndeedScraper("software engineer", "Remote")
        salary, description = scraper._extract_salary_and_description_from_page(page)

        browser.close()

        print(f"✓ Method executed successfully")
        print(f"  Salary: {salary if salary else 'None'}")
        print(f"  Description length: {len(description) if description else 0} characters")
        if description:
            print(f"  Description preview: {description[:150]}...")
            print("  ✅ Indeed description extraction WORKING")
        else:
            print("  ⚠️  No description found (might be blocked or different structure)")

except Exception as e:
    print(f"❌ Indeed test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Test Complete!")
print("="*80)
