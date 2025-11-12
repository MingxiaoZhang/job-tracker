# Deploying Your Updated Job Tracker to AWS

## Quick Summary

You've added new fields to your job tracker:
✅ `job_type` - Full-time, Part-time, Contract, etc.
✅ `work_mode` - Remote, Hybrid, On-site
✅ `experience_level` - Entry, Mid, Senior, Lead, Executive
✅ Plus salary fields, metadata, and application tracking

## The Easiest Way - One Command

```bash
./DEPLOY_NOW.sh
```

This script will:
1. ✅ Check prerequisites (AWS CLI, Docker, Terraform)
2. ✅ Verify AWS credentials
3. ✅ Build Docker image with your updated code
4. ✅ Push to AWS ECR
5. ✅ Optionally force immediate deployment

**Time**: ~5-10 minutes

---

## Manual Deployment (Step by Step)

If you prefer to run commands manually:

### Step 1: Navigate to terraform directory and get ECR URL
```bash
cd aws/terraform
ECR_REPO=$(terraform output -raw ecr_repository_url)
cd ../..
```

### Step 2: Login to ECR
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REPO
```

### Step 3: Build Docker image
```bash
docker build -t job-tracker .
```

### Step 4: Tag and push
```bash
docker tag job-tracker:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### Step 5: Wait or force deployment
```bash
# Option A: Wait for next scheduled run (within 6 hours)
# Nothing to do - scheduler will automatically use new image

# Option B: Force immediate deployment
aws ecs update-service \
  --cluster job-tracker-cluster \
  --service job-tracker-service \
  --force-new-deployment
```

---

## First Time AWS Deployment?

If you haven't deployed to AWS yet, start here:

```bash
cd aws
cat QUICK_START.md
```

Then follow the 5-step guide for initial setup.

---

## Why No Database Migration?

**DynamoDB is schema-less!** 🎉

- New fields automatically work
- Old jobs without new fields: still accessible
- New jobs with new fields: automatically stored
- No downtime, no migration scripts needed

---

## Verify Deployment

### Check logs (real-time)
```bash
aws logs tail /ecs/job-tracker --follow
```

### Check DynamoDB data
```bash
aws dynamodb scan --table-name job-tracker-jobs --max-items 3
```

Look for new attributes:
- `job_type`
- `work_mode`
- `experience_level`
- `created_at`
- `updated_at`

### Check task status
```bash
aws ecs list-tasks --cluster job-tracker-cluster
```

---

## Troubleshooting

### "ECR login failed"
```bash
# Reconfigure AWS credentials
aws configure

# Try login again
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REPO
```

### "Terraform state not found"
```bash
# First time deployment - run terraform
cd aws/terraform
terraform init
terraform apply
```

### "Docker build failed"
```bash
# Clear cache and rebuild
docker build --no-cache -t job-tracker .
```

### "New fields not appearing in DynamoDB"
```bash
# Check if new image is being used
aws ecs describe-tasks \
  --cluster job-tracker-cluster \
  --tasks $(aws ecs list-tasks --cluster job-tracker-cluster --query 'taskArns[0]' --output text)

# Force new deployment
aws ecs update-service \
  --cluster job-tracker-cluster \
  --service job-tracker-service \
  --force-new-deployment
```

---

## Cost

**No additional cost** for schema changes!

Still ~$1-2/month:
- DynamoDB: Free tier (25GB storage)
- ECS Fargate: ~$1.20/month (4 runs/day × 5 min)
- ECR: Free tier (500 MB)
- CloudWatch: Free tier (5 GB logs)

---

## Testing Locally First (Recommended)

Before deploying to AWS, test the new fields locally:

```bash
# Test with local SQLite
python src/main.py

# Check that new fields are populated
python -c "
from src.database.factory import get_database
db = get_database()
jobs = db.get_recent_jobs(days=1)
for job in jobs:
    print(f'{job.title}')
    if hasattr(job, 'job_type'):
        print(f'  Type: {job.job_type}')
    if hasattr(job, 'work_mode'):
        print(f'  Mode: {job.work_mode}')
    if hasattr(job, 'experience_level'):
        print(f'  Level: {job.experience_level}')
"
```

---

## What's Different Now?

### Before (Old Schema)
```json
{
  "url": "https://...",
  "title": "Software Engineer",
  "company": "Acme Corp",
  "location": "Remote",
  "board_source": "indeed",
  "posted_date": "2025-10-22",
  "status": "active"
}
```

### After (New Schema)
```json
{
  "url": "https://...",
  "title": "Software Engineer",
  "company": "Acme Corp",
  "location": "Remote",
  "board_source": "indeed",
  "posted_date": "2025-10-22",
  "status": "active",
  "job_type": "Full-time",          ← NEW
  "work_mode": "Remote",            ← NEW
  "experience_level": "Mid",        ← NEW
  "created_at": "2025-10-22T10:00", ← NEW
  "updated_at": "2025-10-22T10:00", ← NEW
  "applied": false,                 ← NEW
  "application_status": "not_applied" ← NEW
}
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Deploy changes** | `./DEPLOY_NOW.sh` |
| **View logs** | `aws logs tail /ecs/job-tracker --follow` |
| **Check jobs** | `aws dynamodb scan --table-name job-tracker-jobs --max-items 5` |
| **Force deploy** | `aws ecs update-service --cluster job-tracker-cluster --service job-tracker-service --force-new-deployment` |
| **Disable scheduler** | `aws events disable-rule --name job-tracker-schedule` |
| **Enable scheduler** | `aws events enable-rule --name job-tracker-schedule` |
| **Destroy AWS** | `cd aws/terraform && terraform destroy` |

---

## Files Created

- ✅ `DEPLOY_NOW.sh` - One-command deployment script
- ✅ `DEPLOY_SCHEMA_CHANGES.md` - Detailed deployment guide
- ✅ `README_DEPLOYMENT.md` - This file (quick reference)

---

## Support

For detailed information, see:
- **Quick Start**: `aws/QUICK_START.md`
- **Full Guide**: `aws/DEPLOYMENT.md`
- **Schema Changes**: `DEPLOY_SCHEMA_CHANGES.md`
- **Migration Info**: `MIGRATION_SUMMARY.md`

---

**Ready to deploy?** Run `./DEPLOY_NOW.sh` 🚀
