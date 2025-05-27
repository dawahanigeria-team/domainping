# DomainPing Infrastructure as Code (IaC)

This directory contains Infrastructure as Code (IaC) configurations for deploying DomainPing's AWS infrastructure using Terraform.

## 🏗️ What This Creates

The Terraform configuration automatically provisions:

- **S3 Bucket**: Secure storage for React frontend files
- **CloudFront Distribution**: Global CDN for fast content delivery
- **Origin Access Control (OAC)**: Secure access from CloudFront to S3
- **IAM User & Policies**: GitHub Actions deployment permissions
- **Route53 Hosted Zone**: DNS management (optional)
- **ACM SSL Certificate**: HTTPS encryption (optional)
- **Security Features**: Encryption, versioning, access controls

## 📁 Directory Structure

```
iac/
├── terraform/
│   ├── main.tf                 # Main infrastructure configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   ├── versions.tf             # Provider version constraints
│   ├── terraform.tfvars.example # Example configuration
│   ├── .gitignore              # Terraform gitignore
│   └── README.md               # Detailed Terraform docs
├── deploy.sh                   # Automated deployment script
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Make script executable (if not already)
chmod +x iac/deploy.sh

# Run full deployment
./iac/deploy.sh deploy
```

### Option 2: Manual Deployment

```bash
cd iac/terraform

# 1. Configure variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# 2. Initialize Terraform
terraform init

# 3. Plan deployment
terraform plan

# 4. Deploy infrastructure
terraform apply
```

## 📋 Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **Domain name** (optional, for custom domain)

### Install Prerequisites

```bash
# Install Terraform (macOS)
brew install terraform

# Install AWS CLI (macOS)
brew install awscli

# Configure AWS credentials
aws configure

# Install GitHub CLI (optional, for automatic secret setup)
brew install gh
```

## ⚙️ Configuration

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

## 🎯 Deployment Options

### Full Deployment
```bash
./iac/deploy.sh deploy
```
- Checks prerequisites
- Sets up Terraform
- Plans deployment
- Applies infrastructure
- Shows outputs
- Configures GitHub secrets

### Plan Only
```bash
./iac/deploy.sh plan
```
- Shows what will be created/changed
- Doesn't make any changes

### Show Outputs
```bash
./iac/deploy.sh output
```
- Displays deployment information
- Shows GitHub Actions configuration

### Destroy Infrastructure
```bash
./iac/deploy.sh destroy
```
- ⚠️ **Warning**: Destroys all resources!

## 📤 Key Outputs

After deployment, you'll get:

| Output | Description | Use Case |
|--------|-------------|----------|
| `website_url` | Your website URL | Access your deployed site |
| `s3_bucket_name` | S3 bucket name | GitHub Actions deployment |
| `cloudfront_distribution_id` | CloudFront ID | Cache invalidation |
| `github_actions_access_key_id` | IAM access key | GitHub secrets |
| `github_actions_secret_access_key` | IAM secret key | GitHub secrets |

## 🔐 GitHub Actions Integration

The deployment automatically creates IAM credentials for GitHub Actions. Add these secrets to your repository:

```bash
# Automatically set secrets (requires GitHub CLI)
./iac/deploy.sh deploy  # Will prompt to set secrets

# Or manually get values
cd iac/terraform
terraform output github_actions_access_key_id
terraform output -raw github_actions_secret_access_key
```

### Required GitHub Secrets

| Secret Name | Value Source |
|-------------|--------------|
| `AWS_ACCESS_KEY_ID` | `terraform output github_actions_access_key_id` |
| `AWS_SECRET_ACCESS_KEY` | `terraform output -raw github_actions_secret_access_key` |
| `AWS_S3_BUCKET` | `terraform output s3_bucket_name` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `terraform output cloudfront_distribution_id` |
| `AWS_REGION` | `terraform output aws_region` |

## 🌐 Custom Domain Setup

If you configured a custom domain:

1. **Deploy infrastructure** with `domain_name` set
2. **Get name servers**:
   ```bash
   terraform output route53_name_servers
   ```
3. **Update domain registrar**: Point your domain to Route53 name servers
4. **Wait for DNS propagation**: Usually 24-48 hours
5. **Verify**: Your site will be available at `https://yourdomain.com`

## 💰 Cost Estimation

### AWS Free Tier (12 months)
- **S3**: 5GB storage, 20K requests - **FREE**
- **CloudFront**: 1TB transfer, 10M requests - **FREE**
- **Route53**: $0.50/month (if using custom domain)

### After Free Tier
- **S3**: ~$0.10-1/month
- **CloudFront**: ~$1-5/month
- **Route53**: $0.50/month
- **Total**: **$1-7/month**

## 🔄 Environment Management

### Multiple Environments

```bash
# Development environment
terraform workspace new dev
terraform apply -var="environment=dev" -var="domain_name=dev.domainping.com"

# Staging environment
terraform workspace new staging
terraform apply -var="environment=staging" -var="domain_name=staging.domainping.com"

# Production environment
terraform workspace new prod
terraform apply -var="environment=prod" -var="domain_name=domainping.com"
```

### Environment-Specific Variables

Create separate tfvars files:

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

- **Private S3 Bucket**: Only CloudFront can access
- **Origin Access Control**: Modern secure access method
- **HTTPS Enforced**: All traffic redirected to HTTPS
- **Encryption**: Server-side encryption enabled
- **IAM Least Privilege**: Minimal permissions for GitHub Actions
- **Versioning**: S3 object versioning for rollbacks

## 🔧 Maintenance

### Update Infrastructure
```bash
# Check for changes
terraform plan

# Apply updates
terraform apply
```

### Backup State
```bash
# Backup current state
cp terraform.tfstate terraform.tfstate.backup
```

### Remote State (Production)

For production, use remote state storage:

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

1. **AWS credentials not configured**:
   ```bash
   aws configure
   ```

2. **Terraform not found**:
   ```bash
   brew install terraform
   ```

3. **Domain validation timeout**:
   - Check DNS propagation
   - Verify Route53 name servers

4. **CloudFront deployment slow**:
   - CloudFront takes 5-15 minutes to deploy
   - This is normal AWS behavior

### Debug Commands

```bash
# Validate configuration
terraform validate

# Format code
terraform fmt

# Show current state
terraform show

# Check for drift
terraform plan -detailed-exitcode
```

## 📚 Additional Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [DomainPing AWS Deployment Guide](../deploy/aws-s3-cloudfront-deploy.md)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

## 🤝 Contributing

1. Make changes to Terraform files
2. Run `terraform fmt` to format code
3. Run `terraform validate` to validate syntax
4. Test in development environment
5. Submit pull request

## 📄 License

This infrastructure code is part of the DomainPing project.

---

## 🎉 What's Next?

After deploying your infrastructure:

1. ✅ **Infrastructure is ready** - S3 bucket and CloudFront created
2. 🔐 **GitHub secrets configured** - Automated deployments enabled
3. 🌐 **Domain setup** (if configured) - Professional URL ready
4. 🚀 **Deploy your frontend** - Push to trigger GitHub Actions
5. 📊 **Monitor costs** - Track AWS usage and costs

Your DomainPing frontend now has enterprise-grade hosting infrastructure! 🌍✨ 