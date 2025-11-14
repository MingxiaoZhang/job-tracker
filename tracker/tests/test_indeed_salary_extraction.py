"""
Test script to verify Indeed salary extraction.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.indeed_scraper import IndeedScraper

def test_indeed_salary():
    """Test Indeed scraper with salary extraction."""
    print("Testing Indeed Salary Extraction...")
    print("=" * 60)
    print("Note: Indeed has strict bot detection, so results may vary")
    print("=" * 60)

    scraper = IndeedScraper("software engineer", "Remote")

    # Scrape jobs (limited to first 5 for quick testing to avoid bot detection)
    jobs = scraper.scrape()

    print(f"\nScraped {len(jobs)} jobs\n")
    print("=" * 60)

    # Display results with focus on salary data
    for i, job in enumerate(jobs[:10], 1):  # Show first 10
        print(f"\nJob #{i}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Salary: {job['salary'] or 'Not available'}")
        print(f"URL: {job['url'][:80]}...")
        print("-" * 60)

    # Summary
    jobs_with_salary = sum(1 for job in jobs if job['salary'])
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total jobs scraped: {len(jobs)}")
    print(f"Jobs with salary data: {jobs_with_salary}")
    print(f"Percentage with salary: {jobs_with_salary/len(jobs)*100:.1f}%" if jobs else "N/A")

    if jobs_with_salary == 0:
        print("\n⚠ Note: Indeed likely triggered bot detection.")
        print("This is expected behavior - Indeed has stricter anti-bot measures than LinkedIn.")

if __name__ == "__main__":
    test_indeed_salary()
