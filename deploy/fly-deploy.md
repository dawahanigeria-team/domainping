# DomainPing Fly.io Deployment Guide

## 🚀 Deploy DomainPing to Fly.io

Fly.io is an excellent choice for hosting DomainPing! It offers a generous free tier, excellent FastAPI support, and global edge deployment.

### 🎁 Free Tier Benefits
- **$5/month in free credits** (enough for small apps)
- **Shared CPU instances** starting at ~$2/month
- **Auto-sleep** when inactive (saves money)
- **Global edge deployment** for low latency
- **Built-in SSL certificates**

### Prerequisites
- Fly.io account (free at [fly.io](https://fly.io))
- `flyctl` CLI installed
- DomainPing code ready for deployment

## Step 1: Install Fly.io CLI

### macOS/Linux:
```bash
curl -L https://fly.io/install.sh | sh
```

### Windows:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Verify Installation:
```bash
flyctl version
```

## Step 2: Login to Fly.io

```bash
flyctl auth login
```

This will open your browser to authenticate. Create an account if you don't have one.

## Step 3: Prepare DomainPing for Fly.io

### Create Fly.io Dockerfile

Create `Dockerfile.fly` in your project root:

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Update Backend for Health Check

Add this to your `backend/main.py`:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io"""
    return {
        "status": "healthy",
        "service": "DomainPing API",
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Step 4: Initialize Fly.io App

In your project root directory:

```bash
flyctl launch --dockerfile Dockerfile.fly
```

This will:
- Detect your app type
- Create a `fly.toml` configuration file
- Ask you to choose a region
- Set up basic configuration

### Choose Your Configuration:
- **App name**: `domainping-api` (or your preferred name)
- **Region**: Choose closest to your users
- **Database**: Skip for now (we'll add SQLite volume)
- **Deploy**: Say "No" for now

## Step 5: Configure fly.toml

Edit the generated `fly.toml` file:

```toml
app = "domainping-api"
primary_region = "iad"  # or your chosen region

[build]
  dockerfile = "Dockerfile.fly"

[env]
  PORT = "8000"
  API_HOST = "0.0.0.0"
  API_PORT = "8000"

[http_service]
  internal_port = 8000
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

[[mounts]]
  source = "domainping_data"
  destination = "/app/data"

[deploy]
  release_command = "python -c 'from app.models import create_tables; create_tables()'"
```

## Step 6: Create Persistent Volume for SQLite

```bash
flyctl volumes create domainping_data --size 1 --region iad
```

- `--size 1`: 1GB volume (minimum)
- `--region iad`: Same region as your app

## Step 7: Set Environment Variables

```bash
# Required environment variables
flyctl secrets set \
  SECRET_KEY="your-super-secret-key-change-this" \
  SMTP_SERVER="smtp.gmail.com" \
  SMTP_PORT="587" \
  SMTP_USERNAME="your-email@gmail.com" \
  SMTP_PASSWORD="your-app-password" \
  SMTP_USE_TLS="true" \
  FROM_EMAIL="your-email@gmail.com" \
  FROM_NAME="DomainPing" \
  DATABASE_URL="sqlite:///data/domains.db"

# Optional: Twilio for SMS
flyctl secrets set \
  TWILIO_ACCOUNT_SID="your-twilio-sid" \
  TWILIO_AUTH_TOKEN="your-twilio-token" \
  TWILIO_PHONE_NUMBER="+1234567890"

# Optional: Notification settings
flyctl secrets set \
  DEFAULT_REMINDER_DAYS="90,30,14,7,3,1" \
  ENABLE_EMAIL_NOTIFICATIONS="true" \
  ENABLE_SMS_NOTIFICATIONS="false" \
  ENABLE_DESKTOP_NOTIFICATIONS="false"
```

## Step 8: Deploy to Fly.io

```bash
flyctl deploy
```

This will:
- Build your Docker image
- Push to Fly.io registry
- Deploy to your chosen region
- Run health checks
- Provide your app URL

## Step 9: Verify Deployment

### Check App Status:
```bash
flyctl status
```

### View Logs:
```bash
flyctl logs
```

### Test API:
```bash
curl https://your-app-name.fly.dev/health
```

### Open in Browser:
```bash
flyctl open
```

## Step 10: Scale and Monitor

### Scale to Zero (Save Money):
```bash
flyctl scale count 0
```
App will auto-start when traffic arrives.

### Scale Up for Production:
```bash
flyctl scale count 1
```

### Monitor Resource Usage:
```bash
flyctl status --all
flyctl metrics
```

## 🔧 Advanced Configuration

### Custom Domain

1. **Add domain to Fly.io:**
```bash
flyctl certs create domainping.com
flyctl certs create www.domainping.com
```

2. **Update DNS records:**
```
A record: @ → [your-fly-ip]
CNAME record: www → your-app-name.fly.dev
```

### Database Backups

```bash
# SSH into your app
flyctl ssh console

# Backup database
cp /app/data/domains.db /tmp/backup-$(date +%Y%m%d).db

# Download backup
flyctl ssh sftp get /tmp/backup-20241201.db ./local-backup.db
```

### Scheduled Tasks

Create `scripts/scheduler.py`:
```python
import asyncio
import schedule
import time
from app.tasks.domain_checker import check_all_domains

def run_scheduler():
    schedule.every().day.at("09:00").do(lambda: asyncio.run(check_all_domains()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
```

Add to `fly.toml`:
```toml
[processes]
  app = "uvicorn main:app --host 0.0.0.0 --port 8000"
  scheduler = "python scripts/scheduler.py"
```

## 💰 Cost Optimization

### Free Tier Strategy:
- Use **shared-cpu-1x** with **256MB RAM** (~$2/month)
- Enable **auto-stop** when inactive
- Use **SQLite** instead of managed database
- Monitor usage with `flyctl status`

### Production Strategy:
- Upgrade to **shared-cpu-1x** with **512MB RAM** (~$3/month)
- Add **Redis** for caching (~$1/month)
- Enable **multiple regions** for global performance

## 🆘 Troubleshooting

### Common Issues:

1. **Build Fails:**
```bash
flyctl logs --app your-app-name
# Check Dockerfile and dependencies
```

2. **Database Connection Issues:**
```bash
flyctl ssh console
ls -la /app/data/
# Check volume mount and permissions
```

3. **Health Check Fails:**
```bash
flyctl status
# Verify /health endpoint works
```

4. **App Won't Start:**
```bash
flyctl logs --app your-app-name
# Check environment variables and secrets
```

### Debug Commands:
```bash
# SSH into running app
flyctl ssh console

# Check environment variables
flyctl ssh console -C "env | grep -E '(SMTP|DATABASE)'"

# Restart app
flyctl restart

# Force redeploy
flyctl deploy --force
```

## 🎉 You're Live!

Once deployed, your DomainPing API will be available at:
- **API**: `https://your-app-name.fly.dev`
- **Docs**: `https://your-app-name.fly.dev/docs`
- **Health**: `https://your-app-name.fly.dev/health`

### Next Steps:
1. **Deploy Frontend** to Vercel/Netlify
2. **Set up monitoring** with Fly.io metrics
3. **Configure custom domain**
4. **Set up CI/CD** with GitHub Actions
5. **Add Redis** for caching (optional)

Your domain renewal reminder system is now running globally on Fly.io! 🌍✨ 