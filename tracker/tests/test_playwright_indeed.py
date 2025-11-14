"""
Test Indeed with Playwright - modern browser automation with better stealth.
"""
from playwright.sync_api import sync_playwright
import time

def test_indeed_with_playwright():
    print("="*80)
    print("Testing Indeed with Playwright")
    print("="*80 + "\n")

    with sync_playwright() as p:
        # Launch browser with stealth options
        print("Launching Chromium browser...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )

        # Additional stealth: Remove webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        # Test direct job URL
        job_url = "https://www.indeed.com/viewjob?jk=9a713e1032ca15cf"
        print(f"Loading job URL: {job_url}\n")

        try:
            page.goto(job_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)

            # Get page info
            title = page.title()
            url = page.url

            print(f"Page title: {title}")
            print(f"Current URL: {url}\n")

            # Check for blocking
            content = page.content()

            print("Checking for bot detection...")
            if "blocked" in title.lower():
                print("❌ BLOCKED: Page title contains 'blocked'")
                print("\nFirst 500 chars of page:")
                print(content[:500])
            elif "just a moment" in title.lower():
                print("❌ BLOCKED: Cloudflare Turnstile challenge")
            elif "additional verification" in content.lower():
                print("❌ BLOCKED: Additional verification required")
            elif "request blocked" in content.lower():
                print("❌ BLOCKED: Cloudflare WAF")
            else:
                print("✅ No obvious blocking detected!\n")

            # Try to extract salary
            print("="*80)
            print("Attempting to extract salary...")
            print("="*80 + "\n")

            try:
                # Try to find salary element
                salary_element = page.query_selector("#salaryInfoAndJobType")
                if salary_element:
                    salary_text = salary_element.inner_text()
                    print(f"✅ SUCCESS! Found salary:")
                    print(f"Salary: {salary_text}\n")
                    success = True
                else:
                    print("❌ Could not find salary element #salaryInfoAndJobType\n")
                    success = False
            except Exception as e:
                print(f"❌ Error extracting salary: {e}\n")
                success = False

            # Check keywords
            print("="*80)
            print("Keywords in page:")
            print("="*80)
            keywords = {
                "jobsearch": "jobsearch" in content.lower(),
                "salary": "salary" in content.lower(),
                "job description": "job description" in content.lower(),
                "apply": "apply" in content.lower(),
                "salaryInfoAndJobType": "salaryInfoAndJobType" in content,
            }
            for keyword, found in keywords.items():
                status = "✅" if found else "❌"
                print(f"{status} '{keyword}': {found}")

            # Save page for inspection
            with open('/tmp/indeed_playwright.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("\n📄 Page source saved to: /tmp/indeed_playwright.html")

            # Final result
            print("\n" + "="*80)
            if success:
                print("✅ SUCCESS! Playwright bypassed Indeed's blocking!")
            elif keywords['jobsearch'] or keywords['salaryInfoAndJobType']:
                print("✅ PARTIAL SUCCESS: Got to job page but salary not found")
            else:
                print("❌ FAILED: Still blocked by Indeed")
            print("="*80)

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()

    print("\nTest complete!")

if __name__ == "__main__":
    test_indeed_with_playwright()
