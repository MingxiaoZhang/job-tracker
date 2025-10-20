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

            for card in job_cards[:20]:  # Limit to first 20 jobs for MVP
                try:
                    job_data = self._parse_job_card_selenium(card)
                    if job_data:
                        jobs.append(job_data)
                    time.sleep(random.uniform(0.2, 0.5))
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue

            print(f"LinkedIn: Successfully scraped {len(jobs)} jobs")

        except Exception as e:
            print(f"Error scraping LinkedIn with Selenium: {e}")

        finally:
            if driver:
                driver.quit()

        return jobs

    def _parse_job_card_selenium(self, card) -> Dict:
        """Parse individual job card using Selenium."""
        try:
            # Extract title
            title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
            title = title_elem.text.strip()

            # Extract company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
                company = company_elem.text.strip()
            except:
                company = "Unknown"

            # Extract location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                location = location_elem.text.strip()
            except:
                location = None

            # Extract URL
            link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            job_url = link_elem.get_attribute('href')

            if not title or not job_url:
                return None

            return {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'posted_date': datetime.utcnow(),
                'board_source': 'linkedin'
            }

        except Exception as e:
            print(f"Error extracting job details: {e}")
            return None
