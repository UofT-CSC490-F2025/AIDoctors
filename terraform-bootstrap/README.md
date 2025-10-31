# Terraform Bootstrap

This directory contains the bootstrap infrastructure that must be created **before** the main Terraform configuration can run.

## What This Creates

1. **S3 Bucket** (`aidoctors-terraform-state`) - Stores Terraform state files
2. **GitHub OIDC Provider** - Allows GitHub Actions to authenticate with AWS without access keys
3. **IAM Role** - Role that GitHub Actions assumes to deploy infrastructure

## Why Separate Bootstrap?

The main Terraform configuration uses an S3 backend to store its state. However, you can't use an S3 bucket as a backend if it doesn't exist yet. This bootstrap configuration solves the "chicken and egg" problem by:

-   Using **local state** (stored in this directory)
-   Creating the S3 bucket and supporting resources
-   Being run **once** manually before the CI/CD pipeline

## Prerequisites

### 1. Install AWS CLI

```bash
brew install awscli
```

Or download from: https://aws.amazon.com/cli/

### 2. Install Terraform

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

Or download from: https://www.terraform.io/downloads

### 3. Configure AWS Credentials

You need AWS credentials with permissions to create S3 buckets, IAM roles, and OIDC providers.

**Option A: AWS SSO (Recommended for organizations)**

```bash
aws configure sso
```

This will prompt for your SSO start URL and region. After authentication, your credentials will be managed automatically.

**Option B: AWS CLI Configure (For IAM users)**

```bash
aws configure
```

This will prompt for:

-   AWS Access Key ID
-   AWS Secret Access Key
-   Default region (use: `us-east-1`)
-   Default output format (optional, e.g., `json`)

Credentials are stored in `~/.aws/credentials`

**Option C: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Verify AWS Access**

```bash
# Check your AWS identity
aws sts get-caller-identity

# Should return your account ID and user/role ARN
```

## Setup Instructions

### 1. Create Bootstrap State Bucket

Before running Terraform, you need to manually create an S3 bucket for the bootstrap state:

**Via AWS CLI:**

```bash
# Create the bucket
aws s3api create-bucket \
  --bucket aidoctors-tf-bootstrap-state \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket aidoctors-tf-bootstrap-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket aidoctors-tf-bootstrap-state \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Block public access
aws s3api put-public-access-block \
  --bucket aidoctors-tf-bootstrap-state \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 2. Update Configuration

Edit `terraform.tfvars` and update:

-   `github_repo` - Your GitHub repository (e.g., "your-org/AIDoctors")
-   Other values as needed

### 3. Run Bootstrap

```bash
cd terraform-bootstrap

# Initialize Terraform (connects to the S3 backend)
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

**Note:** All team members can now run `terraform init` and share the same state from S3. No need to pass state files around!

### 4. Verify Bootstrap Outputs

After applying, note the outputs:

```bash
terraform output
```

You'll see:

-   `state_bucket_name` - S3 bucket for Terraform state
-   `state_bucket_arn` - ARN of the state bucket
-   `github_actions_role_arn` - IAM role for GitHub Actions (for OIDC)

### 5. Migrate to OIDC Authentication

Instead of using AWS access keys in GitHub secrets, you can use the IAM role created by this bootstrap:

Update `.github/workflows/deploy.yaml`:

```yaml
- name: "Configure AWS credentials"
  uses: aws-actions/configure-aws-credentials@v4
  with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }} # ARN from bootstrap output
      aws-region: ${{ env.AWS_REGION }}
```

## State Management

**Bootstrap state is stored in S3**: `s3://aidoctors-terraform-bootstrap-state/bootstrap/terraform.tfstate`

**The Two-Tier State Strategy:**

1. **Bootstrap state** → Stored in manually-created S3 bucket (`aidoctors-terraform-bootstrap-state`)
2. **Application state** → Stored in Terraform-managed S3 bucket (`aidoctors-terraform-state`)

## Updating Bootstrap

If you need to modify the bootstrap infrastructure:

```bash
cd terraform-bootstrap
terraform plan
terraform apply
```

## Destroying Bootstrap

Only destroy bootstrap infrastructure if you're tearing down the entire project:

```bash
cd terraform-bootstrap
terraform destroy
```

## Outputs

After applying, you'll see:

-   `state_bucket_name` - Use this in your main Terraform backend config
-   `dynamodb_table_name` - Use this for state locking
-   `github_actions_role_arn` - Use this for OIDC authentication (optional)
