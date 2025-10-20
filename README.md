# Job Board Tracker

A job board monitoring tool that tracks job listings across multiple platforms and notifies you of new opportunities.

## Features
- Monitor multiple job boards (Indeed, LinkedIn)
- Track new job postings automatically
- Keyword-based filtering
- Email notifications for new matches
- Simple CLI interface
- Docker support for easy deployment

## Setup

### Local Setup (without Docker)

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure settings:
```bash
cp .env.example .env
# Edit .env with your preferences
```

3. Run the tracker:
```bash
python src/main.py
```

### Docker Setup (Recommended)

1. Build the image:
```bash
docker-compose build
```

2. Run once (scrape now):
```bash
docker-compose run --rm tracker
```

3. Run scheduler (continuous):
```bash
docker-compose --profile scheduler up -d scheduler
```

4. View logs:
```bash
docker-compose logs -f scheduler
```

5. Stop scheduler:
```bash
docker-compose --profile scheduler down
```

## CLI Commands

```bash
# Run scraper (default)
python src/main.py

# List jobs from last 7 days
python src/main.py list --days 7

# Search jobs by keyword
python src/main.py search --keyword python

# Show statistics
python src/main.py stats
```

### Docker CLI Commands

```bash
# List jobs
docker-compose run --rm tracker python src/main.py list --days 7

# Search jobs
docker-compose run --rm tracker python src/main.py search --keyword python

# Stats
docker-compose run --rm tracker python src/main.py stats
```

## Configuration

Edit `.env` file:

```bash
# Scraper settings
SEARCH_QUERY=software engineer
LOCATION=Remote
SCRAPE_INTERVAL_HOURS=6

# Email notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

## Deployment

### AWS EC2
1. Launch t2.micro instance (free tier)
2. Install Docker
3. Clone repository
4. Run with docker-compose

### AWS ECS/Fargate
1. Build and push image to ECR
2. Create ECS task definition
3. Use EventBridge to schedule task runs

### Local with cron
```bash
# Add to crontab
0 */6 * * * cd /path/to/tracker && docker-compose run --rm tracker
```

## Project Structure
```
tracker/
├── src/
│   ├── scrapers/      # Job board scrapers
│   ├── database/      # Database models and operations
│   ├── tracker/       # Job monitoring logic
│   ├── cli/           # CLI commands
│   ├── notifications/ # Email notifications
│   ├── main.py        # Entry point
│   └── scheduler.py   # Continuous scheduler
├── config/            # Configuration
├── tests/             # Tests
├── Dockerfile         # Docker image definition
├── docker-compose.yml # Docker orchestration
└── requirements.txt   # Python dependencies
```

## License
MIT
