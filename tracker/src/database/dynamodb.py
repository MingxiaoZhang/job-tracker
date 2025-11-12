"""
DynamoDB database implementation for AWS deployment.
"""
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute, BooleanAttribute
from datetime import datetime, timedelta
from typing import List, Optional
import os


class JobModel(Model):
    """DynamoDB Job model."""
    class Meta:
        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'job-tracker-jobs')
        region = os.getenv('AWS_REGION', 'us-east-1')

    url = UnicodeAttribute(hash_key=True)  # URL as primary key (unique)
    id = NumberAttribute(null=True)  # For compatibility, auto-generated
    title = UnicodeAttribute()
    company = UnicodeAttribute()
    location = UnicodeAttribute(null=True)
    board_source = UnicodeAttribute()
    posted_date = UTCDateTimeAttribute(null=True)
    status = UnicodeAttribute(default='active')

    # Job details
    job_type = UnicodeAttribute(null=True)  # 'Full-time', 'Part-time', 'Contract', 'Internship', 'Temporary'
    work_mode = UnicodeAttribute(null=True)  # 'Remote', 'Hybrid', 'On-site'
    experience_level = UnicodeAttribute(null=True)  # 'Entry', 'Mid', 'Senior', 'Lead', 'Executive'
    description = UnicodeAttribute(null=True)  # Full job description

    # Salary information
    salary_min = NumberAttribute(null=True)
    salary_max = NumberAttribute(null=True)
    salary_currency = UnicodeAttribute(null=True, default='USD')
    salary_period = UnicodeAttribute(null=True)  # 'yearly', 'hourly', 'monthly'

    # Metadata
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)

    # Application tracking
    applied = BooleanAttribute(default=False)
    applied_date = UTCDateTimeAttribute(null=True)
    application_status = UnicodeAttribute(default='not_applied')  # 'not_applied', 'applied', 'interview', 'rejected', 'offer'


class DynamoDatabase:
    """DynamoDB database manager - compatible with existing Database interface."""

    def __init__(self, table_name: str = None):
        """Initialize DynamoDB connection."""
        if table_name:
            JobModel.Meta.table_name = table_name

        # Create table if it doesn't exist
        if not JobModel.exists():
            JobModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def create_tables(self):
        """Create DynamoDB table if it doesn't exist."""
        if not JobModel.exists():
            JobModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def add_job(self, title: str, company: str, url: str, board_source: str,
                location: str = None, posted_date: datetime = None,
                job_type: str = None, work_mode: str = None,
                experience_level: str = None, description: str = None,
                salary_min: int = None, salary_max: int = None,
                salary_currency: str = 'USD', salary_period: str = None) -> JobModel:
        """
        Add a new job to DynamoDB.

        Returns:
            The created JobModel object
        """
        # Generate a simple numeric ID based on timestamp
        job_id = int(datetime.utcnow().timestamp() * 1000000)

        job = JobModel(
            url=url,
            id=job_id,
            title=title,
            company=company,
            board_source=board_source,
            location=location,
            posted_date=posted_date,
            status='active',
            job_type=job_type,
            work_mode=work_mode,
            experience_level=experience_level,
            description=description,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            salary_period=salary_period
        )
        job.save()
        return job

    def get_job_by_url(self, url: str) -> Optional[JobModel]:
        """Get a job by its URL."""
        try:
            return JobModel.get(url)
        except JobModel.DoesNotExist:
            return None

    def get_jobs_by_status(self, status: str = 'active') -> List[JobModel]:
        """Get all jobs with a specific status."""
        # Note: This requires a Global Secondary Index on 'status' for efficiency
        # For now, we scan the entire table (acceptable for small datasets)
        return list(JobModel.scan(JobModel.status == status))

    def get_jobs_since(self, since: datetime, status: str = 'active') -> List[JobModel]:
        """Get jobs added since a specific datetime."""
        jobs = JobModel.scan(
            (JobModel.posted_date >= since) & (JobModel.status == status)
        )
        return sorted(list(jobs), key=lambda x: x.posted_date, reverse=True)

    def get_recent_jobs(self, days: int = 7, status: str = 'active') -> List[JobModel]:
        """Get jobs from the last N days."""
        since = datetime.utcnow() - timedelta(days=days)
        return self.get_jobs_since(since, status)

    def mark_job_expired(self, url: str) -> bool:
        """Mark a job as expired by URL."""
        try:
            job = JobModel.get(url)
            job.status = 'expired'
            job.save()
            return True
        except JobModel.DoesNotExist:
            return False

    def search_jobs(self, keyword: str, status: str = 'active') -> List[JobModel]:
        """Search jobs by keyword in title or company."""
        keyword_lower = keyword.lower()
        all_jobs = self.get_jobs_by_status(status)

        # Filter in Python (DynamoDB doesn't support LIKE queries)
        return [
            job for job in all_jobs
            if keyword_lower in job.title.lower() or keyword_lower in job.company.lower()
        ]

    def get_job_count_by_source(self) -> dict:
        """Get count of jobs grouped by board source."""
        all_jobs = list(JobModel.scan())

        stats = {}
        for job in all_jobs:
            source = job.board_source
            status = job.status

            if source not in stats:
                stats[source] = {}
            if status not in stats[source]:
                stats[source][status] = 0
            stats[source][status] += 1

        return stats
