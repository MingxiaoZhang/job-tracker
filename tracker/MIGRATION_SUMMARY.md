# AWS Fargate Migration Summary

## What Was Done

Your Job Board Tracker has been upgraded to support **cloud deployment on AWS Fargate**! 🎉

### Key Changes

#### 1. **Database Abstraction Layer**
- ✅ Added DynamoDB support (cloud database)
- ✅ Created database factory pattern (automatically chooses SQLite or DynamoDB)
- ✅ **Your local setup still works exactly as before!**

#### 2. **AWS Infrastructure (Terraform)**
- ✅ Complete infrastructure as code
- ✅ ECS Fargate cluster
- ✅ DynamoDB table
- ✅ EventBridge scheduler (runs every 6 hours)
- ✅ IAM roles & security groups
- ✅ CloudWatch logging

#### 3. **Documentation**
- ✅ Quick start guide (5-minute deployment)
- ✅ Detailed deployment guide
- ✅ Cost breakdown
- ✅ Troubleshooting tips

## New Files Created

```
aws/
├── terraform/
│   ├── main.tf          # Infrastructure configuration
│   ├── variables.tf     # Customizable settings
│   └── outputs.tf       # Deployment info
├── DEPLOYMENT.md        # Detailed guide
├── QUICK_START.md       # Fast deployment
└── README.md            # Overview

src/database/
├── dynamodb.py          # DynamoDB implementation
└── factory.py           # Database selector

.env.aws.example         # AWS environment variables reference
MIGRATION_SUMMARY.md     # This file
```

## Modified Files

### `src/main.py`
**Before:**
```python
from src.database.db import Database
db = Database(DATABASE_PATH)
```

**After:**
```python
from src.database.factory import get_database
db = get_database()  # Auto-selects SQLite or DynamoDB
```

### `config/settings.py`
**Added:**
```python
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'job-tracker-jobs')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
```

### `requirements.txt`
**Added:**
```
boto3>=1.28.0         # AWS SDK
pynamodb>=5.5.0       # DynamoDB ORM
```

## Backward Compatibility

### ✅ Local Development (Unchanged)
```bash
# Still works exactly as before
python src/main.py
docker-compose run --rm tracker
docker-compose --profile scheduler up -d
```

### ✅ All Features Work
- Scrapers (Indeed, LinkedIn) - No changes
- CLI commands (list, search, stats) - No changes
- Docker setup - No changes
- Scheduler - No changes

## How It Works Now

### Local Mode (Default)
```bash
# Uses SQLite (default)
python src/main.py
```

### AWS Mode
```bash
# Set environment variable
export DATABASE_TYPE=dynamodb

# Uses DynamoDB
python src/main.py
```

The Terraform configuration automatically sets `DATABASE_TYPE=dynamodb` for ECS tasks.

## Architecture Comparison

### Before (Local Only)
```
┌──────────────┐
│   Your PC    │
│              │
│  ┌────────┐  │
│  │ Cron   │  │ ← Stops when you close VSCode
│  └───┬────┘  │
│      │       │
│  ┌───▼────┐  │
│  │Scraper │  │
│  └───┬────┘  │
│      │       │
│  ┌───▼────┐  │
│  │ SQLite │  │ ← Local file database
│  └────────┘  │
└──────────────┘
```

### After (AWS Fargate)
```
┌─────────────────────────────────────┐
│             AWS Cloud               │
│                                     │
│  ┌──────────────┐                  │
│  │ EventBridge  │ ← Runs 24/7      │
│  │  (Schedule)  │                  │
│  └──────┬───────┘                  │
│         │ Every 6 hours            │
│         ▼                          │
│  ┌──────────────┐                  │
│  │ ECS Fargate  │ ← Serverless     │
│  │  (Container) │                  │
│  └──────┬───────┘                  │
│         │                          │
│         ▼                          │
│  ┌──────────────┐                  │
│  │  DynamoDB    │ ← Cloud database │
│  └──────────────┘                  │
└─────────────────────────────────────┘
```

## Cost Breakdown

| Component | Cost/Month | Notes |
|-----------|------------|-------|
| ECS Fargate (0.5 vCPU, 1 GB RAM) | ~$1.20 | 4 runs/day × 5 min |
| DynamoDB (on-demand) | $0.00 | Free tier: 25 GB |
| ECR (image storage) | $0.00 | Free tier: 500 MB |
| CloudWatch Logs | $0.00 | Free tier: 5 GB |
| EventBridge | $0.00 | Always free |
| **Total** | **~$1-2/month** | After free tier expires |

