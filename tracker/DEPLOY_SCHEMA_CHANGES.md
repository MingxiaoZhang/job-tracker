# Deploying Schema Changes to AWS

## What Changed

You've added new fields to the database schema:
- `job_type` (Full-time, Part-time, etc.)
- `work_mode` (Remote, Hybrid, On-site)
- `experience_level` (Entry, Mid, Senior, etc.)
- `description`, salary fields, metadata, and application tracking fields

## Good News: DynamoDB is Schema-less! 🎉

Unlike traditional SQL databases, **DynamoDB doesn't require migrations**. Your new fields will automatically work because:

1. **Schema-less design**: DynamoDB allows different items to have different attributes
2. **Backward compatible**: Existing jobs without new fields continue to work
3. **Forward compatible**: New jobs with new fields are automatically stored

## Deployment Steps

### Option 1: Quick Redeploy (Recommended)

If you've already deployed to AWS, simply rebuild and push your Docker image:

```bash
# 1. Get your ECR repository URL
cd aws/terraform
ECR_REPO=$(terraform output -raw ecr_repository_url)
cd ../..

# 2. Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REPO

# 3. Build new image with updated code
docker build -t job-tracker .

# 4. Tag and push
docker tag job-tracker:latest $ECR_REPO:latest
docker push $ECR_REPO:latest

# 5. Force ECS to pull new image on next run
aws ecs update-service \
  --cluster job-tracker-cluster \
  --service job-tracker-service \
  --force-new-deployment

# Or just wait for the next scheduled run (within 6 hours)
```

### Option 2: First Time AWS Deployment

If you haven't deployed to AWS yet:

```bash
# Follow the quick start guide
cd aws
cat QUICK_START.md

# Then run these commands:
cd terraform
terraform init
terraform apply  # Type 'yes' when prompted
```

Then follow the Docker build steps from Option 1.

## Verify Deployment

### 1. Check that new code is running

```bash
# Watch logs for the next scraper run
aws logs tail /ecs/job-tracker --follow
```

Look for scrapers extracting new fields like:
```
Successfully scraped X jobs
Job type: Full-time
Work mode: Remote
```

### 2. Verify new fields in DynamoDB

```bash
# Query recent jobs and check for new fields
aws dynamodb scan \
  --table-name job-tracker-jobs \
  --max-items 3 \
  --output json
```

You should see attributes like `job_type`, `work_mode`, `experience_level` in the response.

### 3. Test locally with DynamoDB (Optional)

```bash
# Set environment to use AWS DynamoDB
export DATABASE_TYPE=dynamodb
export DYNAMODB_TABLE_NAME=job-tracker-jobs
export AWS_REGION=us-east-1

# Run scraper locally (connects to AWS DynamoDB)
source venv/bin/activate
python src/main.py

# Check that new fields are populated
```

## What Happens to Existing Jobs?

### Existing Jobs (Before Schema Change)
- **Still accessible**: All old jobs remain in DynamoDB
- **Missing fields**: New fields will be `null` for old jobs
- **No errors**: Code uses `hasattr()` checks and handles missing fields gracefully

### New Jobs (After Schema Change)
- **All fields populated**: job_type, work_mode, experience_level extracted
- **Backward compatible**: Code still works with SQLite locally

## Rollback Plan

If something goes wrong:

```bash
# Option 1: Roll back to previous Docker image
aws ecr describe-images \
  --repository-name job-tracker \
  --query 'imageDetails[*].[imageTags[0],imagePushedAt]' \
  --output table

# Find the previous image tag/digest, then:
docker pull <ECR_REPO>:<previous-tag>
docker tag <ECR_REPO>:<previous-tag> <ECR_REPO>:latest
docker push <ECR_REPO>:latest

# Option 2: Destroy and redeploy
cd aws/terraform
terraform destroy  # Warning: This deletes all job data!
terraform apply
```

## Testing Before Production

### Test the new schema locally first:

