"""
Test job description extraction for both Indeed and LinkedIn scrapers.
"""
import sys
sys.path.insert(0, '/home/michaelz524/tracker/tracker/src')

from scrapers.indeed_scraper import IndeedScraper
from scrapers.linkedin_scraper import LinkedInScraper

print("="*80)
print("Testing Job Description Extraction")
print("="*80)

# Test Indeed (just 2 jobs to save time)
print("\n[1/2] Testing Indeed scraper...")
indeed = IndeedScraper(search_query="software engineer", location="Remote")
indeed_jobs = indeed.scrape()

if indeed_jobs:
    job = indeed_jobs[0]
    print(f"\nSample Indeed Job:")
    print(f"Title: {job.get('title', 'N/A')}")
    print(f"Company: {job.get('company', 'N/A')}")
    print(f"Salary: ${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')} {job.get('salary_period', '')}")
    if job.get('description'):
        desc = job['description']
        print(f"Description: {desc[:200]}..." if len(desc) > 200 else f"Description: {desc}")
        print(f"  ✓ Description extracted ({len(desc)} characters)")
    else:
        print(f"  ✗ No description found")

# Test LinkedIn (just 2 jobs)
print("\n[2/2] Testing LinkedIn scraper...")
linkedin = LinkedInScraper(search_query="software engineer", location="Remote")
linkedin_jobs = linkedin.scrape()

if linkedin_jobs:
    job = linkedin_jobs[0]
    print(f"\nSample LinkedIn Job:")
    print(f"Title: {job.get('title', 'N/A')}")
    print(f"Company: {job.get('company', 'N/A')}")
    print(f"Salary: ${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')} {job.get('salary_period', '')}")
    if job.get('description'):
        desc = job['description']
        print(f"Description: {desc[:200]}..." if len(desc) > 200 else f"Description: {desc}")
        print(f"  ✓ Description extracted ({len(desc)} characters)")
    else:
        print(f"  ✗ No description found")

print("\n" + "="*80)
print("✅ Test complete!")
print("="*80)
