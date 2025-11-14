"""
LinkedIn job board scraper.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import List, Dict
from datetime import datetime
import time
import random
import re
from .base import BaseScraper

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn job listings."""

    BASE_URL = "https://www.linkedin.com/jobs/search"

    def scrape(self) -> List[Dict]:
        """Scrape job listings from LinkedIn using browser automation."""
        jobs = []

        # Set up Chrome options for headless browsing
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
            # f_TPR=r604800 filters to jobs posted in last 7 days
            # sortBy=DD sorts by date (most recent)
            url = f"{self.BASE_URL}?keywords={self.search_query}&location={self.location}&f_TPR=r604800&sortBy=DD"

            # Navigate to LinkedIn
            driver.get(url)

            # Random delay to mimic human behavior
            time.sleep(random.uniform(2, 4))

            # Wait for job cards to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "base-card")))

            # Find all job cards
            job_cards = driver.find_elements(By.CLASS_NAME, "base-card")

            print(f"Found {len(job_cards)} job cards on page")

            # First pass: Extract all basic info from job cards (while elements are fresh)
            job_basics = []
            for card in job_cards[:20]:  # Limit to first 20 jobs for MVP
                try:
                    basic_info = self._extract_basic_info_from_card(card)
                    if basic_info:
                        job_basics.append(basic_info)
                except Exception as e:
                    print(f"Error extracting basic info: {e}")
                    continue

            print(f"Extracted basic info for {len(job_basics)} jobs")

            # Second pass: Visit each job detail page for salary (avoids stale element issues)
            for i, basic_info in enumerate(job_basics, 1):
                try:
                    print(f"Processing job {i}/{len(job_basics)}: {basic_info['title'][:50]}...")
                    salary = self._extract_salary_from_detail_page(driver, basic_info['url'])

                    # Parse salary to extract min, max, and period
                    salary_min, salary_max, salary_period = self.parse_salary(salary) if salary else (None, None, None)

                    # Combine basic info with salary
                    job_data = {
                        **basic_info,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'salary_period': salary_period,
                        'posted_date': datetime.utcnow(),
                        'board_source': 'linkedin'
                    }
                    jobs.append(job_data)

                    time.sleep(random.uniform(0.5, 1.0))
                except Exception as e:
                    print(f"Error processing job: {e}")
                    continue

            print(f"LinkedIn: Successfully scraped {len(jobs)} jobs")

        except Exception as e:
            print(f"Error scraping LinkedIn with Selenium: {e}")

        finally:
            if driver:
                driver.quit()

        return jobs

    def _extract_basic_info_from_card(self, card) -> Dict:
        """Extract basic information from a job card (no navigation required)."""
        try:
            # Extract URL - get the full href
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                job_url = link_elem.get_attribute('href')
                if not job_url:
                    # Try alternative selector
                    link_elem = card.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                    job_url = link_elem.get_attribute('href')
            except Exception as e:
                return None

            # Extract title - use innerText as .text returns empty in headless mode
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
                title = (title_elem.get_attribute('innerText') or title_elem.text or "").strip()
            except:
                title = ""

            # Extract company - it's inside a nested link
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a.hidden-nested-link")
                company = (company_elem.get_attribute('innerText') or company_elem.text or "").strip()
                if not company:
                    # Fallback to h4 text
                    company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
                    company = (company_elem.get_attribute('innerText') or company_elem.text or "").strip()
            except:
                company = ""

            # Extract location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                location = (location_elem.get_attribute('innerText') or location_elem.text or "").strip()
                if not location:
                    location = None
            except:
                location = None

            if not title or not job_url:
                return None

            # Normalize URL to remove tracking parameters
            normalized_url = self.normalize_url(job_url, 'linkedin')

            return {
                'title': title,
                'company': company,
                'location': location,
                'url': normalized_url
            }

        except Exception as e:
            return None

    def _extract_salary_from_detail_page(self, driver, job_url: str) -> str:
        """Navigate to job detail page and extract salary information."""
        salary = None
        try:
            # Navigate to detail page
            driver.get(job_url)
            time.sleep(random.uniform(1.5, 2.5))  # Wait for page to load

            # Try to find compensation section first (most accurate)
            try:
                compensation_elem = driver.find_element(By.CSS_SELECTOR, "[class*='compensation']")
                compensation_text = (compensation_elem.get_attribute('innerText') or compensation_elem.text or "").strip()

                # Look for salary range in the compensation section
                salary_pattern = r'\$[\d,]+(?:\.\d+)?(?:/yr|/year)?\s*-\s*\$[\d,]+(?:\.\d+)?(?:/yr|/year)?'
                match = re.search(salary_pattern, compensation_text)
                if match:
                    salary = match.group(0)
                    # Clean up formatting
                    salary = salary.replace('.00', '').replace(',', '')
            except:
                pass

            # Fallback: try to find salary elements if not found yet
            if not salary:
                try:
                    salary_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='salary']")
                    for elem in salary_elements[:3]:  # Check first 3 to avoid similar jobs
                        text = (elem.get_attribute('innerText') or elem.text or "").strip()
                        # Look for salary pattern
                        if '$' in text and any(c.isdigit() for c in text):
                            # Check if it contains a range or single value
                            salary_pattern = r'\$[\d,]+(?:\.\d+)?(?:/yr|/year)?(?:\s*-\s*\$[\d,]+(?:\.\d+)?(?:/yr|/year)?)?'
                            match = re.search(salary_pattern, text)
                            if match:
                                salary = match.group(0)
                                salary = salary.replace('.00', '').replace(',', '')
                                break
                except:
                    pass

        except Exception as e:
            print(f"Error extracting salary: {e}")

        return salary
