# DomainPing AWS S3 + CloudFront Deployment

## 🚀 Deploy React Frontend to AWS S3 + CloudFront

Perfect solution for cost-effective, globally distributed React hosting with automated deployments!

### 🎁 AWS Free Tier Benefits
- ✅ **S3**: 5GB storage, 20,000 GET requests/month (12 months)
- ✅ **CloudFront**: 1TB data transfer, 10M requests/month (12 months)
- ✅ **Route 53**: $0.50/month for hosted zone (after free tier)
- ✅ **Total Cost**: ~$0-5/month (mostly free for small apps)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                           │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Route 53  │    │ CloudFront  │    │     S3      │ │
│  │   (DNS)     │───▶│    (CDN)    │───▶│  (Storage)  │ │
│  │             │    │             │    │             │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────────────┐
                    │ GitHub Actions  │
                    │   (CI/CD)       │
                    └─────────────────┘
```

## Part 1: AWS Setup

### Step 1: Create S3 Bucket

1. **Login to AWS Console** and navigate to S3
2. **Click "Create Bucket"**
3. **Configure bucket:**
   - **Bucket name**: `domainping-frontend` (must be globally unique)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
   - **Block Public Access**: Keep enabled (CloudFront will access privately)
   - **Versioning**: Enable (optional, for rollbacks)

4. **Create the bucket**

### Step 2: Configure S3 for Static Website Hosting

1. **Go to your bucket** → **Properties** tab
2. **Scroll to "Static website hosting"**
3. **Click "Edit"** and configure:
   - **Enable**: Static website hosting
   - **Index document**: `index.html`
   - **Error document**: `index.html` (for React Router)

4. **Save changes**

### Step 3: Create CloudFront Distribution

1. **Navigate to CloudFront** in AWS Console
2. **Click "Create Distribution"**
3. **Configure Origin:**
   - **Origin Domain**: Select your S3 bucket
   - **Origin Access**: Origin Access Control (OAC)
   - **Create new OAC**: Yes (this secures S3 access)

4. **Configure Default Cache Behavior:**
   - **Viewer Protocol Policy**: Redirect HTTP to HTTPS
   - **Allowed HTTP Methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - **Cache Policy**: Managed-CachingOptimized

5. **Configure Settings:**
   - **Price Class**: Use all edge locations (or choose based on budget)
   - **Default Root Object**: `index.html`
   - **Custom Error Pages**: Add 404 → `/index.html` (for React Router)

6. **Create Distribution** (takes 5-15 minutes to deploy)

### Step 4: Update S3 Bucket Policy

CloudFront will provide a bucket policy. Copy and apply it:

1. **Go to S3 bucket** → **Permissions** → **Bucket Policy**
2. **Paste the policy** CloudFront generated
3. **Save changes**

## Part 2: GitHub Actions Setup

### Step 5: Create IAM User for GitHub Actions

1. **Go to IAM** → **Users** → **Create User**
2. **Username**: `github-actions-domainping`
3. **Attach policies directly:**
   - `AmazonS3FullAccess`
   - `CloudFrontFullAccess`

4. **Create user**
5. **Go to Security Credentials** → **Create Access Key**
6. **Choose "Application running outside AWS"**
7. **Download CSV** with credentials

### Step 6: Add GitHub Secrets

In your GitHub repository:

1. **Go to Settings** → **Secrets and Variables** → **Actions**
2. **Add these secrets:**

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key |
| `AWS_S3_BUCKET` | `domainping-frontend` |
| `AWS_REGION` | `us-east-1` (or your region) |
| `CLOUDFRONT_DISTRIBUTION_ID` | From CloudFront console |

### Step 7: Create GitHub Actions Workflow

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to AWS S3 + CloudFront

on:
  push:
    branches: [main, master]
    paths: ['frontend/**']
  pull_request:
    branches: [main, master]
    paths: ['frontend/**']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Build React app
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://domainping-api.fly.dev
          GENERATE_SOURCEMAP: false
        run: npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Deploy to S3
        working-directory: frontend
        run: |
          aws s3 sync build/ s3://${{ secrets.AWS_S3_BUCKET }} --delete --exact-timestamps

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

      - name: Output deployment URL
        run: |
          echo "🚀 Frontend deployed successfully!"
          echo "📱 CloudFront URL: https://${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}.cloudfront.net"
```

## Part 3: Frontend Configuration

### Step 8: Update Frontend for Production

Create `frontend/.env.production`:

```env
# Production API URL (your backend)
REACT_APP_API_URL=https://domainping-api.fly.dev

# Disable source maps for security
GENERATE_SOURCEMAP=false

# Enable production optimizations
NODE_ENV=production
```

### Step 9: Update package.json Scripts

Add deployment-friendly scripts to `frontend/package.json`:

```json
{
  "scripts": {
    "build": "react-scripts build",
    "build:prod": "REACT_APP_API_URL=https://domainping-api.fly.dev npm run build",
    "deploy": "npm run build:prod && aws s3 sync build/ s3://domainping-frontend --delete"
  }
}
```

