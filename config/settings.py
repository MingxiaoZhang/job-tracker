"""
Configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_PATH = os.getenv('DATABASE_PATH', 'jobs.db')

# Scraper settings
SEARCH_QUERY = os.getenv('SEARCH_QUERY', 'software engineer')
LOCATION = os.getenv('LOCATION', 'Remote')
SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 6))

# Email notification settings
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

# Notification settings
NOTIFY_ON_NEW_JOBS = os.getenv('NOTIFY_ON_NEW_JOBS', 'true').lower() == 'true'
KEYWORDS_FILTER = os.getenv('KEYWORDS_FILTER', '').split(',') if os.getenv('KEYWORDS_FILTER') else []
