"""
Indeed scraper using Playwright for browser automation.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List, Dict
from datetime import datetime
import time
import random
import re
from .base import BaseScraper

class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com using Playwright."""

    BASE_URL = "https://www.indeed.com/jobs"

    def scrape(self) -> List[Dict]:
        """Scrape job listings from Indeed using Playwright browser automation."""
        jobs = []
        job_basics = []

        # Step 1: Get all job URLs from search page
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )

                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                )

                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                page = context.new_page()

                # Build search URL
                url = f"{self.BASE_URL}?q={self.search_query}&l={self.location}&sort=date"

                # Navigate to Indeed search page
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(random.uniform(3, 5))

                # Wait for job cards to load
                page.wait_for_selector(".job_seen_beacon", timeout=15000)

                # Find all job cards
                job_cards = page.query_selector_all(".job_seen_beacon")
                print(f"Found {len(job_cards)} job cards on page")

                # Extract all basic info from job cards
                for card in job_cards[:20]:  # Limit to first 20 jobs
                    try:
                        basic_info = self._extract_basic_info_from_card(card)
                        if basic_info:
                            job_basics.append(basic_info)
                    except Exception as e:
                        print(f"Error extracting basic info: {e}")
                        continue

                print(f"Extracted basic info for {len(job_basics)} jobs")

                # IMPORTANT: Close browser completely before visiting job details
                browser.close()

            except Exception as e:
                print(f"Error getting job URLs from Indeed: {e}")
                return jobs

        # Step 2: Visit each job URL independently with a fresh browser
        # This makes each visit look like a standalone page visit (not scraping pattern)
        for i, basic_info in enumerate(job_basics, 1):
            print(f"Processing job {i}/{len(job_basics)}: {basic_info['title'][:50]}...")

            salary = self._extract_salary_standalone(basic_info['url'])

            # Parse salary to extract min, max, and period
            salary_min, salary_max, salary_period = self.parse_salary(salary) if salary else (None, None, None)

            # Combine basic info with salary
            job_data = {
                **basic_info,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_period': salary_period,
                'posted_date': datetime.utcnow(),
                'board_source': 'indeed'
            }
            jobs.append(job_data)

            # Random delay between independent visits
            time.sleep(random.uniform(3.0, 6.0))

        print(f"Indeed: Successfully scraped {len(jobs)} jobs")
        return jobs

    def _extract_basic_info_from_card(self, card) -> Dict:
        """Extract basic information from a job card (no navigation required)."""
        try:
            # Extract title
            title_elem = card.query_selector("h2.jobTitle")
            title = title_elem.inner_text().strip() if title_elem else None

            # Extract company
            company_elem = card.query_selector("span[data-testid='company-name']")
            company = company_elem.inner_text().strip() if company_elem else "Unknown"

            # Extract location
            location_elem = card.query_selector("div[data-testid='text-location']")
            location = location_elem.inner_text().strip() if location_elem else None

            # Extract URL
            link_elem = card.query_selector("h2.jobTitle a")
            job_url = link_elem.get_attribute('href') if link_elem else None

            if not title or not job_url:
                return None

            # Convert relative URL to absolute URL
            if job_url.startswith('/'):
                job_url = f"https://www.indeed.com{job_url}"

            # Normalize URL to remove tracking parameters
            normalized_url = self.normalize_url(job_url, 'indeed')

            return {
                'title': title,
                'company': company,
                'location': location,
                'url': normalized_url
            }

        except Exception as e:
            return None

    def _extract_salary_standalone(self, job_url: str) -> str:
        """
        Visit a job URL with a completely fresh browser instance.
        This makes each visit appear independent (not part of a scraping session).
        """
        salary = None

        with sync_playwright() as p:
            try:
                # Fresh browser for this single job
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )

                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                )

                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                page = context.new_page()

                # Navigate directly to this job (like a user clicking a link)
                page.goto(job_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(random.uniform(2.5, 4.0))

                # Check if blocked
                page_content = page.content().lower()
                if "blocked" in page.title().lower() or "additional verification" in page_content:
                    print("  ⚠ Bot detection triggered")
                    browser.close()
                    return None

                # Extract salary
                salary = self._extract_salary_from_page(page)

                browser.close()

            except Exception as e:
                print(f"  Error: {str(e)[:50]}")

        return salary

    def _extract_salary_from_page(self, page) -> str:
        """Extract salary from an already-loaded page."""
        try:
            # Try to find salary using the ID selector
            salary_container = page.query_selector("#salaryInfoAndJobType")
            if salary_container:
                salary_text = salary_container.inner_text().strip()
                lines = salary_text.split('\n')
                if lines:
                    salary_line = lines[0].strip()
                    salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s+(?:a|an)\s+(?:year|hour|month|week))?'
                    match = re.search(salary_pattern, salary_line)
                    if match:
                        salary = match.group(0)
                        print(f"  ✓ Found salary: {salary}")
                        return salary

            # Fallback: Try alternative selectors
            salary_selectors = [
                "span.css-1oc7tea",
                "[data-testid='jobsearch-JobMetadataHeader-salary']",
                "div.jobsearch-JobMetadataHeader-item",
            ]

            for selector in salary_selectors:
                elements = page.query_selector_all(selector)
                for elem in elements:
                    text = elem.inner_text().strip()
                    if '$' in text or 'year' in text.lower() or 'hour' in text.lower():
                        salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s+(?:a|an)\s+(?:year|hour|month|week))?'
                        match = re.search(salary_pattern, text)
                        if match:
                            salary = match.group(0)
                            print(f"  ✓ Found salary: {salary}")
                            return salary

        except Exception as e:
            pass

        return None

    def _extract_salary_from_detail_page(self, page, job_url: str) -> str:
        """Navigate to job detail page and extract salary information."""
        salary = None
        try:
            # Navigate to detail page - use 'domcontentloaded' for reliability
            page.goto(job_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(random.uniform(2.5, 4.0))  # Longer wait for Indeed

            # Check if we got blocked
            page_content = page.content().lower()
            if "blocked" in page.title().lower() or "additional verification" in page_content:
                print("  ⚠ Bot detection triggered, skipping salary extraction")
                return None

            # Try to find salary using the ID selector from the user's example
            salary_container = page.query_selector("#salaryInfoAndJobType")
            if salary_container:
                salary_text = salary_container.inner_text().strip()

                # Extract just the salary part (first line usually)
                lines = salary_text.split('\n')
                if lines:
                    salary_line = lines[0].strip()
                    # Clean up the salary text - more flexible pattern
                    salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s+(?:a|an)\s+(?:year|hour|month|week))?'
                    match = re.search(salary_pattern, salary_line)
                    if match:
                        salary = match.group(0)
                        print(f"  ✓ Found salary: {salary}")
                        return salary

            # Fallback: Try alternative selectors
            salary_selectors = [
                "span.css-1oc7tea",
                "[data-testid='jobsearch-JobMetadataHeader-salary']",
                "div.jobsearch-JobMetadataHeader-item",
            ]

            for selector in salary_selectors:
                elements = page.query_selector_all(selector)
                for elem in elements:
                    text = elem.inner_text().strip()
                    if '$' in text or 'year' in text.lower() or 'hour' in text.lower():
                        salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s+(?:a|an)\s+(?:year|hour|month|week))?'
                        match = re.search(salary_pattern, text)
                        if match:
                            salary = match.group(0)
                            print(f"  ✓ Found salary: {salary}")
                            return salary

        except Exception as e:
            print(f"  Error extracting salary: {e}")

        return salary