### Step 10: Handle React Router

Create `frontend/public/_redirects` (for SPA routing):

```
/*    /index.html   200
```

Or ensure your CloudFront distribution has custom error pages:
- **404** → `/index.html` (200 status)

## Part 4: Custom Domain (Optional)

### Step 11: Set Up Custom Domain

1. **Buy domain** in Route 53 or use existing domain
2. **Create hosted zone** in Route 53
3. **Request SSL certificate** in AWS Certificate Manager:
   - **Domain**: `domainping.com`
   - **Add**: `www.domainping.com`
   - **Validation**: DNS validation

4. **Update CloudFront distribution:**
   - **Alternate Domain Names**: `domainping.com`, `www.domainping.com`
   - **SSL Certificate**: Select your ACM certificate

5. **Create Route 53 records:**
   ```
   A record: domainping.com → CloudFront distribution
   CNAME record: www.domainping.com → domainping.com
   ```

## Part 5: Advanced Optimizations

### Step 12: Performance Optimizations

Update your GitHub Actions workflow for better performance:

```yaml
      - name: Build React app with optimizations
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://domainping-api.fly.dev
          GENERATE_SOURCEMAP: false
          INLINE_RUNTIME_CHUNK: false
        run: |
          npm run build
          # Compress files
          find build -name "*.js" -exec gzip -k {} \;
          find build -name "*.css" -exec gzip -k {} \;

      - name: Deploy to S3 with optimized settings
        working-directory: frontend
        run: |
          # Upload with proper content types and caching
          aws s3 sync build/ s3://${{ secrets.AWS_S3_BUCKET }} \
            --delete \
            --exact-timestamps \
            --cache-control "public,max-age=31536000,immutable" \
            --exclude "*.html" \
            --exclude "service-worker.js"
          
          # Upload HTML files with no cache
          aws s3 sync build/ s3://${{ secrets.AWS_S3_BUCKET }} \
            --delete \
            --exact-timestamps \
            --cache-control "public,max-age=0,must-revalidate" \
            --include "*.html" \
            --include "service-worker.js"
```

### Step 13: Environment-Specific Deployments

Create separate workflows for staging and production:

**`.github/workflows/deploy-staging.yml`:**
```yaml
name: Deploy to Staging
on:
  push:
    branches: [develop]
    paths: ['frontend/**']

# ... same as above but with staging bucket and CloudFront
```

## 💰 Cost Breakdown

### AWS Free Tier (First 12 months)
- **S3**: 5GB storage, 20K GET requests - **FREE**
- **CloudFront**: 1TB transfer, 10M requests - **FREE**
- **Route 53**: $0.50/month for hosted zone
- **Certificate Manager**: **FREE**

### After Free Tier
- **S3**: ~$0.10-1/month (depending on traffic)
- **CloudFront**: ~$1-5/month (depending on traffic)
- **Route 53**: $0.50/month
- **Total**: **$1-7/month**

## 🔧 Management Commands

### Useful AWS CLI Commands

```bash
# Manual deployment
npm run build
aws s3 sync build/ s3://domainping-frontend --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/*"

# Check S3 bucket contents
aws s3 ls s3://domainping-frontend --recursive

# Monitor CloudFront metrics
aws cloudfront get-distribution --id E1234567890123
```

### GitHub Actions Debugging

```bash
# Check workflow status
gh run list --workflow=deploy-frontend.yml

# View logs
gh run view --log

# Re-run failed workflow
gh run rerun <run-id>
```

## 🚀 Deployment Process

### Automatic Deployment
1. **Push to main/master** branch
2. **GitHub Actions triggers** automatically
3. **Builds React app** with production settings
4. **Uploads to S3** with optimized caching
5. **Invalidates CloudFront** cache
6. **Your app is live** globally!

### Manual Deployment
```bash
cd frontend
npm run build:prod
aws s3 sync build/ s3://domainping-frontend --delete
aws cloudfront create-invalidation --distribution-id E1234567890123 --paths "/*"
```

## 🎉 You're Live!

Your DomainPing frontend is now deployed on AWS with:

- ✅ **Global CDN**: Fast loading worldwide
- ✅ **Auto-scaling**: Handles any traffic load
- ✅ **HTTPS**: Secure by default
- ✅ **Cost-effective**: Mostly free with AWS free tier
- ✅ **Automated deployments**: Push to deploy
- ✅ **Custom domain**: Professional appearance

### Your URLs:
- **CloudFront**: `https://d1234567890123.cloudfront.net`
- **Custom Domain**: `https://domainping.com` (if configured)
- **Backend API**: `https://domainping-api.fly.dev`

### Next Steps:
1. **Set up monitoring** with AWS CloudWatch
2. **Configure alerts** for errors or high costs
3. **Add staging environment** for testing
4. **Implement blue-green deployments**
5. **Set up AWS WAF** for security (if needed)

Your domain renewal reminder system now has enterprise-grade hosting! 🌍✨ 