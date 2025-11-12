#!/usr/bin/env python
"""
Migration script to normalize URLs in the database.
This removes tracking parameters from existing job URLs.
"""
import sys
sys.path.insert(0, '.')

from src.database.db import Database
from src.database.models import Job
from src.scrapers.base import BaseScraper

def migrate_urls():
    """Normalize all URLs in the database and remove duplicates."""
    db = Database('jobs.db')
    session = db.get_session()

    try:
        # Get all jobs ordered by most recent first
        jobs = session.query(Job).order_by(Job.first_seen.desc()).all()
        total = len(jobs)
        updated = 0
        deleted = 0

        print(f"Found {total} jobs in database")
        print("Normalizing URLs and removing duplicates...")

        # Track which normalized URLs we've seen
        seen_urls = {}

        for job in jobs:
            old_url = job.url
            normalized_url = BaseScraper.normalize_url(old_url)

            if normalized_url in seen_urls:
                # Duplicate - delete this older entry
                print(f"\nRemoving duplicate: {job.title} (ID: {job.id})")
                print(f"  Kept: ID {seen_urls[normalized_url]} (newer)")
                print(f"  Deleted: ID {job.id} (older)")
                session.delete(job)
                deleted += 1
            else:
                # First time seeing this normalized URL
                if old_url != normalized_url:
                    job.url = normalized_url
                    updated += 1

                    if updated <= 5:  # Show first 5 examples
                        print(f"\nUpdating job: {job.title}")
                        print(f"  Old: {old_url[:80]}...")
                        print(f"  New: {normalized_url}")

                # Mark this URL as seen
                seen_urls[normalized_url] = job.id

        # Commit changes
        session.commit()

        print(f"\n{'='*60}")
        print(f"Migration complete!")
        print(f"Total jobs before: {total}")
        print(f"URLs normalized: {updated}")
        print(f"Duplicates removed: {deleted}")
        print(f"Jobs remaining: {total - deleted}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_urls()