```bash
# 1. Test with local SQLite
python src/main.py

# 2. Check that new fields appear
python -c "
from src.database.factory import get_database
db = get_database()
jobs = db.get_recent_jobs(days=1)
for job in jobs:
    print(f'{job.title}: {job.job_type} | {job.work_mode} | {job.experience_level}')
"
```

### Test with AWS DynamoDB (non-production table):

```bash
# Create a test table
export DATABASE_TYPE=dynamodb
export DYNAMODB_TABLE_NAME=job-tracker-test
export AWS_REGION=us-east-1

python src/main.py

# Verify new fields
aws dynamodb scan --table-name job-tracker-test --max-items 2

# Clean up test table
aws dynamodb delete-table --table-name job-tracker-test
```

## Monitoring After Deployment

### 1. Check CloudWatch Logs

```bash
# Real-time logs
aws logs tail /ecs/job-tracker --follow

# Search for errors
aws logs filter-pattern /ecs/job-tracker --filter-pattern "ERROR"

# Get last 50 log entries
aws logs tail /ecs/job-tracker --since 1h
```

### 2. Verify Scraper Success

```bash
# Check recent task runs
aws ecs list-tasks --cluster job-tracker-cluster

# Get task details
TASK_ARN=$(aws ecs list-tasks --cluster job-tracker-cluster --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster job-tracker-cluster --tasks $TASK_ARN
```

### 3. Query New Jobs with New Fields

```bash
# Count jobs with job_type
aws dynamodb scan \
  --table-name job-tracker-jobs \
  --filter-expression "attribute_exists(job_type)" \
  --select COUNT

# Get sample jobs with new fields
aws dynamodb scan \
  --table-name job-tracker-jobs \
  --filter-expression "attribute_exists(work_mode)" \
  --max-items 5
```

## Cost Impact

**No additional cost!** The schema changes don't affect pricing:
- DynamoDB charges per read/write, not per field
- Same number of jobs = same cost
- Additional attributes have negligible storage cost

**Estimated**: Still ~$1-2/month

## Troubleshooting

### Issue: New fields not appearing

**Cause**: Old Docker image still running

**Solution**:
```bash
# Force ECS to use new image
aws ecs update-service \
  --cluster job-tracker-cluster \
  --service job-tracker-service \
  --force-new-deployment
```

### Issue: "AttributeError: 'Job' object has no attribute 'job_type'"

**Cause**: Querying old jobs that don't have new fields

**Solution**: Already handled in code with `hasattr()` checks. If you see this error, update your code:
```python
# Wrong
print(job.job_type)

# Right
if hasattr(job, 'job_type') and job.job_type:
    print(job.job_type)
```

### Issue: Docker build fails

**Cause**: Requirements or dependencies changed

**Solution**:
```bash
# Clear Docker cache and rebuild
docker build --no-cache -t job-tracker .

# Check requirements.txt is up to date
cat requirements.txt
```

### Issue: Can't push to ECR

**Cause**: ECR authentication expired

**Solution**:
```bash
# Re-authenticate
ECR_REPO=$(cd aws/terraform && terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REPO

# Try push again
docker push $ECR_REPO:latest
```

## Summary

✅ **Schema changes are deployed by simply pushing a new Docker image**

✅ **No database migrations needed** (DynamoDB is schema-less)

✅ **Existing data remains intact** (backward compatible)

✅ **Zero downtime deployment** (next scheduled run picks up new code)

## Next Steps

1. ✅ Build and push Docker image (5 minutes)
2. ✅ Wait for next scheduled run OR trigger manually
3. ✅ Check logs to verify new fields are extracted
4. ✅ Query DynamoDB to see new job data

**Deployment time**: ~5-10 minutes

**Downtime**: None (jobs continue to be tracked)

---

Need help? Check:
- CloudWatch Logs: `aws logs tail /ecs/job-tracker --follow`
- AWS Console: https://console.aws.amazon.com/ecs/
- DynamoDB Console: https://console.aws.amazon.com/dynamodb/
