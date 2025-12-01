variable "app_image_tag" {
  description = "Docker image tag for application"
  type        = string
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
  description = "Cron expression for extraction schedule "
  type        = string
  default     = "cron(0 0 1 * ? *)"
}

variable "pipeline_schedule" {
  description = "Cron expression for pipeline schedule "
  type        = string
  default     = "cron(30 0 1 * ? *)"
}