"""
Test direct access to a specific Indeed job URL.
Testing: https://www.indeed.com/viewjob?jk=9a713e1032ca15cf
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

driver = None
try:
    print("="*80)
    print("Testing DIRECT access to Indeed job URL")
    print("="*80 + "\n")

    # Initialize undetected Chrome
    print("Initializing undetected Chrome driver...")
    options = uc.ChromeOptions()
    options.binary_location = "/home/michaelz524/.cache/selenium/chrome/linux64/142.0.7444.162/chrome"
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options, use_subprocess=False)

    # Navigate DIRECTLY to the specific job URL
    job_url = "https://www.indeed.com/viewjob?jk=9a713e1032ca15cf"
    print(f"Loading job URL directly: {job_url}\n")

    driver.get(job_url)
    time.sleep(5)  # Wait for page to load

    # Check what page we got
    page_title = driver.title
    current_url = driver.current_url
    page_source = driver.page_source

    print(f"Page title: {page_title}")
    print(f"Current URL: {current_url}\n")

    # Check for blocking
    print("Checking for bot detection...")
    if "blocked" in page_title.lower():
        print("❌ BLOCKED by Indeed's own protection!")
        print("\nFirst 500 chars of page:")
        print(page_source[:500])
    elif "just a moment" in page_title.lower():
        print("❌ Cloudflare Turnstile challenge detected!")
    elif "additional verification" in page_source.lower():
        print("❌ Additional verification required!")
    elif "request blocked" in page_source.lower():
        print("❌ Cloudflare WAF blocked the request!")
        print("\nChecking for block message...")
        if "PAGE_TYPE" in page_source and "waf_block" in page_source:
            print("Confirmed: WAF Block (PAGE_TYPE:waf_block)")
    else:
        print("✅ No obvious blocking detected!")

    # Try to extract salary
    print("\n" + "="*80)
    print("Attempting to extract salary from #salaryInfoAndJobType...")
    print("="*80 + "\n")

    try:
        salary_elem = driver.find_element(By.CSS_SELECTOR, "#salaryInfoAndJobType")
        salary_text = salary_elem.text
        print(f"✅ SUCCESS! Found salary element:")
        print(f"Salary: {salary_text}\n")
        success = True
    except Exception as e:
        print(f"❌ Could not find salary element: {str(e)[:100]}\n")
        success = False

    # Check for job-related keywords
    print("="*80)
    print("Keywords in page:")
    print("="*80)
    keywords = {
        "jobsearch": "jobsearch" in page_source.lower(),
        "salary": "salary" in page_source.lower(),
        "job description": "job description" in page_source.lower(),
        "apply": "apply" in page_source.lower(),
        "salaryInfoAndJobType": "salaryInfoAndJobType" in page_source,
    }
    for keyword, found in keywords.items():
        status = "✅" if found else "❌"
        print(f"{status} '{keyword}': {found}")

    # Save page for inspection
    with open('/tmp/indeed_direct_access.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("\n📄 Full page source saved to: /tmp/indeed_direct_access.html")

    # Final result
    print("\n" + "="*80)
    if success:
        print("✅ SUCCESS! Direct URL access works and salary was extracted!")
    elif keywords['jobsearch'] or keywords['salaryInfoAndJobType']:
        print("✅ PARTIAL SUCCESS: Got through to job page but salary element not found")
    else:
        print("❌ FAILED: Still blocked or page didn't load properly")
    print("="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    if driver:
        print("\nClosing browser...")
        driver.quit()

print("\nTest complete!")
