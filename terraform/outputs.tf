output "db_instance_master_user_secret_arn" {
  description = "The ARN of the master user secret"
  value       = module.db.db_instance_master_user_secret_arn
}