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