**First 12 months**: Potentially $0/month with AWS free tier

## Next Steps

### To Deploy to AWS:

1. **Quick Start** (5 minutes)
   ```bash
   cd aws
   cat QUICK_START.md
   ```

2. **Detailed Guide** (with explanations)
   ```bash
   cd aws
   cat DEPLOYMENT.md
   ```

### To Continue Local Development:

Nothing changes! Just keep using:
```bash
python src/main.py
docker-compose run --rm tracker
```

## Key Benefits

### ✅ Runs 24/7
Your scraper runs even when your computer is off or VSCode is closed.

### ✅ No Server Management
AWS manages the infrastructure. You just push code.

### ✅ Automatic Scaling
If jobs take longer, AWS handles it. No capacity planning needed.

### ✅ Cloud-Native Storage
DynamoDB automatically backs up data and scales infinitely.

### ✅ Professional Logging
CloudWatch captures all logs with timestamps and searchability.

### ✅ Cost-Effective
~$1-2/month is cheaper than running a server or keeping your PC on 24/7.

## Testing Before Deployment

### Test DynamoDB Locally:
```bash
# Install AWS CLI and configure
aws configure

# Run with DynamoDB (creates table in your AWS account)
export DATABASE_TYPE=dynamodb
export DYNAMODB_TABLE_NAME=job-tracker-test
export AWS_REGION=us-east-1
python src/main.py

# Clean up test table
aws dynamodb delete-table --table-name job-tracker-test
```

## Rollback Plan

If you want to remove AWS deployment:

```bash
cd aws/terraform
terraform destroy
# Type 'yes' to confirm
```

This removes:
- All AWS resources
- DynamoDB table (and all job data)
- ECS cluster
- EventBridge schedule
- CloudWatch logs

**Your local setup is unaffected.**

## Support & Troubleshooting

### Common Issues:

**1. "Terraform not found"**
```bash
# Install Terraform
brew install terraform  # macOS
# or download from https://terraform.io
```

**2. "AWS credentials not configured"**
```bash
aws configure
# Enter your Access Key ID and Secret Access Key
```

**3. "Docker image push failed"**
```bash
# Re-authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ECR_URL>
```

**4. "Task failed to start"**
```bash
# Check logs
aws logs tail /ecs/job-tracker --follow
```

### Getting Help:

1. Check `aws/DEPLOYMENT.md` for detailed troubleshooting
2. View AWS Console for visual debugging
3. Check CloudWatch logs for error messages

## What Hasn't Changed

- ✅ Scraper logic (Indeed, LinkedIn)
- ✅ Job deduplication
- ✅ CLI commands
- ✅ Docker configuration
- ✅ Local development workflow
- ✅ .env configuration format

## Database Migration (Optional)

If you want to migrate existing SQLite jobs to DynamoDB:

```python
# migration_script.py (create this if needed)
import os
os.environ['DATABASE_TYPE'] = 'sqlite'
from src.database.db import Database as SQLiteDB

os.environ['DATABASE_TYPE'] = 'dynamodb'
from src.database.dynamodb import DynamoDatabase

# Read from SQLite
sqlite_db = SQLiteDB('jobs.db')
jobs = sqlite_db.get_jobs_by_status('active')

# Write to DynamoDB
dynamo_db = DynamoDatabase()
for job in jobs:
    dynamo_db.add_job(
        title=job.title,
        company=job.company,
        url=job.url,
        board_source=job.board_source,
        location=job.location,
        posted_date=job.posted_date
    )

print(f"Migrated {len(jobs)} jobs to DynamoDB")
```

## Future Enhancements

Now that you're on AWS, you can easily add:

1. **Email Notifications** (via Amazon SES)
2. **Web Dashboard** (via AWS Amplify or S3 + CloudFront)
3. **Slack/Discord Alerts** (via AWS Lambda)
4. **Multiple Schedules** (different searches at different times)
5. **Analytics Dashboard** (via CloudWatch Dashboards)

## Summary

🎉 **Success!** Your job tracker is now ready for cloud deployment.

- **Local development**: Works exactly as before
- **AWS deployment**: Fully automated, runs 24/7
- **Cost**: ~$1-2/month
- **Setup time**: 5 minutes

**Next step**: See `aws/QUICK_START.md` to deploy!

---

Questions? Check `aws/DEPLOYMENT.md` or open an issue.
