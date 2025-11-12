"""
Main entry point for the Job Board Tracker application.
"""
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    DATABASE_PATH, SEARCH_QUERY, LOCATION
)
from src.database.factory import get_database
from src.scrapers.indeed_scraper import IndeedScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.tracker.monitor import JobMonitor
from src.cli.commands import CLI

def run_scraper():
    """Run the job scraper."""
    print("=" * 60)
    print("Job Board Tracker - Starting...")
    print("=" * 60)

    # Initialize database
    print(f"\nInitializing database...")
    db = get_database()
    db.create_tables()
    print("✓ Database initialized")

    # Initialize monitor
    monitor = JobMonitor(db)

    # Initialize scrapers
    print(f"\nSearch Query: '{SEARCH_QUERY}'")
    print(f"Location: '{LOCATION}'")
    print("\nScraping job boards...")

    all_new_jobs = []
    total_scraped = 0
    total_new = 0
    total_seen_again = 0

    # Scrape Indeed
    print("\n[1/2] Scraping Indeed...")
    indeed_scraper = IndeedScraper(SEARCH_QUERY, LOCATION)
    indeed_jobs = indeed_scraper.scrape()

    # Process Indeed jobs
    print(f"Processing {len(indeed_jobs)} jobs from Indeed...")
    indeed_results = monitor.process_jobs(indeed_jobs, 'indeed')
    all_new_jobs.extend(indeed_results['new'])
    total_scraped += indeed_results['total_processed']
    total_new += indeed_results['new_count']
    total_seen_again += indeed_results['seen_again_count']

    # Scrape LinkedIn
    print("\n[2/2] Scraping LinkedIn...")
    linkedin_scraper = LinkedInScraper(SEARCH_QUERY, LOCATION)
    linkedin_jobs = linkedin_scraper.scrape()

    # Process LinkedIn jobs
    print(f"Processing {len(linkedin_jobs)} jobs from LinkedIn...")
    linkedin_results = monitor.process_jobs(linkedin_jobs, 'linkedin')
    all_new_jobs.extend(linkedin_results['new'])
    total_scraped += linkedin_results['total_processed']
    total_new += linkedin_results['new_count']
    total_seen_again += linkedin_results['seen_again_count']

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total jobs scraped: {total_scraped}")
    print(f"New jobs found: {total_new}")
    print(f"Previously seen: {total_seen_again}")

    # Show new jobs
    if total_new > 0:
        print("\n--- NEW JOBS ---")
        for job in all_new_jobs:
            print(f"\n• {job.title}")
            print(f"  Company: {job.company}")
            print(f"  Location: {job.location or 'N/A'}")
            print(f"  Source: {job.board_source}")
            print(f"  URL: {job.url}")

    print("\n" + "=" * 60)
    print("Tracking complete!")
    print("=" * 60)

def main():
    """Main application entry point."""
    # Check if CLI command was provided
    if len(sys.argv) > 1 and sys.argv[1] in ['list', 'search', 'stats']:
        # CLI mode
        db = get_database()
        db.create_tables()
        monitor = JobMonitor(db)
        cli = CLI(db, monitor)
        cli.run()
    else:
        # Scraper mode (default)
        run_scraper()

if __name__ == "__main__":
    main()
