# AWS Systems Manager Parameter Store for Application Environment Variables

# Database connection parameters
resource "aws_ssm_parameter" "db_host" {
  name        = "/${local.name}/db/host"
  description = "RDS PostgreSQL hostname"
  type        = "String"
  value       = module.db.db_instance_address

  tags = {
    Name = "${local.name}-db-host"
  }
}

resource "aws_ssm_parameter" "db_port" {
  name        = "/${local.name}/db/port"
  description = "RDS PostgreSQL port"
  type        = "String"
  value       = tostring(module.db.db_instance_port)

  tags = {
    Name = "${local.name}-db-port"
  }
}

resource "aws_ssm_parameter" "db_name" {
  name        = "/${local.name}/db/name"
  description = "RDS PostgreSQL database name"
  type        = "String"
  value       = module.db.db_instance_name

  tags = {
    Name = "${local.name}-db-name"
  }
}

resource "aws_ssm_parameter" "db_user" {
  name        = "/${local.name}/db/user"
  description = "RDS PostgreSQL username"
  type        = "String"
  value       = module.db.db_instance_username

  tags = {
    Name = "${local.name}-db-user"
  }
}

# Database schema for pipeline
resource "aws_ssm_parameter" "db_schema" {
  name        = "/${local.name}/db/schema"
  description = "PostgreSQL schema name"
  type        = "String"
  value       = "production"

  tags = {
    Name = "${local.name}-db-schema"
  }
}

# Database password secret ARN (stored in Secrets Manager)
resource "aws_ssm_parameter" "db_password_secret_arn" {
  name        = "/${local.name}/db/password-secret-arn"
  description = "ARN of the RDS master user secret in Secrets Manager"
  type        = "String"
  value       = module.db.db_instance_master_user_secret_arn

  tags = {
    Name = "${local.name}-db-password-secret-arn"
  }
}

# S3 bucket names
resource "aws_ssm_parameter" "s3_raw_datasets_bucket" {
  name        = "/${local.name}/s3/raw-datasets-bucket"
  description = "S3 bucket name for raw datasets"
  type        = "String"
  value       = module.s3_raw_datasets.s3_bucket_id

  tags = {
    Name = "${local.name}-s3-raw-datasets-bucket"
  }
}

resource "aws_ssm_parameter" "s3_raw_datasets_prefix" {
  name        = "/${local.name}/s3/raw-datasets-prefix"
  description = "S3 prefix for raw datasets"
  type        = "String"
  value       = "raw_datasets/"

  tags = {
    Name = "${local.name}-s3-raw-datasets-prefix"
  }
}

# Application secrets (use SecureString for sensitive data)
resource "aws_ssm_parameter" "access_token_secret" {
  name        = "/${local.name}/app/access-token-secret"
  description = "JWT access token secret key"
  type        = "SecureString"
  value       = random_password.access_token_secret.result

  tags = {
    Name = "${local.name}-access-token-secret"
  }
}

# Generate random password for JWT secret
resource "random_password" "access_token_secret" {
  length  = 64
  special = true
}
