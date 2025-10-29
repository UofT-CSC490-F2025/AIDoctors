# AIDoctors Terraform Infrastructure

This directory contains the Infrastructure as Code (IaC) for the AIDoctors application, deployed on AWS using Terraform.

## Getting Started

1. Download Terraform locally from [Hashicorp](https://developer.hashicorp.com/terraform/install)
2. Install tfsec: `brew install tfsec`
3. Install tflint: `brew install tflint`

## Architecture Overview

The infrastructure deploys a highly available, scalable web application using AWS services with the following architecture:

-   **Compute**: ECS Fargate for containerized application hosting
-   **Load Balancing**: Application Load Balancer (ALB) for traffic distribution
-   **Database**: RDS PostgreSQL with Multi-AZ deployment
-   **Networking**: VPC with public, private, and database subnets across multiple availability zones
-   **Container Registry**: ECR for Docker image storage
-   **DNS**: Route 53 for domain management
-   **Storage**: S3 for ALB access logs
-   **Monitoring**: CloudWatch for logs and metrics

## AWS Resources Deployed

### Networking (`networking.tf`)

-   **VPC**: Custom VPC with CIDR block

### Security Groups (`security_groups.tf`)

-   **RDS Security Group**: Controls access to PostgreSQL database
-   **ECS Tasks Security Group**: Controls access to ECS containers

### Application Load Balancer (`alb.tf`)

-   **ALB**: Internet-facing load balancer in public subnets
    -   HTTP listener on port 80 (forwards to ECS tasks)
    -   HTTPS listener on port 443 (commented out, pending domain registration)
    -   Target group for ECS Fargate tasks with health checks
    -   Access logs stored in S3

### ECS Cluster & Service (`ecs.tf`)

-   **ECS Cluster**: Fargate-based cluster with capacity providers
-   **Task Definition**:
    -   CPU: 256 (0.25 vCPU)
    -   Memory: 512 MB
    -   Container port: 80
    -   CloudWatch Logs integration
-   **ECS Service**:
    -   Desired count: 0 (scale up as needed)
    -   Private subnet deployment
    -   Integrated with ALB target group

### RDS PostgreSQL Database (`rds.tf`)

-   **Engine**: PostgreSQL 17.6
-   **Instance Class**: db.t4g.micro
-   **Storage**: 20 GB allocated, auto-scaling up to 50 GB
-   **High Availability**: Multi-AZ deployment enabled
-   **Security Features**:
    -   Automated password rotation (30-day cycle)
    -   IAM database authentication enabled
    -   Deletion protection enabled
    -   Automated backups (7-day retention)
    -   Enhanced monitoring (60-second intervals)
-   **Maintenance**: Automated during Monday 00:00-03:00 window
-   **Logging**: PostgreSQL and upgrade logs exported to CloudWatch

### Elastic Container Registry (`ecr.tf`)

-   **Repository**: Stores Docker images for the application
-   **Image Scanning**: Enabled on push for security vulnerabilities
-   **Lifecycle Policy**:
    -   Keeps last 5 tagged images (prefix: `v`)
    -   Removes untagged images after 7 days
-   **Encryption**: AES256 encryption at rest

### Route 53 DNS (`route53.tf`)

-   **Hosted Zone**: `aidoctors.com`
-   **A Record**: Points root domain to ALB
-   **ACM Certificate**: Commented out (pending domain ownership verification)
-   **Wildcard Subdomain**: Commented out (for future prod/dev environment separation)

### S3 Storage (`s3.tf`)

-   **ALB Logs Bucket**: Stores Application Load Balancer access logs
    -   Versioning enabled
    -   Server-side encryption (AES256)
    -   Lifecycle rules:
        -   Transition to STANDARD_IA after 30 days
        -   Transition to GLACIER after 90 days
        -   Expiration after 365 days
    -   Public access blocked

### IAM Roles & Policies (`iam.tf`)

-   **ECS Task Execution Role**: Used by ECS to manage containers
    -   ECR image pull permissions
    -   CloudWatch Logs write permissions
-   **ECS Task Role**: Used by application containers
    -   CloudWatch Logs access
    -   S3, ECR, ECS, and RDS permissions

### State Management (`main.tf`)

-   **Backend**: S3 backend for remote state storage
    -   Bucket: `aidoctors-terraform-state`
    -   Key: `prod/terraform.tfstate`
    -   Region: `us-east-2`
    -   Encryption enabled
    -   State locking enabled

## Deployment Strategy

The infrastructure is deployed automatically using GitHub Actions workflows with a GitOps approach.

### Workflow: Terraform PR Check (`.github/workflows/terraform-pr-check.yaml`)

**Trigger**: Pull requests to `main` branch with changes in `terraform/**`

**Purpose**: Validate and preview infrastructure changes before merging

**Steps**:

1. **Checkout**: Clone repository code
2. **Setup Terraform**: Install Terraform v1.13.4
3. **AWS Authentication**: Assume AWS role using OIDC
4. **Linting & Security**:
5. **Terraform Validation**:
6. **PR Comment**: Post plan output as a comment on the PR for review

### Workflow: Terraform CI/CD (`.github/workflows/deploy.yaml`)

**Trigger**:

-   Push to `main` branch with changes in `terraform/**`
-   Manual workflow dispatch

**Purpose**: Automatically apply approved infrastructure changes

**Steps**:

1. **Checkout**: Clone repository code
2. **Setup Terraform**: Install Terraform v1.13.4
3. **AWS Authentication**: Assume AWS role using OIDC (prod environment)
4. **Terraform Deployment**:

**Environment**: Production (`prod`)

### Deployment Flow

```
Developer makes changes
        ↓
Create Pull Request
        ↓
PR Check Workflow runs
  - Validates code
  - Runs security checks
  - Generates plan
  - Posts plan to PR
        ↓
Team reviews plan
        ↓
PR approved & merged to main
        ↓
Deploy Workflow runs
  - Applies changes automatically
        ↓
Infrastructure updated in AWS
```

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **S3 Backend**: Bootstrap S3 bucket for Terraform state (see `terraform-bootstrap/`)
3. **GitHub Secrets**: Configure the following secrets:
    - `AWS_ROLE_ARN`: ARN of the IAM role for GitHub Actions OIDC
4. **Domain**: Register `aidoctors.com` domain (for Route 53 and ACM)

## Future Enhancements

-   [ ] Enable HTTPS with ACM certificate
-   [ ] Implement ECS auto-scaling based on CPU/memory
-   [ ] Add RDS read replicas for read-heavy workloads
-   [ ] Implement AWS WAF for security
-   [ ] Add CloudFront CDN for static assets
-   [ ] Separate dev/staging/prod environments
-   [ ] Implement AWS Secrets Manager for application secrets
