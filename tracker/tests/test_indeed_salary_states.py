"""
Test Indeed salary extraction in states with salary transparency laws.
States like CA, NY, CO, WA require salary disclosure in job postings.
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

# Test different locations
locations = ["New York, NY", "San Francisco, CA", "Denver, CO"]

for location in locations:
    print(f"\n{'='*80}")
    print(f"Testing location: {location}")
    print(f"{'='*80}\n")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Build search URL
        search_query = "software engineer"
        url = f"https://www.indeed.com/jobs?q={search_query}&l={location}&sort=date"

        print(f"URL: {url}\n")
        driver.get(url)

        time.sleep(3)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon")))

        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

        print(f"Found {len(job_cards)} job cards\n")

        # Check for salary in first 10 jobs
        jobs_with_salary = 0
        salary_examples = []

        for i, card in enumerate(job_cards[:10], 1):
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                title = title_elem.text.strip()

                # Try to find salary
                salary = None
                try:
                    salary_elem = card.find_element(By.CSS_SELECTOR,
                        "div.salary-snippet-container, div[data-testid='attribute_snippet_testid'], .salary-snippet")
                    salary = salary_elem.text.strip()
                    if salary and any(char.isdigit() for char in salary):
                        jobs_with_salary += 1
                        if len(salary_examples) < 3:
                            salary_examples.append((title[:50], salary))
                except:
                    pass

            except:
                continue

        print(f"Jobs with salary: {jobs_with_salary}/10")
        print(f"Percentage: {jobs_with_salary/10*100:.1f}%\n")

        if salary_examples:
            print("Examples:")
            for title, salary in salary_examples:
                print(f"  • {title}: {salary}")
        else:
            print("No salary data found on search results page")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()

print(f"\n{'='*80}")
print("Test complete!")
print(f"{'='*80}")
