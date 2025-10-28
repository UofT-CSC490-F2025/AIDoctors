terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
    backend "s3" {
        bucket         = "aidoctors-terraform-state"
        key            = "prod/terraform.tfstate"
        region         = "us-east-2"
        encrypt        = true
        use_lockfile   = true
    }
}

provider "aws" {
    region = "us-east-2"
}

resource "aws_s3_bucket" "test" {
    bucket = "test-bucket"
}
    