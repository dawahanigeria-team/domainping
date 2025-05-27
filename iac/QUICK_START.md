# DomainPing IaC Quick Start

## 🚀 Deploy AWS Infrastructure in 5 Minutes

### Prerequisites
```bash
# Install tools (macOS)
brew install terraform awscli gh

# Configure AWS
aws configure
```

### Deploy Infrastructure
```bash
# 1. Run automated deployment
./iac/deploy.sh deploy

# 2. Follow prompts to:
#    - Configure terraform.tfvars
#    - Review deployment plan
#    - Apply infrastructure
#    - Set GitHub secrets
```

### What Gets Created
- ✅ S3 bucket for React frontend
- ✅ CloudFront distribution (global CDN)
- ✅ IAM user for GitHub Actions
- ✅ SSL certificate (if custom domain)
- ✅ Route53 hosted zone (if custom domain)

### Configuration Options

#### Basic (CloudFront domain)
```hcl
# terraform.tfvars
project_name = "domainping"
environment  = "prod"
domain_name  = ""  # Uses CloudFront domain
```

#### Custom Domain
```hcl
# terraform.tfvars
project_name = "domainping"
environment  = "prod"
domain_name  = "domainping.com"  # Your domain
```

### After Deployment

1. **Get your website URL**:
   ```bash
   terraform output website_url
   ```

2. **GitHub secrets are automatically configured** (if you have `gh` CLI)

3. **For custom domain**: Update your domain's name servers to Route53

### Cost
- **Free Tier**: Mostly free for 12 months
- **After Free Tier**: $1-7/month

### Commands
```bash
./iac/deploy.sh deploy    # Full deployment
./iac/deploy.sh plan      # Plan only
./iac/deploy.sh output    # Show outputs
./iac/deploy.sh destroy   # Destroy infrastructure
```

### Troubleshooting
- **AWS credentials**: Run `aws configure`
- **Terraform not found**: Run `brew install terraform`
- **Slow deployment**: CloudFront takes 5-15 minutes

### Next Steps
1. ✅ Infrastructure deployed
2. 🔐 GitHub secrets configured
3. 🚀 Push code to trigger deployment
4. 🌐 Access your live site!

📖 **Full documentation**: [README.md](README.md) 