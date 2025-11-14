"""
Quick test script to verify LinkedIn salary extraction.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.linkedin_scraper import LinkedInScraper

def test_linkedin_salary():
    """Test LinkedIn scraper with salary extraction."""
    print("Testing LinkedIn Salary Extraction...")
    print("=" * 60)

    scraper = LinkedInScraper("software engineer", "Remote")

    # Scrape jobs (limited to first 3 for quick testing)
    jobs = scraper.scrape()

    print(f"\nScraped {len(jobs)} jobs\n")
    print("=" * 60)

    # Display results with focus on salary data
    for i, job in enumerate(jobs[:5], 1):  # Show first 5
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

if __name__ == "__main__":
    test_linkedin_salary()
