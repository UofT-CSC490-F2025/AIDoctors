output "db_instance_master_user_secret_arn" {
  description = "The ARN of the master user secret"
  value       = module.db.db_instance_master_user_secret_arn
}

output "ssm_parameter_prefix" {
  description = "SSM Parameter Store prefix for application environment variables"
  value       = "/${local.name}/"
}

output "ssm_parameters" {
  description = "Map of SSM parameter names"
  value = {
    db_host                = aws_ssm_parameter.db_host.name
    db_port                = aws_ssm_parameter.db_port.name
    db_name                = aws_ssm_parameter.db_name.name
    db_user                = aws_ssm_parameter.db_user.name
    db_schema              = aws_ssm_parameter.db_schema.name
    db_password_secret_arn = aws_ssm_parameter.db_password_secret_arn.name
    s3_raw_datasets_bucket = aws_ssm_parameter.s3_raw_datasets_bucket.name
    s3_raw_datasets_prefix = aws_ssm_parameter.s3_raw_datasets_prefix.name
    access_token_secret    = aws_ssm_parameter.access_token_secret.name
  }
}

output "alb_dns_name" {
  description = "ALB DNS name for accessing the application"
  value       = module.alb.dns_name
}

output "app_image_tag" {
  description = "Current application image tag deployed"
  value       = var.app_image_tag
}
