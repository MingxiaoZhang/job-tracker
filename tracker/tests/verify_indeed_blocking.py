"""
Verify if Indeed is actually blocking us and what we're getting.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = None
try:
    driver = webdriver.Chrome(options=chrome_options)

    # First, get a job URL from search page
    search_url = "https://www.indeed.com/jobs?q=software+engineer&l=Remote&sort=date"
    print(f"Step 1: Loading search page...")
    print(f"URL: {search_url}\n")

    driver.get(search_url)
    time.sleep(3)

    # Get first job URL
    job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
    print(f"Found {len(job_cards)} job cards\n")

    if job_cards:
        first_card = job_cards[0]
        title_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
        title = title_elem.text.strip()

        link_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
        job_url = link_elem.get_attribute('href')

        print(f"First job: {title}")
        print(f"Job URL: {job_url}\n")

        # Now navigate to the detail page
        print("=" * 80)
        print("Step 2: Navigating to job detail page...")
        print("=" * 80 + "\n")

        driver.get(job_url)
        time.sleep(3)

        # Check what we got
        current_url = driver.current_url
        page_title = driver.title

        print(f"Current URL: {current_url}")
        print(f"Page Title: {page_title}\n")

        # Check for blocking indicators
        page_source = driver.page_source

        print("Checking for bot detection indicators...")
        if "additional verification required" in page_source.lower():
            print("❌ BLOCKED: 'Additional Verification Required' detected")
        elif "captcha" in page_source.lower():
            print("❌ BLOCKED: CAPTCHA detected")
        elif "access denied" in page_source.lower():
            print("❌ BLOCKED: 'Access Denied' detected")
        else:
            print("✅ No obvious blocking detected")

        # Try to find salary element
        print("\n" + "=" * 80)
        print("Attempting to extract salary...")
        print("=" * 80 + "\n")

        try:
            salary_elem = driver.find_element(By.CSS_SELECTOR, "#salaryInfoAndJobType")
            salary_text = salary_elem.text
            print(f"✅ SUCCESS! Found salary element:")
            print(f"Salary: {salary_text}\n")
        except Exception as e:
            print(f"❌ Could not find salary element: {e}\n")

        # Save page source to file for inspection
        with open('/tmp/indeed_detail_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Full page source saved to: /tmp/indeed_detail_page.html")

        # Print a snippet of the page
        print("\n" + "=" * 80)
        print("Page source snippet (first 1000 chars):")
        print("=" * 80)
        print(page_source[:1000])

        # Check for specific keywords that would indicate success
        print("\n" + "=" * 80)
        print("Keywords in page:")
        print("=" * 80)
        keywords = {
            "jobsearch": "jobsearch" in page_source.lower(),
            "salary": "salary" in page_source.lower(),
            "job description": "job description" in page_source.lower(),
            "apply": "apply" in page_source.lower(),
        }
        for keyword, found in keywords.items():
            status = "✅" if found else "❌"
            print(f"{status} '{keyword}': {found}")

finally:
    if driver:
        driver.quit()

print("\n" + "=" * 80)
print("Verification complete!")
print("=" * 80)
