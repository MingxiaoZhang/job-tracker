output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.job_tracker.repository_url
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.jobs.name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.job_tracker.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for ECS tasks"
  value       = aws_cloudwatch_log_group.job_tracker.name
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge schedule rule"
  value       = aws_cloudwatch_event_rule.job_tracker_schedule.name
}
