module "nlb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "${local.name}-nlb"
  load_balancer_type = "network"
  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets
  enable_deletion_protection = false
  internal           = false

  # NLB doesn't use security groups, uses target security groups instead
  enable_cross_zone_load_balancing = true

  access_logs = {
    bucket = module.s3_alb_logs.s3_bucket_id
  }

  listeners = {
    ex-http = {
      port     = 80
      protocol = "TCP"

      forward = {
        target_group_key = "aidoctors-application"
      }
    }
  }

  target_groups = {
    aidoctors-application = {
      name_prefix                       = "aid"
      protocol                          = "TCP"
      port                              = 8000
      target_type                       = "ip" # Use 'ip' for Fargate tasks
      vpc_id                            = module.vpc.vpc_id
      deregistration_delay              = 30
      preserve_client_ip                = false

      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 10
        port                = 8000
        protocol            = "HTTP"
        path                = "/"
        timeout             = 6
        unhealthy_threshold = 2
        matcher             = "200-299"
      }

      create_attachment = false
    }
  }

  depends_on = [module.vpc]

  tags = {
    Name = "${local.name}-nlb"
  }
}