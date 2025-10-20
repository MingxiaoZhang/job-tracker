"""
Database models using SQLAlchemy.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='active')  # 'active', 'expired', 'archived'

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"
