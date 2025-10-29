# Route 53 Hosted Zone and Records Module
module "route53_zone" {
  source  = "terraform-aws-modules/route53/aws//modules/zones"
  version = "~> 4.0"

  zones = {
    "aidoctors.com" = {
      comment = "Hosted zone for AIDoctors application"
      tags = {
        Name = "${local.name}-hosted-zone"
      }
    }
  }

  tags = {
    Name = "${local.name}-route53"
  }
}

# Route 53 Record for root domain
resource "aws_route53_record" "root" {
  zone_id = module.route53_zone.route53_zone_zone_id["aidoctors.com"]
  name    = "aidoctors.com"
  type    = "A"

  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = true
  }

  depends_on = [module.route53_zone, module.alb]
}

# Route 53 Record for wildcard subdomain - used to separate Prod and Dev Environments later on
# resource "aws_route53_record" "wildcard" {
#   zone_id = module.route53_zone.route53_zone_zone_id["aidoctors.com"]
#   name    = "*.aidoctors.com"
#   type    = "A"

#   alias {
#     name                   = module.alb.dns_name
#     zone_id                = module.alb.zone_id
#     evaluate_target_health = true
#   }

#   depends_on = [module.route53_zone, module.alb]
# }

# ACM Certificate Module
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 5.0"

  domain_name = "aidoctors.com"
  zone_id     = module.route53_zone.route53_zone_zone_id["aidoctors.com"]

  subject_alternative_names = [
    "*.aidoctors.com"
  ]

  validation_method   = "DNS"
  wait_for_validation = true

  tags = {
    Name = "${local.name}-certificate"
  }
}