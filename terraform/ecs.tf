# CloudWatch Log Group for Application
resource "aws_cloudwatch_log_group" "ecs_app" {
  name              = "/ecs/${local.name}-app"
  retention_in_days = 7

  tags = {
    Name = "${local.name}-app-logs"
  }
}

# CloudWatch Log Group for Data Pipeline
resource "aws_cloudwatch_log_group" "ecs_datapipeline" {
  name              = "/ecs/${local.name}-datapipeline"
  retention_in_days = 7

  tags = {
    Name = "${local.name}-datapipeline-logs"
  }
}

# ECS Cluster
module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 5.0"

  cluster_name = "${local.name}-cluster"

  # Fargate capacity providers
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 50
        base   = 20
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
  }

  tags = {
    Name = "${local.name}-ecs-cluster"
  }
}

# ECS Task Definition for Application
resource "aws_ecs_task_definition" "app" {
  family                   = "${local.name}-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 512 MB
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${local.name}-app-container"
      image     = "${module.ecr_app.repository_url}:${var.app_image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_app.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "app"
        }
        depends_on = [aws_cloudwatch_log_group.ecs_app]
      }

      # Update After Deployment
      #   healthCheck = {
      #     command     = ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
      #     interval    = 30
      #     timeout     = 5
      #     retries     = 3
      #     startPeriod = 60
      #   }
    }
  ])

  tags = {
    Name = "${local.name}-app-task-definition"
  }
}

# ECS Task Definition for Data Pipeline
resource "aws_ecs_task_definition" "pipeline" {
  family                   = "${local.name}-pipeline"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512" # 0.5 vCPU
  memory                   = "1024" # 1 GB
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${local.name}-pipeline-container"
      image     = "${module.ecr_pipeline.repository_url}:${var.pipeline_image_tag}"
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_datapipeline.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "pipeline"
        }
        depends_on = [aws_cloudwatch_log_group.ecs_datapipeline]
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = "production"
        }
      ]
    }
  ])

  tags = {
    Name = "${local.name}-pipeline-task-definition"
  }
}

# ECS Service for Application
resource "aws_ecs_service" "app" {
  name            = "${local.name}-app-service"
  cluster         = module.ecs_cluster.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 0

  launch_type = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = module.alb.target_groups["aidoctors-application"].arn
    container_name   = "${local.name}-app-container"
    container_port   = 80
  }

  # Allow external changes without Terraform plan difference
  lifecycle {
    ignore_changes = [desired_count]
  }

  depends_on = [
    module.alb
  ]

  tags = {
    Name = "${local.name}-app-service"
  }
}

# ECS Service for Data Pipeline
resource "aws_ecs_service" "pipeline" {
  name            = "${local.name}-pipeline-service"
  cluster         = module.ecs_cluster.id
  task_definition = aws_ecs_task_definition.pipeline.arn
  desired_count   = 0

  launch_type = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # Allow external changes without Terraform plan difference
  lifecycle {
    ignore_changes = [desired_count]
  }

  tags = {
    Name = "${local.name}-pipeline-service"
  }
}