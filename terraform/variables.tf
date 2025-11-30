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

variable "extraction_image_tag" {
  description = "Docker image tag for data extraction"
  type        = string
  default     = "latest"
}

variable "extraction_schedule" {
  description = "Cron expression for extraction schedule (default: daily at 1:00 AM UTC)"
  type        = string
  default     = "cron(0 1 * * ? *)"
}

variable "pipeline_schedule" {
  description = "Cron expression for pipeline schedule (default: daily at 1:30 AM UTC, 30 minutes after extraction)"
  type        = string
  default     = "cron(30 1 * * ? *)"
}