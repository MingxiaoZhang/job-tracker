"""
Base scraper class that all job board scrapers inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    """Abstract base class for job board scrapers."""

    def __init__(self, search_query: str, location: str):
        self.search_query = search_query
        self.location = location

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape job listings from the job board.

        Returns:
            List of job dictionaries with keys: title, company, location, url, posted_date
        """
        pass
