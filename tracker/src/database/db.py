"""
Database connection and operations.
"""
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Optional
from .models import Base, Job

class Database:
    """Database connection manager."""

    def __init__(self, db_path: str = 'jobs.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    def add_job(self, title: str, company: str, url: str, board_source: str,
                location: str = None, posted_date: datetime = None,
                job_type: str = None, work_mode: str = None,
                experience_level: str = None, description: str = None,
                salary_min: int = None, salary_max: int = None,
                salary_currency: str = 'USD', salary_period: str = None) -> Job:
        """
        Add a new job to the database.

        Returns:
            The created Job object
        """
        session = self.get_session()
        try:
            job = Job(
                title=title,
                company=company,
                url=url,
                board_source=board_source,
                location=location,
                posted_date=posted_date,
                job_type=job_type,
                work_mode=work_mode,
                experience_level=experience_level,
                description=description,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                salary_period=salary_period
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        finally:
            session.close()

    def get_job_by_url(self, url: str) -> Optional[Job]:
        """Get a job by its URL."""
        session = self.get_session()
        try:
            return session.query(Job).filter(Job.url == url).first()
        finally:
            session.close()

    def get_jobs_by_status(self, status: str = 'active') -> List[Job]:
        """Get all jobs with a specific status."""
        session = self.get_session()
        try:
            return session.query(Job).filter(Job.status == status).all()
        finally:
            session.close()

    def get_jobs_since(self, since: datetime, status: str = 'active') -> List[Job]:
        """Get jobs added since a specific datetime."""
        session = self.get_session()
        try:
            return session.query(Job).filter(
                and_(Job.posted_date >= since, Job.status == status)
            ).order_by(Job.posted_date.desc()).all()
        finally:
            session.close()

    def get_recent_jobs(self, days: int = 7, status: str = 'active') -> List[Job]:
        """Get jobs from the last N days."""
        since = datetime.utcnow() - timedelta(days=days)
        return self.get_jobs_since(since, status)

    def mark_job_expired(self, job_id: int) -> bool:
        """Mark a job as expired."""
        session = self.get_session()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = 'expired'
                session.commit()
                return True
            return False
        finally:
            session.close()

    def search_jobs(self, keyword: str, status: str = 'active') -> List[Job]:
        """Search jobs by keyword in title or company."""
        session = self.get_session()
        try:
            search_pattern = f'%{keyword}%'
            return session.query(Job).filter(
                and_(
                    Job.status == status,
                    (Job.title.ilike(search_pattern) | Job.company.ilike(search_pattern))
                )
            ).all()
        finally:
            session.close()

    def get_job_count_by_source(self) -> dict:
        """Get count of jobs grouped by board source."""
        session = self.get_session()
        try:
            results = session.query(
                Job.board_source,
                Job.status,
                session.query(Job.id).filter(
                    and_(Job.board_source == Job.board_source, Job.status == Job.status)
                ).count()
            ).group_by(Job.board_source, Job.status).all()

            stats = {}
            for source, status, count in results:
                if source not in stats:
                    stats[source] = {}
                stats[source][status] = count
            return stats
        finally:
            session.close()
