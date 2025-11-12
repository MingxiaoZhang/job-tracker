"""
Database models using SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    """Job listing model."""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    url = Column(String, unique=True, nullable=False)
    board_source = Column(String, nullable=False)  # 'indeed', 'linkedin', etc.
    posted_date = Column(DateTime)
    status = Column(String, default='active')  # 'active', 'expired', 'archived'

    # Job details
    job_type = Column(String)  # 'Full-time', 'Part-time', 'Contract', 'Internship', 'Temporary'
    work_mode = Column(String)  # 'Remote', 'Hybrid', 'On-site'
    experience_level = Column(String)  # 'Entry', 'Mid', 'Senior', 'Lead', 'Executive'
    description = Column(Text)  # Full job description

    # Salary information
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String, default='USD')
    salary_period = Column(String)  # 'yearly', 'hourly', 'monthly'

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Application tracking
    applied = Column(Boolean, default=False)
    applied_date = Column(DateTime)
    application_status = Column(String, default='not_applied')  # 'not_applied', 'applied', 'interview', 'rejected', 'offer'

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"
