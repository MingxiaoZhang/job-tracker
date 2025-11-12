# AWS Fargate Deployment

This directory contains everything needed to deploy the Job Tracker to AWS using ECS Fargate.

## What's Changed?

Your job tracker now supports **two database backends**:

1. **SQLite** (local development) - Original setup, still works locally
2. **DynamoDB** (AWS deployment) - New cloud-native database

The application automatically chooses the right database based on the `DATABASE_TYPE` environment variable.

## Files Overview

```
aws/
├── terraform/           # Infrastructure as Code
│   ├── main.tf         # Main Terraform configuration
│   ├── variables.tf    # Customizable settings
│   └── outputs.tf      # Deployment outputs
├── DEPLOYMENT.md       # Detailed deployment guide
├── QUICK_START.md      # 5-minute quick start
└── README.md          # This file
```

## How It Works

### Local Development (No changes needed!)
```bash
# Still works exactly as before
docker-compose run --rm tracker
```

### AWS Production
```bash
# Runs automatically every 6 hours on AWS Fargate
# Uses DynamoDB instead of SQLite
# No server to maintain!
```

## Architecture

```
┌─────────────────┐
│  EventBridge    │  Triggers every 6 hours
│   Schedule      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ECS Fargate   │  Runs Docker container
│   (Job Tracker) │  - Chrome + Selenium
└────────┬────────┘  - Python scraper
         │
         ├──────────► DynamoDB (stores jobs)
         │
         ├──────────► Indeed.com (scrapes)
         │
         ├──────────► LinkedIn.com (scrapes)
         │
         └──────────► CloudWatch Logs (logging)
```

## Cost Breakdown

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| ECS Fargate | 4 runs/day × 5 min × $0.04048/hour | ~$1.20 |
| DynamoDB | On-demand (25 GB free) | $0.00 |
| ECR | 500 MB (free tier) | $0.00 |
| CloudWatch Logs | < 5 GB (free tier) | $0.00 |
| EventBridge | Unlimited rules (free) | $0.00 |
| **Total** | | **~$1-2/month** |

**Note**: First 12 months of AWS include free tier credits that may reduce costs to $0.

## Getting Started

Choose your path:

### 🚀 Fast Track (5 minutes)
Follow **[QUICK_START.md](./QUICK_START.md)** for rapid deployment.

### 📚 Detailed Guide
Follow **[DEPLOYMENT.md](./DEPLOYMENT.md)** for step-by-step instructions with explanations.

## Code Changes Summary

### New Files
- `src/database/dynamodb.py` - DynamoDB implementation
- `src/database/factory.py` - Database selector (SQLite or DynamoDB)
- `config/settings.py` - Added `DATABASE_TYPE`, `DYNAMODB_TABLE_NAME`, `AWS_REGION`
- `requirements.txt` - Added `boto3` and `pynamodb` for AWS

### Modified Files
- `src/main.py` - Now uses database factory instead of hardcoded SQLite

### No Changes Needed
- Scrapers (Indeed, LinkedIn) - Work exactly the same
- Docker setup - Already compatible with ECS Fargate
- CLI commands - Work with both databases

## Local Testing with DynamoDB

You can test DynamoDB locally before deploying:

```bash
# Install AWS CLI and configure credentials
aws configure

# Set environment variables
export DATABASE_TYPE=dynamodb
export DYNAMODB_TABLE_NAME=job-tracker-jobs-dev
export AWS_REGION=us-east-1

# Run normally
python src/main.py
```

This will create a DynamoDB table in your AWS account and use it instead of SQLite.

## Switching Back to SQLite

Your local setup is unchanged! Just don't set `DATABASE_TYPE`:

```bash
# Uses SQLite by default
python src/main.py

# Or explicitly set it
export DATABASE_TYPE=sqlite
python src/main.py
```

## Monitoring

### View Logs
```bash
aws logs tail /ecs/job-tracker --follow
```

### Check Jobs
```bash
aws dynamodb scan --table-name job-tracker-jobs --max-items 10
```

### AWS Console Links
- [ECS Tasks](https://console.aws.amazon.com/ecs/v2/clusters/job-tracker-cluster/tasks)
- [DynamoDB Table](https://console.aws.amazon.com/dynamodbv2/home#item-explorer?table=job-tracker-jobs)
- [CloudWatch Logs](https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups/log-group/$252Fecs$252Fjob-tracker)
- [EventBridge Schedule](https://console.aws.amazon.com/events/home#/rules/job-tracker-schedule)

## FAQ

**Q: Will this break my local setup?**
A: No! Local development still uses SQLite by default. The changes are backward compatible.

**Q: Can I run this without Terraform?**
A: Not easily. Terraform automates creating 10+ AWS resources. Manual setup would take hours.

**Q: What if I want to use a different database?**
A: The factory pattern makes it easy to add new backends. Just create a new class in `src/database/` that implements the same interface.

**Q: How do I update my search query?**
A: Edit `aws/terraform/variables.tf` and run `terraform apply`. Or update the ECS task definition in the AWS Console.

**Q: Can I run this on a schedule other than 6 hours?**
A: Yes! Edit the `schedule_expression` in `aws/terraform/main.tf`. See [DEPLOYMENT.md](./DEPLOYMENT.md#changing-the-schedule).

**Q: Will Chrome/Selenium work in Fargate?**
A: Yes! Your existing Dockerfile already installs Chrome and ChromeDriver. It works great in Fargate.

**Q: How do I delete everything?**
A: Run `terraform destroy` in the `aws/terraform` directory.

## Support

- **Issues**: Open a GitHub issue
- **AWS Documentation**: [ECS Fargate Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- **Terraform Docs**: [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## What's Next?

1. ✅ Deploy to AWS (see QUICK_START.md)
2. Implement email notifications
3. Add a web dashboard to view jobs
4. Set up CloudWatch dashboards for metrics
5. Add more job boards (Glassdoor, Monster, etc.)

Happy job hunting! 🚀
