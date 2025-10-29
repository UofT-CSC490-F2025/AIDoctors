module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${local.name}-db"

  # PostgreSQL Configuration
  engine                   = "postgres"
  engine_version           = "15.4"
  engine_lifecycle_support = "open-source-rds-extended-support-disabled"
  family                   = "postgres15" # DB parameter group
  major_engine_version     = "15"         # DB option group
  instance_class           = "db.t4g.small"

  # Storage Configuration
  allocated_storage     = 30
  max_allocated_storage = 50

  # Database Configuration
  db_name  = "${local.name}-db"
  username = "aidoctors_admin"
  port     = 5432

  # Password Management - RDS will manage the password automatically
  manage_master_user_password_rotation              = true
  master_user_password_rotate_immediately           = false
  master_user_password_rotation_schedule_expression = "rate(30 days)"

  # High Availability & Networking
  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.rds_security_group.security_group_id]

  # IAM Authentication
  iam_database_authentication_enabled = true

  # Maintenance & Backup Windows
  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  backup_retention_period         = 7 # Keep backups for 7 days
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  # Enhanced Monitoring
  monitoring_interval    = 60
  create_monitoring_role = true
  monitoring_role_name   = "${local.name}-rds-monitoring-role"

  # Deletion Protection
  deletion_protection = true
  skip_final_snapshot = false

  # PostgreSQL Parameters
  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    },
    {
      name  = "log_connections"
      value = 1
    }
  ]

  tags = {
    Name = "${local.name}-postgres"
  }
}