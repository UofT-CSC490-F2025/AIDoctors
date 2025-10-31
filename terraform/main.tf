terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    bucket       = "aidoctors-tf-state"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "us-east-1"
}


locals {
  name             = "aidoctors"
  cidr             = "10.0.0.0/16"
  azs              = ["us-east-1a", "us-east-1c"]
  public_subnets   = ["10.0.1.0/24", "10.0.4.0/24"]
  private_subnets  = ["10.0.2.0/24", "10.0.5.0/24"]
  database_subnets = ["10.0.3.0/24", "10.0.6.0/24"]
}
