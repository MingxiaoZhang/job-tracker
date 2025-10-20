"""
CLI commands for interacting with the job tracker.
"""
import argparse
from datetime import datetime, timedelta

class CLI:
    """Command-line interface handler."""

    def __init__(self, database, monitor):
        self.db = database
        self.monitor = monitor

    def run(self):
        """Run the CLI."""
        parser = argparse.ArgumentParser(description='Job Board Tracker')
        parser.add_argument('command', choices=['list', 'search', 'stats'],
                          help='Command to execute')
        parser.add_argument('--keyword', help='Keyword to search for')
        parser.add_argument('--days', type=int, default=7, help='Number of days to look back')

        args = parser.parse_args()

        if args.command == 'list':
            self.list_jobs(args.days)
        elif args.command == 'search':
            if not args.keyword:
                print("Error: --keyword is required for search command")
                return
            self.search_jobs(args.keyword)
        elif args.command == 'stats':
            self.show_stats()

    def list_jobs(self, days: int):
        """List recent jobs."""
        jobs = self.monitor.get_recent_jobs(days=days)

        print(f"\n{'='*80}")
        print(f"JOBS FROM LAST {days} DAYS: {len(jobs)} total")
        print(f"{'='*80}\n")

        if not jobs:
            print("No jobs found in this time period.")
            return

        for i, job in enumerate(jobs, 1):
            # Calculate how long ago the job was found
            time_ago = datetime.utcnow() - job.first_seen
            if time_ago.days > 0:
                time_str = f"{time_ago.days} day{'s' if time_ago.days > 1 else ''} ago"
            else:
                hours = time_ago.seconds // 3600
                time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"

            print(f"{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location or 'N/A'}")
            print(f"   Source: {job.board_source}")
            print(f"   Found: {time_str}")
            print(f"   URL: {job.url}")
            print()

    def search_jobs(self, keyword: str):
        """Search for jobs by keyword."""
        jobs = self.db.search_jobs(keyword)

        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS FOR '{keyword}': {len(jobs)} matches")
        print(f"{'='*80}\n")

        if not jobs:
            print("No jobs found matching your search.")
            return

        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location or 'N/A'}")
            print(f"   Source: {job.board_source}")
            print(f"   First Seen: {job.first_seen.strftime('%Y-%m-%d %H:%M')}")
            print(f"   URL: {job.url}")
            print()

    def show_stats(self):
        """Show tracking statistics."""
        # Get all jobs
        all_jobs = self.db.get_jobs_by_status('active')

        # Get jobs by time period
        today = self.db.get_recent_jobs(days=1)
        this_week = self.db.get_recent_jobs(days=7)
        this_month = self.db.get_recent_jobs(days=30)

        # Get stats by source
        source_stats = self.db.get_job_count_by_source()

        print(f"\n{'='*80}")
        print("JOB TRACKER STATISTICS")
        print(f"{'='*80}\n")

        print("📊 OVERVIEW")
        print(f"   Total jobs tracked: {len(all_jobs)}")
        print(f"   Jobs found today: {len(today)}")
        print(f"   Jobs this week: {len(this_week)}")
        print(f"   Jobs this month: {len(this_month)}")
        print()

        print("📈 BY SOURCE")
        for source, stats in source_stats.items():
            total = sum(stats.values())
            print(f"   {source.capitalize()}: {total} jobs")
            for status, count in stats.items():
                print(f"      - {status}: {count}")
        print()

        # Top companies
        company_counts = {}
        for job in all_jobs:
            company_counts[job.company] = company_counts.get(job.company, 0) + 1

        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        if top_companies:
            print("🏢 TOP COMPANIES")
            for company, count in top_companies:
                print(f"   {company}: {count} job{'s' if count > 1 else ''}")
            print()

        print(f"{'='*80}\n")
