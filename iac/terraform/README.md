# DomainPing Frontend Infrastructure (Terraform)

This directory contains Terraform configuration for deploying DomainPing's frontend infrastructure on AWS, including S3 bucket, CloudFront distribution, and optional custom domain setup.

## 🏗️ Infrastructure Overview

The Terraform configuration creates:

- **S3 Bucket**: Secure storage for React build files
- **CloudFront Distribution**: Global CDN for fast content delivery
- **Origin Access Control (OAC)**: Secure S3 access from CloudFront
- **IAM User & Policies**: GitHub Actions deployment permissions
- **Route53 & ACM Certificate**: Custom domain setup (optional)
- **Security**: Encryption, versioning, and access controls

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **Domain** (optional, for custom domain setup)

## 🚀 Quick Start

### 1. Configure Variables

```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

### 5. Get Outputs

```bash
terraform output
```

## 📝 Configuration Options

### Basic Configuration (CloudFront domain only)

```hcl
# terraform.tfvars
project_name = "domainping"
environment  = "prod"
aws_region   = "us-east-1"
domain_name  = ""  # Leave empty for CloudFront domain
```

### Custom Domain Configuration

```hcl
# terraform.tfvars
project_name = "domainping"
environment  = "prod"
aws_region   = "us-east-1"
domain_name  = "domainping.com"  # Your custom domain
```

## 🔧 Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `project_name` | Project name | `"domainping"` | No |
| `environment` | Environment (dev/staging/prod) | `"prod"` | No |
| `aws_region` | AWS region | `"us-east-1"` | No |
| `domain_name` | Custom domain name | `""` | No |
| `cloudfront_price_class` | CloudFront price class | `"PriceClass_100"` | No |
| `enable_logging` | Enable CloudFront logging | `false` | No |
| `tags` | Additional resource tags | `{}` | No |

## 📤 Outputs

After deployment, Terraform provides these outputs:

```bash
# Get all outputs
terraform output

# Get specific output
terraform output website_url
terraform output s3_bucket_name
terraform output cloudfront_distribution_id
```

### Key Outputs for GitHub Actions

```bash
# S3 bucket name
terraform output s3_bucket_name

# CloudFront distribution ID
terraform output cloudfront_distribution_id

# GitHub Actions credentials
terraform output github_actions_access_key_id
terraform output -raw github_actions_secret_access_key
```

## 🔐 GitHub Actions Integration

After deployment, configure GitHub secrets:

```bash
# Get the values
AWS_ACCESS_KEY_ID=$(terraform output -raw github_actions_access_key_id)
AWS_SECRET_ACCESS_KEY=$(terraform output -raw github_actions_secret_access_key)
AWS_S3_BUCKET=$(terraform output -raw s3_bucket_name)
CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
AWS_REGION=$(terraform output -raw aws_region)

# Add to GitHub repository secrets
gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
gh secret set AWS_S3_BUCKET --body "$AWS_S3_BUCKET"
gh secret set CLOUDFRONT_DISTRIBUTION_ID --body "$CLOUDFRONT_DISTRIBUTION_ID"
gh secret set AWS_REGION --body "$AWS_REGION"
```

## 🌐 Custom Domain Setup

If you configured a custom domain:

1. **Get name servers**:
   ```bash
   terraform output route53_name_servers
   ```

2. **Update domain registrar**: Point your domain to the Route53 name servers

3. **Wait for DNS propagation**: Usually takes 24-48 hours

4. **Verify**: Your site will be available at `https://yourdomain.com`

## 🏷️ Resource Naming

Resources are named using this pattern:
```
{project_name}-{resource_type}-{environment}-{random_suffix}
```

Example:
- S3 Bucket: `domainping-frontend-prod-a1b2c3d4`
- CloudFront: `domainping-frontend-distribution`
- IAM User: `domainping-github-actions`

## 💰 Cost Estimation

### AWS Free Tier (12 months)
- **S3**: 5GB storage, 20K requests - **FREE**
- **CloudFront**: 1TB transfer, 10M requests - **FREE**
- **Route53**: $0.50/month (if using custom domain)

### After Free Tier
- **S3**: ~$0.10-1/month
- **CloudFront**: ~$1-5/month
- **Route53**: $0.50/month
- **Total**: ~$1-7/month

## 🔄 Environment Management

### Multiple Environments

Deploy separate environments:

```bash
# Development
terraform workspace new dev
terraform apply -var="environment=dev"

# Staging
terraform workspace new staging
terraform apply -var="environment=staging"

# Production
terraform workspace new prod
terraform apply -var="environment=prod"
```

### Environment-Specific Variables

Create environment-specific tfvars files:

```bash
# dev.tfvars
environment = "dev"
domain_name = "dev.domainping.com"
cloudfront_price_class = "PriceClass_100"

# prod.tfvars
environment = "prod"
domain_name = "domainping.com"
cloudfront_price_class = "PriceClass_200"
```

Deploy with:
```bash
terraform apply -var-file="dev.tfvars"
```

## 🛡️ Security Features

- **S3 Bucket**: Private with OAC access only
- **Encryption**: Server-side encryption enabled
- **HTTPS**: Forced redirect to HTTPS
- **IAM**: Least privilege access for GitHub Actions
- **Versioning**: S3 object versioning enabled

## 🔧 Maintenance

### Update Infrastructure

```bash
# Check for changes
terraform plan

# Apply updates
terraform apply
```

### Destroy Infrastructure

```bash
# Destroy all resources
terraform destroy
```

⚠️ **Warning**: This will delete all resources and data!

### State Management

For production, use remote state:

```hcl
# versions.tf
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "domainping/frontend/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Domain validation timeout**:
   - Check DNS propagation
   - Verify Route53 name servers

2. **CloudFront deployment slow**:
   - CloudFront distributions take 5-15 minutes to deploy
   - Check AWS console for status

3. **S3 access denied**:
   - Verify bucket policy
   - Check OAC configuration

4. **GitHub Actions deployment fails**:
   - Verify IAM permissions
   - Check secret values

### Debug Commands

```bash
# Check Terraform state
terraform show

# Validate configuration
terraform validate

# Format code
terraform fmt

# Check for security issues
terraform plan -out=tfplan
terraform show -json tfplan | jq
```

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [DomainPing Deployment Guide](../../deploy/aws-s3-cloudfront-deploy.md)

## 🤝 Contributing

1. Make changes to Terraform files
2. Run `terraform fmt` to format code
3. Run `terraform validate` to validate syntax
4. Test in development environment
5. Submit pull request

## 📄 License

This infrastructure code is part of the DomainPing project. 