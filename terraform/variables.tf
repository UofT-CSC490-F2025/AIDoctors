variable "app_image_tag" {
  description = "Docker image tag for application"
  type        = string
  default     = "latest"
}

variable "pipeline_image_tag" {
  description = "Docker image tag for data pipeline"
  type        = string
  default     = "latest"
}

variable "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions"
  type        = string
}

variable "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  type        = string
}

variable "state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  type        = string
}

variable "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  type        = string
}
