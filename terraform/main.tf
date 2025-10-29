terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    bucket       = "aidoctors-terraform-state"
    key          = "prod/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "us-east-2"
}


locals {
  name             = "AIDoctors"
  cidr             = "10.0.0.0/16"
  azs              = ["us-east-2a", "us-east-2b", "us-east-2c"]
  public_subnets   = ["10.0.1.0/24", "10.0.4.0/24"]
  private_subnets  = ["10.0.2.0/24", "10.0.5.0/24"]
  database_subnets = ["10.0.3.0/24", "10.0.6.0/24"]
}
