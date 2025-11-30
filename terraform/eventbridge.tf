# IAM Role for EventBridge Scheduler
resource "aws_iam_role" "eventbridge_scheduler" {
  name = "${local.name}-eventbridge-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${local.name}-eventbridge-scheduler-role"
  }
}

# IAM Policy for EventBridge to run ECS tasks
resource "aws_iam_role_policy" "eventbridge_scheduler_policy" {
  name = "${local.name}-eventbridge-scheduler-policy"
  role = aws_iam_role.eventbridge_scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = [
          aws_ecs_task_definition.pipeline.arn_without_revision,
          "${aws_ecs_task_definition.pipeline.arn_without_revision}:*",
          aws_ecs_task_definition.extraction.arn_without_revision,
          "${aws_ecs_task_definition.extraction.arn_without_revision}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      }
    ]
  })
}

# EventBridge Scheduler for Data Extraction
resource "aws_scheduler_schedule" "extraction" {
  name       = "${local.name}-extraction-schedule"
  group_name = "default"

  schedule_expression = var.extraction_schedule

  flexible_time_window {
    mode = "FLEXIBLE"
    maximum_window_in_minutes = 60
  }

  target {
    arn      = module.ecs_cluster.arn
    role_arn = aws_iam_role.eventbridge_scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.extraction.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_tasks.id]
        assign_public_ip = false
      }

      # Enable CloudWatch Logs
      enable_ecs_managed_tags = true
      enable_execute_command  = false
      
      # Propagate tags from task definition
      propagate_tags = "TASK_DEFINITION"
    }

    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }
}

# EventBridge Scheduler for Data Pipeline
# Runs 30 minutes after extraction to ensure data is available
resource "aws_scheduler_schedule" "pipeline" {
  name       = "${local.name}-pipeline-schedule"
  group_name = "default"

  schedule_expression = var.pipeline_schedule

  flexible_time_window {
    mode = "FLEXIBLE"
    maximum_window_in_minutes = 60
  }

  target {
    arn      = module.ecs_cluster.arn
    role_arn = aws_iam_role.eventbridge_scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_tasks.id]
        assign_public_ip = false
      }

      # Enable CloudWatch Logs
      enable_ecs_managed_tags = true
      enable_execute_command  = false
      
      # Propagate tags from task definition
      propagate_tags = "TASK_DEFINITION"
    }

    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }
}

# Output the schedule ARNs
output "extraction_schedule_arn" {
  description = "ARN of the EventBridge schedule for the data extraction"
  value       = aws_scheduler_schedule.extraction.arn
}

output "pipeline_schedule_arn" {
  description = "ARN of the EventBridge schedule for the data pipeline"
  value       = aws_scheduler_schedule.pipeline.arn
}
