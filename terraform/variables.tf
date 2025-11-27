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

variable "pipeline_schedule" {
  description = "Cron expression for pipeline schedule (default: daily at 2 AM UTC)"
  type        = string
  default     = "cron(0 0 1 * ? *)"
}