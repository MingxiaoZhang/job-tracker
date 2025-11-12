variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for job storage"
  type        = string
  default     = "job-tracker-jobs"
}

variable "search_query" {
  description = "Job search query"
  type        = string
  default     = "software engineer"
}

variable "location" {
  description = "Job location"
  type        = string
  default     = "Remote"
}
