terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB Table for Jobs
resource "aws_dynamodb_table" "jobs" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing (free tier eligible)
  hash_key     = "url"

  attribute {
    name = "url"
    type = "S"
  }

  tags = {
    Name        = "Job Tracker Jobs Table"
    Application = "job-tracker"
  }
}

# ECR Repository for Docker Image
resource "aws_ecr_repository" "job_tracker" {
  name                 = "job-tracker"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "Job Tracker Repository"
    Application = "job-tracker"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "job_tracker" {
  name = "job-tracker-cluster"

  tags = {
    Name        = "Job Tracker Cluster"
    Application = "job-tracker"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "job_tracker" {
  name              = "/ecs/job-tracker"
  retention_in_days = 7 # Keep logs for 7 days

  tags = {
    Name        = "Job Tracker Logs"
    Application = "job-tracker"
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "job-tracker-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "Job Tracker ECS Execution Role"
    Application = "job-tracker"
  }
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Task (application permissions)
resource "aws_iam_role" "ecs_task_role" {
  name = "job-tracker-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "Job Tracker ECS Task Role"
    Application = "job-tracker"
  }
}

# Policy for DynamoDB access
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "job-tracker-dynamodb-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ]
      Resource = aws_dynamodb_table.jobs.arn
    }]
  })
}

# ECS Task Definition
resource "aws_ecs_task_definition" "job_tracker" {
  family                   = "job-tracker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"  # 0.5 vCPU
  memory                   = "1024" # 1 GB RAM
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "job-tracker"
    image = "${aws_ecr_repository.job_tracker.repository_url}:latest"

    environment = [
      {
        name  = "DATABASE_TYPE"
        value = "dynamodb"
      },
      {
        name  = "DYNAMODB_TABLE_NAME"
        value = var.dynamodb_table_name
      },
      {
        name  = "AWS_REGION"
        value = var.aws_region
      },
      {
        name  = "SEARCH_QUERY"
        value = var.search_query
      },
      {
        name  = "LOCATION"
        value = var.location
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.job_tracker.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Name        = "Job Tracker Task Definition"
    Application = "job-tracker"
  }
}

# IAM Role for EventBridge
resource "aws_iam_role" "eventbridge_role" {
  name = "job-tracker-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "Job Tracker EventBridge Role"
    Application = "job-tracker"
  }
}

# Policy to allow EventBridge to run ECS tasks
resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "job-tracker-eventbridge-ecs"
  role = aws_iam_role.eventbridge_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ecs:RunTask"
      ]
      Resource = aws_ecs_task_definition.job_tracker.arn
    }, {
      Effect = "Allow"
      Action = [
        "iam:PassRole"
      ]
      Resource = [
        aws_iam_role.ecs_task_execution_role.arn,
        aws_iam_role.ecs_task_role.arn
      ]
    }]
  })
}

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group for ECS Task
resource "aws_security_group" "ecs_task" {
  name        = "job-tracker-ecs-task"
  description = "Security group for Job Tracker ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  # Allow all outbound traffic (needed for web scraping)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "Job Tracker ECS Task SG"
    Application = "job-tracker"
  }
}

# EventBridge Rule to trigger every 6 hours
resource "aws_cloudwatch_event_rule" "job_tracker_schedule" {
  name                = "job-tracker-schedule"
  description         = "Trigger job tracker every 6 hours"
  schedule_expression = "rate(6 hours)"

  tags = {
    Name        = "Job Tracker Schedule"
    Application = "job-tracker"
  }
}

# EventBridge Target (ECS Task)
resource "aws_cloudwatch_event_target" "ecs_task" {
  rule      = aws_cloudwatch_event_rule.job_tracker_schedule.name
  target_id = "job-tracker-ecs-task"
  arn       = aws_ecs_cluster.job_tracker.arn
  role_arn  = aws_iam_role.eventbridge_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.job_tracker.arn
    launch_type         = "FARGATE"

    network_configuration {
      subnets          = data.aws_subnets.default.ids
      security_groups  = [aws_security_group.ecs_task.id]
      assign_public_ip = true # Required for pulling from ECR and internet access
    }
  }
}
