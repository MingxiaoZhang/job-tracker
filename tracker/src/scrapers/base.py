"""
Base scraper class that all job board scrapers inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from urllib.parse import urlparse, parse_qs

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
