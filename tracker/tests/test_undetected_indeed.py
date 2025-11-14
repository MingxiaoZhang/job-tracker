"""
Test Indeed with undetected-chromedriver to bypass Cloudflare.
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = None
try:
    print("="*80)
    print("Testing Indeed with undetected-chromedriver")
    print("="*80 + "\n")

    # Initialize undetected Chrome
    # Point it to the Chrome binary that Selenium downloaded
    print("Initializing undetected Chrome driver...")
    print("Note: undetected-chromedriver patches Chrome to avoid detection\n")

    options = uc.ChromeOptions()
    options.binary_location = "/home/michaelz524/.cache/selenium/chrome/linux64/142.0.7444.162/chrome"
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options, use_subprocess=False)

    # Navigate to Indeed search
    search_url = "https://www.indeed.com/jobs?q=software+engineer&l=Remote&sort=date"
    print(f"Step 1: Loading search page...\n")
    driver.get(search_url)
    time.sleep(5)  # Wait longer

    # Check what page we got
    page_title = driver.title
    current_url = driver.current_url
    page_source = driver.page_source

    print(f"Page title: {page_title}")
    print(f"Current URL: {current_url}\n")

    # Check for blocks
    if "blocked" in page_title.lower():
        print("❌ BLOCKED by Indeed's own protection!")
        print("\nSaving blocked page source to /tmp/indeed_blocked.html")
        with open('/tmp/indeed_blocked.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("First 500 chars of page:")
        print(page_source[:500])
    elif "just a moment" in page_title.lower():
        print("❌ Cloudflare challenge detected on search page!")
    elif "additional verification" in page_source.lower():
        print("❌ Additional verification required on search page!")
    else:
        print("✅ No obvious blocking on search page")

    # Get first job
    job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
    print(f"\nFound {len(job_cards)} job cards")

    if job_cards:
        first_card = job_cards[0]
        title_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
        title = title_elem.text.strip()

        link_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
        job_url = link_elem.get_attribute('href')

        print(f"First job: {title}")
        print(f"Job URL: {job_url}\n")

        # Navigate to detail page
        print("="*80)
        print("Step 2: Navigating to job detail page...")
        print("="*80 + "\n")

        driver.get(job_url)
        time.sleep(5)  # Wait longer for Cloudflare challenge

        # Check what we got
        current_url = driver.current_url
        page_title = driver.title
        page_source = driver.page_source

        print(f"Current URL: {current_url}")
        print(f"Page Title: {page_title}\n")

        # Check for blocking
        print("Checking for bot detection...")
        if "additional verification required" in page_source.lower():
            print("❌ STILL BLOCKED: 'Additional Verification Required'")
        elif "just a moment" in page_title.lower():
            print("❌ STILL BLOCKED: Cloudflare challenge page")
        elif "captcha" in page_source.lower():
            print("❌ STILL BLOCKED: CAPTCHA detected")
        else:
            print("✅ No obvious blocking detected!")

        # Try to extract salary
        print("\n" + "="*80)
        print("Attempting to extract salary...")
        print("="*80 + "\n")

        try:
            salary_elem = driver.find_element(By.CSS_SELECTOR, "#salaryInfoAndJobType")
            salary_text = salary_elem.text
            print(f"✅ SUCCESS! Found salary:")
            print(f"Salary: {salary_text}\n")
            success = True
        except Exception as e:
            print(f"❌ Could not find salary element: {str(e)[:100]}\n")
            success = False

        # Check keywords
        print("="*80)
        print("Keywords in page:")
        print("="*80)
        keywords = {
            "jobsearch": "jobsearch" in page_source.lower(),
            "salary": "salary" in page_source.lower(),
            "job description": "job description" in page_source.lower(),
            "apply": "apply" in page_source.lower(),
        }
        for keyword, found in keywords.items():
            status = "✅" if found else "❌"
            print(f"{status} '{keyword}': {found}")

        # Final result
        print("\n" + "="*80)
        if success and keywords['jobsearch']:
            print("✅ SUCCESS! Undetected-chromedriver BYPASSED Cloudflare!")
            print("="*80)
        elif keywords['jobsearch']:
            print("✅ PARTIAL SUCCESS: Got through Cloudflare but salary not found")
            print("="*80)
        else:
            print("❌ FAILED: Still blocked by Cloudflare")
            print("="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    if driver:
        print("\nClosing browser...")
        driver.quit()

print("\nTest complete!")
