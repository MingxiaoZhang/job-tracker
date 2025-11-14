"""
Base scraper class that all job board scrapers inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, parse_qs
import re

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

    @staticmethod
    def normalize_url(url: str, source: str = None) -> str:
        """
        Normalize job URLs by extracting stable job identifiers.
        Removes tracking parameters that change between requests.

        Args:
            url: The full job URL
            source: The job board source (indeed, linkedin, etc.)

        Returns:
            Normalized URL with only stable identifiers
        """
        if not url:
            return url

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # For Indeed: use the 'jk' parameter (job key) as the unique identifier
        if 'indeed.com' in parsed.netloc:
            if 'jk' in params:
                job_key = params['jk'][0]
                return f"https://www.indeed.com/viewjob?jk={job_key}"

        # For LinkedIn: extract job ID from URL path or params
        elif 'linkedin.com' in parsed.netloc:
            # LinkedIn URLs look like /jobs/view/software-engineer-at-company-4296417197
            # The job ID is the numeric part at the end before any query params
            if '/jobs/view/' in parsed.path:
                path_part = parsed.path.split('/jobs/view/')[-1].split('?')[0]
                # Extract the numeric job ID (last segment after the last hyphen)
                parts = path_part.split('-')
                # Find the last numeric part
                job_id = None
                for part in reversed(parts):
                    if part.isdigit():
                        job_id = part
                        break
                if job_id:
                    return f"https://www.linkedin.com/jobs/view/{job_id}"

        # Default: return original URL
        return url

    @staticmethod
    def parse_salary(salary_str: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Parse salary string and extract min, max, and period.

        Examples:
            "$100,000 - $150,000 a year" -> (100000, 150000, 'yearly')
            "$50 - $60 an hour" -> (50, 60, 'hourly')
            "$120,000 a year" -> (120000, 120000, 'yearly')
            "$45 an hour" -> (45, 45, 'hourly')

        Args:
            salary_str: Raw salary string

        Returns:
            Tuple of (salary_min, salary_max, salary_period)
        """
        if not salary_str:
            return (None, None, None)

        # Extract all dollar amounts
        amounts = re.findall(r'\$[\d,]+(?:\.\d+)?', salary_str)
        if not amounts:
            return (None, None, None)

        # Clean and convert to integers
        cleaned_amounts = []
        for amount in amounts:
            cleaned = amount.replace('$', '').replace(',', '')
            # Remove decimals for salary (e.g., $100,000.00 -> 100000)
            cleaned = cleaned.split('.')[0]
            try:
                cleaned_amounts.append(int(cleaned))
            except ValueError:
                continue

        if not cleaned_amounts:
            return (None, None, None)

        # Determine min and max
        if len(cleaned_amounts) == 1:
            salary_min = salary_max = cleaned_amounts[0]
        else:
            salary_min = min(cleaned_amounts)
            salary_max = max(cleaned_amounts)

        # Determine period
        salary_lower = salary_str.lower()
        if 'year' in salary_lower:
            period = 'yearly'
        elif 'hour' in salary_lower:
            period = 'hourly'
        elif 'month' in salary_lower:
            period = 'monthly'
        elif 'week' in salary_lower:
            period = 'weekly'
        else:
            period = 'yearly'  # Default assumption

        return (salary_min, salary_max, period)
