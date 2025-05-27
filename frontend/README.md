# DomainPing Frontend

React frontend for the DomainPing domain renewal reminder service.

## Environment Configuration

### Environment Variables

The app uses the following environment variables:

- `REACT_APP_API_URL`: Backend API URL (required)
- `GENERATE_SOURCEMAP`: Whether to generate source maps (optional, default: true in dev, false in prod)

### Local Development

1. Copy the development environment template:
   ```bash
   cp env.development.example .env.development
   ```

2. Update `.env.development` with your local backend URL:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Production Deployment

#### GitHub Actions (Automated)

The GitHub Action automatically builds and deploys the frontend. Configure these secrets in your GitHub repository:

**Required Secrets:**
- `REACT_APP_API_URL`: Your production API URL (e.g., `https://domainping-api.fly.dev`)
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 deployment
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 deployment
- `AWS_REGION`: AWS region (e.g., `us-east-1`)
- `AWS_S3_BUCKET`: S3 bucket name for hosting
- `CLOUDFRONT_DISTRIBUTION_ID`: CloudFront distribution ID

**To add secrets:**
1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with its corresponding value

#### Manual Deployment

1. Set environment variables:
   ```bash
   export REACT_APP_API_URL=https://your-api-url.com
   export GENERATE_SOURCEMAP=false
   ```

2. Build the app:
   ```bash
   npm run build
   ```

3. Deploy the `build/` folder to your static hosting service

### Environment Files Priority

React loads environment variables in this order (higher priority overrides lower):

1. `.env.development.local` (local development only)
2. `.env.local` (always loaded except test)
3. `.env.development` (development environment)
4. `.env` (default)

### Important Notes

- **Build-time variables**: React environment variables are embedded during build time, not runtime
- **Prefix requirement**: All custom environment variables must start with `REACT_APP_`
- **No secrets in frontend**: Never put sensitive data in React environment variables (they're visible to users)
- **Different URLs per environment**: Use different API URLs for development, staging, and production

## Available Scripts

- `npm start`: Start development server
- `npm run build`: Build for production
- `npm test`: Run tests
- `npm run eject`: Eject from Create React App (not recommended)

## Deployment Targets

- **AWS S3 + CloudFront**: Automated via GitHub Actions
- **Fly.io**: Manual deployment using Dockerfile.fly
- **Netlify/Vercel**: Manual deployment of build folder 