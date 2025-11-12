# AWS Fargate Deployment Guide

This guide will help you deploy the Job Tracker to AWS using ECS Fargate with DynamoDB.

## Architecture Overview

- **AWS ECS Fargate**: Runs your scraper in a Docker container (no servers to manage)
- **Amazon DynamoDB**: Stores job listings (replaces SQLite)
- **Amazon ECR**: Stores your Docker image
- **EventBridge**: Triggers the scraper every 6 hours
- **CloudWatch Logs**: Stores application logs

## Cost Estimate

With AWS Free Tier:
- **DynamoDB**: Free (25 GB storage, 200M requests/month)
- **ECS Fargate**: ~$1-2/month (runs 4x/day, ~5 min each)
- **ECR**: Free (500 MB storage)
- **CloudWatch Logs**: Free (5 GB ingestion, 1 month retention)

**Total: ~$1-2/month** (after free tier expires, first 12 months are mostly free)

## Prerequisites

1. **AWS Account**: [Create one here](https://aws.amazon.com/free/)
2. **AWS CLI**: [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **Terraform**: [Install guide](https://developer.hashicorp.com/terraform/install)
4. **Docker**: Already installed (you're using it locally)

## Step 1: Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (use: us-east-1)
# - Default output format (use: json)
```

To get your AWS credentials:
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Click your username (top right) → Security credentials
3. Scroll to "Access keys" → Create access key
4. Copy the Access Key ID and Secret Access Key

## Step 2: Customize Configuration (Optional)

Edit `aws/terraform/variables.tf` to change:
- `search_query`: Your job search keywords (default: "software engineer")
- `location`: Job location (default: "Remote")
- `aws_region`: AWS region (default: "us-east-1")

## Step 3: Deploy Infrastructure with Terraform

```bash
# Navigate to Terraform directory
cd aws/terraform

# Initialize Terraform
terraform init

# Preview changes (optional but recommended)
terraform plan

# Deploy infrastructure
terraform apply

# Type 'yes' when prompted
```

This will create:
- ✅ DynamoDB table
- ✅ ECR repository
- ✅ ECS cluster & task definition
- ✅ EventBridge schedule (every 6 hours)
- ✅ IAM roles and security groups
- ✅ CloudWatch log group

**Save the output** - you'll need the ECR repository URL.

## Step 4: Build and Push Docker Image

```bash
# Go back to project root
cd ../..

# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Get the ECR repository URL from Terraform output
ECR_REPO=$(terraform -chdir=aws/terraform output -raw ecr_repository_url)

# Log in to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build the Docker image
docker build -t job-tracker .

# Tag the image for ECR
docker tag job-tracker:latest $ECR_REPO:latest

# Push to ECR
docker push $ECR_REPO:latest
```

## Step 5: Verify Deployment

### Check if EventBridge rule is enabled:
```bash
aws events describe-rule --name job-tracker-schedule
```

### Manually trigger a test run (optional):
```bash
# Get cluster and task definition ARNs
CLUSTER_ARN=$(terraform -chdir=aws/terraform output -raw ecs_cluster_name)
TASK_DEF=$(aws ecs list-task-definitions --family-prefix job-tracker --query 'taskDefinitionArns[0]' --output text)

# Get default VPC subnets and security group
SUBNETS=$(aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')
SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=job-tracker-ecs-task" --query 'SecurityGroups[0].GroupId' --output text)

# Run task manually
aws ecs run-task \
  --cluster $CLUSTER_ARN \
  --task-definition $TASK_DEF \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=ENABLED}"
```

### View logs:
```bash
# Get the log stream name (after task starts)
aws logs tail /ecs/job-tracker --follow
```

Or visit [CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups/log-group/$252Fecs$252Fjob-tracker)

### Check DynamoDB for jobs:
```bash
aws dynamodb scan --table-name job-tracker-jobs --max-items 5
```

Or visit [DynamoDB Console](https://console.aws.amazon.com/dynamodbv2/home#tables)

## Step 6: Monitor and Manage

### View all scheduled tasks:
```bash
aws events list-targets-by-rule --rule job-tracker-schedule
```

### Temporarily disable the schedule:
```bash
aws events disable-rule --name job-tracker-schedule
```

### Re-enable the schedule:
```bash
aws events enable-rule --name job-tracker-schedule
```

### View recent ECS tasks:
```bash
CLUSTER=$(terraform -chdir=aws/terraform output -raw ecs_cluster_name)
aws ecs list-tasks --cluster $CLUSTER
```

### Query jobs from DynamoDB:
```bash
# Get total count
aws dynamodb scan --table-name job-tracker-jobs --select COUNT

# Get recent jobs (last 5)
aws dynamodb scan --table-name job-tracker-jobs --max-items 5
```

## Updating the Application

When you make code changes:

```bash
# Rebuild and push image
docker build -t job-tracker .
docker tag job-tracker:latest $ECR_REPO:latest
docker push $ECR_REPO:latest

# Force new deployment (pick up latest image)
CLUSTER=$(terraform -chdir=aws/terraform output -raw ecs_cluster_name)
aws ecs update-service --cluster $CLUSTER --service job-tracker --force-new-deployment
```

**Note**: Since we're using scheduled tasks (not a service), new tasks will automatically use the `:latest` tag on the next run.

## Changing the Schedule

To run more/less frequently, edit `aws/terraform/main.tf`:

```hcl
resource "aws_cloudwatch_event_rule" "job_tracker_schedule" {
  schedule_expression = "rate(6 hours)"  # Change this
}
```

Options:
- `rate(1 hour)` - Every hour
- `rate(12 hours)` - Twice daily
- `rate(1 day)` - Once daily
- `cron(0 9 * * ? *)` - Daily at 9 AM UTC

Then run:
```bash
cd aws/terraform
terraform apply
```

## Troubleshooting

### Task fails to start:
```bash
# Check task logs
aws logs tail /ecs/job-tracker --follow --since 1h

# Check task status
CLUSTER=$(terraform -chdir=aws/terraform output -raw ecs_cluster_name)
aws ecs describe-tasks --cluster $CLUSTER --tasks $(aws ecs list-tasks --cluster $CLUSTER --query 'taskArns[0]' --output text)
```

### DynamoDB connection issues:
- Verify the IAM role has DynamoDB permissions
- Check security group allows outbound traffic
- Verify `DATABASE_TYPE=dynamodb` in task definition

### Chrome/Selenium issues:
- Check CloudWatch logs for browser errors
- Fargate has 4 GB RAM limit; if needed, increase memory in `main.tf`:
  ```hcl
  memory = "2048"  # Increase if Chrome crashes
  ```

### "No space left on device":
- Selenium downloads can fill `/tmp`. Consider cleaning up in scraper code.

## Cost Optimization

### Reduce runtime frequency:
```hcl
schedule_expression = "rate(12 hours)"  # Instead of 6
```

### Reduce task resources:
```hcl
cpu    = "256"   # Minimum (0.25 vCPU)
memory = "512"   # Minimum (0.5 GB)
```

### Use DynamoDB On-Demand pricing:
Already configured! You only pay for what you use.

## Cleanup / Destroy Resources

To delete everything and stop billing:

```bash
# Navigate to Terraform directory
cd aws/terraform

# Destroy all resources
terraform destroy

# Type 'yes' when prompted
```

**Warning**: This will delete:
- All job data in DynamoDB
- Docker images in ECR
- All logs in CloudWatch
- ECS cluster and task definitions

## Security Best Practices

1. **Don't commit AWS credentials**: Never add credentials to `.env` or code
2. **Use IAM roles**: ECS tasks use IAM roles (already configured)
3. **Rotate access keys**: Rotate your AWS CLI access keys every 90 days
4. **Restrict IAM permissions**: The Terraform config uses minimal required permissions
5. **Enable MFA**: Enable multi-factor authentication on your AWS account

## Support

### AWS Free Tier Details:
- [AWS Free Tier](https://aws.amazon.com/free/)
- DynamoDB: 25 GB storage, 25 read/write units
- ECS Fargate: Not free, but very cheap (~$0.04/hour for small tasks)

### Useful AWS Console Links:
- [ECS Clusters](https://console.aws.amazon.com/ecs/v2/clusters)
- [DynamoDB Tables](https://console.aws.amazon.com/dynamodbv2/home#tables)
- [CloudWatch Logs](https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups)
- [ECR Repositories](https://console.aws.amazon.com/ecr/repositories)
- [EventBridge Rules](https://console.aws.amazon.com/events/home#/rules)

### Documentation:
- [ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [EventBridge](https://docs.aws.amazon.com/eventbridge/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Next Steps

1. ✅ Deploy to AWS (you just did this!)
2. Monitor logs after first scheduled run (in ~6 hours)
3. Customize search queries in `variables.tf`
4. Set up email notifications (optional - implement `src/notifications/email_notifier.py`)
5. Create a dashboard in CloudWatch for job metrics (optional)

Happy job hunting! 🎉
