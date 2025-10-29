# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name}"
  retention_in_days = 7

  tags = {
    Name = "${local.name}-ecs-logs"
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

# ECS Task Definition
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
      name      = "${local.name}-container"
      image     = "${module.ecr.repository_url}:latest"
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
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = "us-east-2"
          "awslogs-stream-prefix" = "ecs"
        }
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
    Name = "${local.name}-task-definition"
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${local.name}-service"
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
    container_name   = "${local.name}-container"
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
    Name = "${local.name}-ecs-service"
  }
}