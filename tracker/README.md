# Job Tracker

Python-based job board scraper that monitors Indeed and LinkedIn for new job postings and stores them in DynamoDB or SQLite.

## Features

- **Multi-Platform Scraping**: Scrapes Indeed and LinkedIn job boards
- **Intelligent Tracking**: Detects and tracks new jobs, avoiding duplicates
- **Flexible Storage**: Supports both SQLite (local) and DynamoDB (AWS)
- **Job Metadata**: Extracts title, company, location, salary, job type, work mode, and experience level
- **CLI Interface**: Simple commands to list, search, and view statistics
- **Email Notifications**: Optional notifications for new job matches
- **Containerized**: Docker support for easy deployment
- **Serverless Ready**: Deploy to AWS ECS Fargate for 24/7 operation

## Installation

### Prerequisites

- Python 3.10 or higher
- Chrome/Chromium browser (for Selenium)

### Local Setup

1. **Create a virtual environment** (recommended):
```bash
# From project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
cd tracker
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.aws.example .env
# Edit .env with your settings
```

### Configuration

Create a `.env` file in the tracker directory:

```bash
# Database Configuration
DATABASE_TYPE=sqlite          # 'sqlite' or 'dynamodb'
DATABASE_PATH=jobs.db         # For SQLite
DYNAMODB_TABLE_NAME=job-tracker-jobs  # For DynamoDB
AWS_REGION=us-east-1         # For DynamoDB

# AWS Credentials (for DynamoDB)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Scraper Settings
SEARCH_QUERY=software engineer
LOCATION=Remote
SCRAPE_INTERVAL_HOURS=6

# Email Notifications (Optional)
NOTIFY_ON_NEW_JOBS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
KEYWORDS_FILTER=python,remote,senior  # Comma-separated
```

## Usage

### Run the Scraper

```bash
# Run from project root
python tracker/src/main.py
```

This will:
1. Initialize the database
2. Scrape Indeed and LinkedIn
3. Process and store new jobs
4. Display results and statistics

### CLI Commands

#### List Recent Jobs

```bash
# List jobs from the last 7 days (default)
python tracker/src/main.py list --days 7

# List jobs from the last 30 days
python tracker/src/main.py list --days 30
```

#### Search Jobs

```bash
# Search for jobs containing a keyword
python tracker/src/main.py search --keyword python

# Search for remote positions
python tracker/src/main.py search --keyword remote
```

#### View Statistics

```bash
# Display tracking statistics
python tracker/src/main.py stats
```

This shows:
- Total jobs tracked
- Jobs found today/this week/this month
- Breakdown by source (Indeed, LinkedIn)
- Top companies hiring

## Docker Deployment

### Build and Run Locally

```bash
# From project root
docker-compose build

# Run scraper once
docker-compose run --rm tracker

# Run CLI commands
docker-compose run --rm tracker python tracker/src/main.py list --days 7
docker-compose run --rm tracker python tracker/src/main.py stats
```

### Continuous Scheduler

Run the scheduler service to scrape jobs automatically at intervals:

```bash
# Start scheduler (runs every 6 hours)
docker-compose --profile scheduler up -d scheduler

# View logs
docker-compose logs -f scheduler

# Stop scheduler
docker-compose --profile scheduler down
```

## AWS Deployment

### Deploy to AWS ECS Fargate

The tracker can be deployed to AWS for fully automated, serverless job tracking.

**Cost**: ~$1-2/month (mostly free for first 12 months)

**Benefits**:
- Runs 24/7 without keeping your computer on
- Automatic scaling and fault tolerance
- Cloud-native DynamoDB storage
- No server maintenance required

**Quick Deploy**:

```bash
# From project root
cd aws/terraform

# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply

# Build and deploy Docker image
cd ../..
./DEPLOY_NOW.sh
```

**For detailed deployment instructions, see**:
- [Quick Start Guide](../aws/QUICK_START.md)
- [Full Deployment Guide](../aws/DEPLOYMENT.md)

### Environment Variables for AWS

When deploying to AWS, the tracker automatically uses DynamoDB. Configure these in your AWS ECS task definition:

- `DATABASE_TYPE=dynamodb`
- `DYNAMODB_TABLE_NAME=job-tracker-jobs`
- `AWS_REGION=us-east-1`
- `SEARCH_QUERY=software engineer`
- `LOCATION=Remote`
- `SCRAPE_INTERVAL_HOURS=6`

## Database Schema

### Job Model

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique job identifier (URL hash) |
| url | String | Job posting URL |
| title | String | Job title |
| company | String | Company name |
| location | String | Job location |
| salary | String | Salary range (if available) |
| description | Text | Job description |
| posted_date | DateTime | When job was posted |
| board_source | String | 'indeed' or 'linkedin' |
| application_status | String | 'active', 'applied', 'rejected', 'interview' |
| job_type | String | 'Full-time', 'Part-time', 'Contract', etc. |
| work_mode | String | 'Remote', 'Hybrid', 'On-site' |
| experience_level | String | 'Entry', 'Mid', 'Senior', 'Lead' |
| first_seen | DateTime | When tracker first detected this job |
| last_seen | DateTime | Last time tracker saw this job |

## Project Structure

```
tracker/
├── src/
│   ├── cli/
│   │   └── commands.py          # CLI command implementations
│   ├── database/
│   │   ├── db.py               # SQLite implementation
│   │   ├── dynamodb.py         # DynamoDB implementation
│   │   ├── factory.py          # Database factory pattern
│   │   └── models.py           # Job model
│   ├── notifications/
│   │   └── email_notifier.py   # Email notification service
│   ├── scrapers/
│   │   ├── base.py             # Base scraper class
│   │   ├── indeed_scraper.py   # Indeed scraper
│   │   └── linkedin_scraper.py # LinkedIn scraper
│   ├── tracker/
│   │   └── monitor.py          # Job monitoring logic
│   ├── main.py                 # Application entry point
│   └── scheduler.py            # Continuous scheduler
├── config/
│   └── settings.py             # Configuration settings
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## How It Works

1. **Scraping**: The tracker uses Selenium to scrape job listings from Indeed and LinkedIn
2. **Deduplication**: Each job is assigned a unique ID based on its URL to prevent duplicates
3. **Storage**: Jobs are stored in SQLite (local) or DynamoDB (AWS)
4. **Tracking**: The monitor tracks when jobs are first seen and last seen
5. **Notifications**: Optionally sends email notifications for new matches based on keywords

## Troubleshooting

### ChromeDriver Issues

If you encounter ChromeDriver errors:

1. Ensure Chrome/Chromium is installed
2. ChromeDriver version must match your Chrome version
3. For Docker deployments, the Dockerfile handles this automatically

### Database Connection Errors

**SQLite**:
- Ensure the database path is writable
- Check that the parent directory exists

**DynamoDB**:
- Verify AWS credentials are configured correctly
- Ensure the table exists in the specified region
- Check IAM permissions for DynamoDB access

### Scraping Failures

- LinkedIn may require authentication for some searches
- Indeed may rate-limit requests (the scraper includes delays to avoid this)
- Some jobs may not have all fields available

## Development

### Running Tests

```bash
cd tracker
python -m pytest tests/
```

### Adding a New Scraper

1. Create a new file in `src/scrapers/`
2. Inherit from `BaseScraper` class
3. Implement the `scrape()` method
4. Add the scraper to `src/main.py`

Example:

```python
from src.scrapers.base import BaseScraper

class NewBoardScraper(BaseScraper):
    def scrape(self) -> list:
        # Implement scraping logic
        return jobs
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
