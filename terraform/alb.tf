# Application Load Balancer
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "${local.name}-alb"
  load_balancer_type = "application"
  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets
  internal           = false
  enable_deletion_protection = false

  security_groups = [aws_security_group.alb.id]

  access_logs = {
    bucket = module.s3_alb_logs.s3_bucket_id
  }

  listeners = {
    http = {
      port     = 80
      protocol = "HTTP"

      forward = {
        target_group_key = "aidoctors-application"
      }
    }
  }

  target_groups = {
    aidoctors-application = {
      name_prefix                       = "aid"
      protocol                          = "HTTP"
      port                              = 8000
      target_type                       = "ip"
      vpc_id                            = module.vpc.vpc_id
      deregistration_delay              = 30

      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 30
        path                = "/"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 3
        matcher             = "200-299"
      }

      create_attachment = false
    }
  }

  depends_on = [module.vpc]

  tags = {
    Name = "${local.name}-alb"
  }
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "${local.name}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name}-alb-sg"
  }
}
