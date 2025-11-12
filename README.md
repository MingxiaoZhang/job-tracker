# Job Board Tracker

A comprehensive job board monitoring system with a powerful web dashboard. Track job listings across multiple platforms, visualize trends, and discover new opportunities.

## 📦 Project Components

This repository contains two main components:

### 1. **Tracker** (`/tracker`)
Python-based job scraper that monitors Indeed and LinkedIn for new postings and stores them in DynamoDB/SQLite.

**Key Features:**
- Monitor multiple job boards (Indeed, LinkedIn)
- Track new job postings automatically
- Keyword-based filtering
- Email notifications for new matches
- Simple CLI interface
- Docker support for AWS deployment

**[📖 Tracker Documentation →](tracker/README.md)**

### 2. **Dashboard** (`/dashboard`)
Next.js web application that provides a beautiful interface to visualize and filter your tracked jobs.

**Key Features:**
- Real-time job statistics and metrics
- Interactive charts (status distribution, timeline, top companies)
- Searchable and filterable job table with pagination
- Responsive design with Tailwind CSS
- Free deployment on Vercel

**[📖 Dashboard Documentation →](dashboard/README.md)**

## 🚀 Quick Start

### 1. Set up the Tracker

```bash
# Navigate to tracker directory
cd tracker

# Install dependencies
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt

# Configure settings
cp .env.aws.example .env.aws
# Edit .env.aws with your AWS credentials and preferences

# Run the scraper
python src/main.py
```

**For detailed tracker setup, deployment, and CLI usage:**
- [Tracker README](tracker/README.md)
- [AWS Deployment Guide](aws/DEPLOYMENT.md)
- [Quick AWS Start](aws/QUICK_START.md)

### 2. Set up the Dashboard

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your AWS credentials

# Run development server
npm run dev
```

**For detailed dashboard setup and deployment to Vercel:**
- [Dashboard README](dashboard/README.md)

## 💡 Typical Workflow

1. **Deploy Tracker to AWS** - Runs automatically every 6 hours scraping jobs
2. **Deploy Dashboard to Vercel** - Free hosting for your dashboard
3. **Access Dashboard** - View and filter your jobs anytime from anywhere

## 📂 Project Structure

```
job-board-tracker/
├── tracker/                 # Python job scraper
│   ├── src/
│   │   ├── scrapers/       # Job board scrapers (Indeed, LinkedIn)
│   │   ├── database/       # Database models and operations
│   │   ├── tracker/        # Job monitoring logic
│   │   ├── cli/            # CLI commands
│   │   ├── notifications/  # Email notifications
│   │   ├── main.py         # Entry point
│   │   └── scheduler.py    # Continuous scheduler
│   ├── config/             # Configuration settings
│   ├── tests/              # Test files
│   └── requirements.txt    # Python dependencies
│
├── dashboard/              # Next.js web dashboard
│   ├── app/               # Next.js app router pages
│   ├── components/        # React components
│   ├── lib/               # Utility functions and DynamoDB client
│   └── package.json       # Node.js dependencies
│
├── aws/                    # AWS deployment scripts and guides
│   ├── terraform/         # Infrastructure as Code
│   ├── DEPLOYMENT.md      # Full deployment guide
│   └── QUICK_START.md     # Quick start guide
│
├── Dockerfile              # Docker configuration for tracker
├── docker-compose.yml      # Docker orchestration
└── README.md              # This file
```

## 🛠️ Technology Stack

**Tracker:**
- Python 3.10+ with Selenium for web scraping
- SQLite (local) or DynamoDB (AWS) for storage
- Docker for containerization
- AWS ECS Fargate for serverless deployment

**Dashboard:**
- Next.js 14 with App Router
- React with TypeScript
- Tailwind CSS for styling
- Chart.js for data visualization
- Vercel for deployment (free tier)

## 📝 License

MIT
