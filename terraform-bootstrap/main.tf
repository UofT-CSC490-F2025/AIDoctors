terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  # Bootstrap state stored in a manually-created S3 bucket
  # This bucket must be created manually before running terraform init
  backend "s3" {
    bucket  = "aidoctors-tf-bootstrap-state"
    key     = "bootstrap/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}
