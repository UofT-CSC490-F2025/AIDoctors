# ECR Repository for Application
module "ecr_app" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.0"

  repository_name = "${local.name}-app"

  # Lifecycle policy to manage image retention
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Remove untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })

  # Enable image scanning
  repository_image_scan_on_push = true

  # Enable encryption
  repository_encryption_type = "AES256"

  # Force delete on destroy
  repository_force_delete = true

  tags = {
    Name = "${local.name}-app-ecr"
  }
}

# ECR Repository for Data Pipeline
module "ecr_pipeline" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.0"

  repository_name = "${local.name}-pipeline"

  # Lifecycle policy to manage image retention
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Remove untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })

  # Enable image scanning
  repository_image_scan_on_push = true

  # Enable encryption
  repository_encryption_type = "AES256"

  # Force delete on destroy
  repository_force_delete = true

  tags = {
    Name = "${local.name}-pipeline-ecr"
  }
}
  