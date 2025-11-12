"""
Job monitoring and change detection logic.
"""
from typing import List, Dict
from datetime import datetime

class JobMonitor:
    """Monitors job listings and detects changes."""

    def __init__(self, database):
        self.db = database

    def process_jobs(self, jobs: List[Dict], source: str) -> Dict:
        """
        Process scraped jobs and identify new/updated/removed listings.

        Args:
            jobs: List of job dictionaries from scraper
            source: Job board source name

        Returns:
            Dictionary with 'new', 'updated', 'seen_again' job lists and counts
        """
        new_jobs = []
        seen_again = []

        for job_data in jobs:
            url = job_data.get('url')
            if not url:
                continue

            # Check if job already exists in database
            existing_job = self.db.get_job_by_url(url)

            if existing_job:
                # Job exists - already tracked
                seen_again.append(existing_job)
            else:
                # New job - add to database
                new_job = self.db.add_job(
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    url=url,
                    board_source=job_data.get('board_source', source),
                    location=job_data.get('location'),
                    posted_date=job_data.get('posted_date'),
                    job_type=job_data.get('job_type'),
                    work_mode=job_data.get('work_mode'),
                    experience_level=job_data.get('experience_level'),
                    description=job_data.get('description'),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    salary_currency=job_data.get('salary_currency', 'USD'),
                    salary_period=job_data.get('salary_period')
                )
                new_jobs.append(new_job)

        return {
            'new': new_jobs,
            'new_count': len(new_jobs),
            'seen_again': seen_again,
            'seen_again_count': len(seen_again),
            'total_processed': len(jobs)
        }

    def get_new_jobs(self, since: datetime = None) -> List:
        """Get jobs added since a specific time."""
        if since:
            return self.db.get_jobs_since(since)
        else:
            return self.db.get_recent_jobs(days=1)

    def get_recent_jobs(self, days: int = 7) -> List:
        """Get jobs from the last N days."""
        return self.db.get_recent_jobs(days=days)
