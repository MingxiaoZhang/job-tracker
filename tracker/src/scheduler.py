"""
Scheduler for running the job tracker at regular intervals.
"""
import sys
import os
import schedule
import time
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import SCRAPE_INTERVAL_HOURS
from src.main import run_scraper

def job():
    """Wrapper function that runs the scraper and handles errors."""
    try:
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scrape...")
        print(f"{'='*60}\n")

        run_scraper()

        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scrape completed successfully")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR during scrape: {e}")
        print(f"{'='*60}\n")

def main():
    """Main scheduler entry point."""
    print(f"\n{'='*60}")
    print("Job Tracker Scheduler - Starting...")
    print(f"Will run every {SCRAPE_INTERVAL_HOURS} hours")
    print(f"{'='*60}\n")

    # Schedule the job
    schedule.every(SCRAPE_INTERVAL_HOURS).hours.do(job)

    # Run once immediately on startup
    print("Running initial scrape...")
    job()

    # Then run on schedule
    print(f"\nScheduler running. Next run in {SCRAPE_INTERVAL_HOURS} hours...")
    print("Press Ctrl+C to stop\n")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")
        sys.exit(0)
