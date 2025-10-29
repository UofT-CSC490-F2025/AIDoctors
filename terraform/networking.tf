# VPC
module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    name = "aidoctors-vpc"
    cidr = "10.0.0.0/16"

    azs = ["us-east-2a", "us-east-2b", "us-east-2c"]
    public_subnets = ["10.0.1.0/24", "10.0.4.0/24"]
    private_subnets = ["10.0.2.0/24", "10.0.5.0/24"]
    database_subnets = ["10.0.3.0/24", "10.0.6.0/24"]

    enable_nat_gateway = true
    enable_dns_support   = true
    enable_dns_hostnames = true
    
    tags = {
        Name = "AIDoctors VPC"
    }
}