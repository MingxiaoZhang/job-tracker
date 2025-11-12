# Quick Start - AWS Deployment

Deploy your job tracker to AWS in 5 minutes!

## Prerequisites

- AWS Account ([sign up](https://aws.amazon.com/free/))
- AWS CLI installed
- Terraform installed
- Docker installed

## Deploy in 5 Steps

### 1. Configure AWS

```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
# Region: us-east-1
# Output format: json
```

### 2. Deploy Infrastructure

```bash
cd aws/terraform
terraform init
terraform apply
# Type 'yes' when prompted
```

### 3. Build & Push Docker Image

```bash
cd ../..  # Back to project root

# Get ECR URL
ECR_REPO=$(terraform -chdir=aws/terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build and push
docker build -t job-tracker .
docker tag job-tracker:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### 4. Verify Deployment

```bash
# Watch logs (wait for first scheduled run in ~6 hours, or trigger manually)
aws logs tail /ecs/job-tracker --follow
```

### 5. Check Your Jobs

```bash
# View jobs in DynamoDB
aws dynamodb scan --table-name job-tracker-jobs --max-items 5
```

## Done! 🎉

Your job tracker now runs automatically every 6 hours on AWS Fargate.

**Cost**: ~$1-2/month (mostly free for first 12 months)

## Quick Commands

```bash
# View logs
aws logs tail /ecs/job-tracker --follow

# Disable schedule
aws events disable-rule --name job-tracker-schedule

# Enable schedule
aws events enable-rule --name job-tracker-schedule

# Manual run
cd aws/terraform
CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEF=$(aws ecs list-task-definitions --family-prefix job-tracker --query 'taskDefinitionArns[0]' --output text)
SUBNETS=$(aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')
SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=job-tracker-ecs-task" --query 'SecurityGroups[0].GroupId' --output text)

aws ecs run-task \
  --cluster $CLUSTER \
  --task-definition $TASK_DEF \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=ENABLED}"

# Destroy everything
cd aws/terraform
terraform destroy
```

## Customize

Edit `aws/terraform/variables.tf`:
- `search_query`: Your job search terms
- `location`: Job location
- `aws_region`: AWS region

Then run `terraform apply` again.

---

**Need help?** See full guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
