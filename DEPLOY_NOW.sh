#!/bin/bash
# Quick Deploy Script - Deploy Schema Changes to AWS
# Run this script to deploy your updated job tracker with new fields

set -e  # Exit on error

echo "=================================="
echo "Job Tracker - AWS Deployment"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install: https://aws.amazon.com/cli/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install: https://www.docker.com/get-started"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Install: https://www.terraform.io/downloads"
    exit 1
fi

echo "✅ All prerequisites installed"
echo ""

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS credentials configured"
echo ""

# Get ECR repository URL
echo "Getting ECR repository URL..."
cd aws/terraform

if [ ! -f "terraform.tfstate" ]; then
    echo "❌ Terraform state not found. Have you run 'terraform apply' yet?"
    echo "If this is your first deployment, follow: aws/QUICK_START.md"
    exit 1
fi

ECR_REPO=$(terraform output -raw ecr_repository_url 2>/dev/null || echo "")

if [ -z "$ECR_REPO" ]; then
    echo "❌ Could not get ECR repository URL"
    echo "Run 'terraform apply' in aws/terraform first"
    exit 1
fi

echo "✅ ECR Repository: $ECR_REPO"
cd ../..
echo ""

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $ECR_REPO

if [ $? -ne 0 ]; then
    echo "❌ ECR login failed"
    exit 1
fi

echo "✅ ECR login successful"
echo ""

# Build Docker image
echo "Building Docker image..."
echo "This may take a few minutes..."
docker build -t job-tracker .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Tag image
echo "Tagging image..."
docker tag job-tracker:latest $ECR_REPO:latest

echo "✅ Image tagged"
echo ""

# Push image
echo "Pushing image to ECR..."
echo "This may take a few minutes..."
docker push $ECR_REPO:latest

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    exit 1
fi

echo "✅ Image pushed to ECR"
echo ""

# Optional: Force new deployment
echo "Do you want to force ECS to use the new image immediately? (y/n)"
echo "(If you select 'n', the new image will be used on the next scheduled run)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Forcing new deployment..."

    CLUSTER=$(cd aws/terraform && terraform output -raw ecs_cluster_name)

    # Check if service exists
    SERVICE_COUNT=$(aws ecs list-services --cluster $CLUSTER --query 'serviceArns' --output text | wc -w)

    if [ "$SERVICE_COUNT" -gt 0 ]; then
        aws ecs update-service \
            --cluster $CLUSTER \
            --service job-tracker-service \
            --force-new-deployment > /dev/null

        echo "✅ Deployment forced. New task will start soon."
    else
        echo "ℹ️  No service found. The new image will be used on the next scheduled run."
    fi
else
    echo "ℹ️  Skipping forced deployment. New image will be used on next scheduled run."
fi

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "What's Next:"
echo ""
echo "1. View logs:"
echo "   aws logs tail /ecs/job-tracker --follow"
echo ""
echo "2. Check recent jobs in DynamoDB:"
echo "   aws dynamodb scan --table-name job-tracker-jobs --max-items 5"
echo ""
echo "3. Verify new fields are being extracted:"
echo "   Look for 'job_type', 'work_mode', 'experience_level' in the scan results"
echo ""
echo "4. Monitor task runs:"
echo "   aws ecs list-tasks --cluster job-tracker-cluster"
echo ""
echo "Cost: ~\$1-2/month (mostly free for first 12 months)"
echo ""
echo "=================================="
