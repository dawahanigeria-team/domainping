# DomainPing Full-Stack Fly.io Deployment

## 🚀 Deploy Both Backend & Frontend to Fly.io

Perfect solution for team repositories! Deploy your entire DomainPing application (backend + frontend) to Fly.io without GitHub account restrictions.

### 🎁 Benefits of Full-Stack Fly.io
- ✅ **No GitHub team restrictions** (unlike Vercel)
- ✅ **Single platform** for both backend and frontend
- ✅ **Unified billing and monitoring**
- ✅ **Internal networking** between services
- ✅ **Custom domains** for both services
- ✅ **Cost-effective** (~$5-10/month total)

## Architecture Overview

```
┌─────────────────────────────────────┐
│              Fly.io                 │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Frontend    │  │ Backend     │   │
│  │ React App   │◄─┤ FastAPI     │   │
│  │ (Static)    │  │ API         │   │
│  └─────────────┘  └─────────────┘   │
│                   │ SQLite +    │   │
│                   │ Volume      │   │
│                   └─────────────┘   │
└─────────────────────────────────────┘
```

## Part 1: Deploy Backend (API)

Follow the standard backend deployment first:

### 1. Deploy Backend API

```bash
# Install Fly.io CLI (if not already done)
curl -L https://fly.io/install.sh | sh
flyctl auth login

# Deploy backend using existing guide
flyctl launch --dockerfile Dockerfile.fly --name domainping-api
flyctl deploy
```

📖 **Full Backend Guide**: [fly-deploy.md](fly-deploy.md)

## Part 2: Deploy Frontend (React App)

### 2. Create Frontend Dockerfile

Create `frontend/Dockerfile.fly`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 8080 (Fly.io standard)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Create Nginx Configuration

Create `frontend/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    server {
        listen 8080;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        
        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 4. Update Frontend Environment

Create `frontend/.env.production`:

```env
# Point to your Fly.io backend
REACT_APP_API_URL=https://domainping-api.fly.dev
```

Update `frontend/package.json` build script if needed:

```json
{
  "scripts": {
    "build": "REACT_APP_API_URL=https://domainping-api.fly.dev react-scripts build"
  }
}
```

### 5. Create Frontend Fly.io Config

Create `frontend/fly.toml`:

```toml
app = "domainping-frontend"
primary_region = "iad"  # Same region as backend

[build]
  dockerfile = "Dockerfile.fly"

[env]
  NODE_ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[vm]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### 6. Deploy Frontend

```bash
# Navigate to frontend directory
cd frontend

# Initialize and deploy
flyctl launch --dockerfile Dockerfile.fly --name domainping-frontend
flyctl deploy
```

## Part 3: Connect Backend & Frontend

### 7. Update Backend CORS

Update `backend/main.py` to allow your frontend domain:

```python
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://domainping-frontend.fly.dev",  # Fly.io frontend
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend:

```bash
cd ../  # Back to project root
flyctl deploy --app domainping-api
```

### 8. Test Full-Stack Application

Your apps will be available at:
- **Frontend**: `https://domainping-frontend.fly.dev`
- **Backend API**: `https://domainping-api.fly.dev`
- **API Docs**: `https://domainping-api.fly.dev/docs`

## Part 4: Custom Domains (Optional)

### 9. Set Up Custom Domains

```bash
# Add custom domain to frontend
flyctl certs create domainping.com --app domainping-frontend
flyctl certs create www.domainping.com --app domainping-frontend

# Add custom domain to backend API
flyctl certs create api.domainping.com --app domainping-api
```

### 10. Update DNS Records

```
# Frontend
A record: @ → [frontend-fly-ip]
CNAME record: www → domainping-frontend.fly.dev

# Backend API
CNAME record: api → domainping-api.fly.dev
```

### 11. Update Frontend Environment for Custom Domain

Update `frontend/.env.production`:

```env
REACT_APP_API_URL=https://api.domainping.com
```

Rebuild and redeploy frontend:

```bash
cd frontend
flyctl deploy
```

## Alternative: Single App Deployment

### Option: Combined Frontend + Backend

If you prefer a single app, create a combined Dockerfile:

Create `Dockerfile.fullstack`:

```dockerfile
# Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.9-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc curl nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build /app/static

# Copy nginx config for serving frontend
COPY nginx-fullstack.conf /etc/nginx/nginx.conf

# Create startup script
RUN echo '#!/bin/bash\nnginx &\nuvicorn main:app --host 0.0.0.0 --port 8001' > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]
```

## 💰 Cost Breakdown

### Two-App Setup (Recommended)
- **Backend**: $2-5/month (shared-cpu-1x, 256MB)
- **Frontend**: $2-3/month (shared-cpu-1x, 256MB)
- **Volume**: $0.15/month (1GB)
- **Total**: **$4-8/month**

### Single-App Setup
- **Combined App**: $3-5/month (shared-cpu-1x, 512MB)
- **Volume**: $0.15/month (1GB)
- **Total**: **$3-5/month**

## 🔧 Management Commands

### Useful Commands

```bash
# Check status of both apps
flyctl status --app domainping-api
flyctl status --app domainping-frontend

# View logs
flyctl logs --app domainping-api
flyctl logs --app domainping-frontend

# Scale apps
flyctl scale count 1 --app domainping-api
flyctl scale count 1 --app domainping-frontend

# SSH into apps
flyctl ssh console --app domainping-api
flyctl ssh console --app domainping-frontend

# Deploy updates
flyctl deploy --app domainping-api
flyctl deploy --app domainping-frontend
```

### Environment Variables

```bash
# Set frontend environment variables
flyctl secrets set REACT_APP_API_URL=https://domainping-api.fly.dev --app domainping-frontend

# Set backend environment variables (same as before)
flyctl secrets set DATABASE_URL=sqlite:///data/domains.db --app domainping-api
```

## 🚀 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --app domainping-api --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --app domainping-frontend --remote-only --dockerfile frontend/Dockerfile.fly
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## 🎉 You're Live!

Your full-stack DomainPing application is now running on Fly.io:

- ✅ **Frontend**: React app with global CDN
- ✅ **Backend**: FastAPI with SQLite database
- ✅ **No GitHub restrictions**: Works with team repositories
- ✅ **Cost-effective**: $4-8/month total
- ✅ **Scalable**: Auto-scaling and global deployment
- ✅ **Secure**: HTTPS, security headers, and health checks

### Next Steps:
1. **Set up monitoring** with Fly.io metrics
2. **Configure alerts** for downtime
3. **Set up automated backups**
4. **Add custom domains**
5. **Implement CI/CD pipeline**

Your domain renewal reminder system is now fully deployed on Fly.io! 🌍✨ 