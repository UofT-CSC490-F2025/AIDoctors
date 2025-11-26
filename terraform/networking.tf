# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "aidoctors-vpc"
  cidr = local.cidr

  azs              = local.azs
  public_subnets   = local.public_subnets
  private_subnets  = local.private_subnets
  database_subnets = local.database_subnets

  enable_nat_gateway   = true
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${local.name}-vpc"
  }
}

# DB Subnet Group for public access (development)
resource "aws_db_subnet_group" "public" {
  name       = "${local.name}-public-db-subnet-group"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "${local.name}-public-db-subnet-group"
  }
}

