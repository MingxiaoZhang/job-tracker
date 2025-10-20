"""
Indeed scraper using Selenium for browser automation.
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
from .base import BaseScraper

class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com using Selenium."""

    BASE_URL = "https://www.indeed.com/jobs"

    def scrape(self) -> List[Dict]:
        """Scrape job listings from Indeed using browser automation."""
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
            url = f"{self.BASE_URL}?q={self.search_query}&l={self.location}&sort=date"

            # Navigate to Indeed
            driver.get(url)

            # Random delay to mimic human behavior
            time.sleep(random.uniform(2, 4))

            # Wait for job cards to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon")))

            # Find all job cards
            job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

            print(f"Found {len(job_cards)} job cards on page")

            for card in job_cards[:20]:  # Limit to first 20 jobs for MVP
                try:
                    job_data = self._parse_job_card_selenium(card)
                    if job_data:
                        jobs.append(job_data)
                    time.sleep(random.uniform(0.2, 0.5))
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue

            print(f"Indeed: Successfully scraped {len(jobs)} jobs")

        except Exception as e:
            print(f"Error scraping Indeed with Selenium: {e}")

        finally:
            if driver:
                driver.quit()

        return jobs

    def _parse_job_card_selenium(self, card) -> Dict:
        """Parse individual job card using Selenium."""
        try:
            # Extract title
            title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
            title = title_elem.text.strip()

            # Extract company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
                company = company_elem.text.strip()
            except:
                company = "Unknown"

            # Extract location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']")
                location = location_elem.text.strip()
            except:
                location = None

            # Extract URL
            link_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
            job_url = link_elem.get_attribute('href')

            if not title or not job_url:
                return None

            return {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'posted_date': datetime.utcnow(),
                'board_source': 'indeed'
            }

        except Exception as e:
            print(f"Error extracting job details: {e}")
            return None
