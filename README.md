# DomainPing

Never lose a domain again! DomainPing provides comprehensive domain renewal reminders through multiple channels.

## Features

- 📅 **Smart Reminders**: Notifications at 90, 30, 14, 7, 3, and 1 days before expiration
- 📧 **Email Notifications**: Customizable email alerts
- 🖥️ **Desktop Notifications**: Native OS notifications
- 📱 **SMS Alerts**: Optional SMS notifications via Twilio
- 🌐 **Web Dashboard**: Beautiful interface to manage domains
- 🔍 **WHOIS Integration**: Automatic expiration date verification
- 📊 **Analytics**: Track renewal history and costs
- 🔄 **Auto-sync**: Periodic checks for domain status updates

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Easy Installation & Startup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd domainping
```

2. **Run the startup script:**
```bash
./start.sh
```

The script will:
- Check dependencies
- Create `.env` file from template (if needed)
- Install backend and frontend dependencies
- Start both services automatically

3. **Access the application:**
- 🌐 **Frontend Dashboard**: http://localhost:3000
- 📊 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

### Manual Installation (Alternative)

If you prefer manual setup:

1. **Setup backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup frontend:**
```bash
cd frontend
npm install
```

3. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your settings
```

4. **Run services:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

## Configuration

Edit `.env` file:

```env
# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Twilio (Optional)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

# Database
DATABASE_URL=sqlite:///domains.db

# Notification Settings
DEFAULT_REMINDER_DAYS=90,30,14,7,3,1
```

## Usage

1. **Add Domains**: Use the web interface to add your domains
2. **Set Preferences**: Configure notification preferences
3. **Monitor**: DomainPing runs automatically in the background
4. **Renew**: Get timely reminders and never miss a renewal

## 🚀 Deployment

### Cloud Hosting Options

1. **AWS S3 + CloudFront** (Recommended - Enterprise-grade)
2. **Fly.io** (Cost-effective - Backend)
3. **Railway** (Easiest - Full Stack)
4. **Vercel** (Frontend only)

### Infrastructure as Code (IaC)

Deploy AWS infrastructure automatically with Terraform:

```bash
# One-command deployment
./iac/deploy.sh deploy
```

This creates:
- S3 bucket for frontend hosting
- CloudFront distribution for global CDN
- IAM user for GitHub Actions
- Optional custom domain setup

### Manual Deployment

📖 **Detailed deployment guides**: [deploy/](deploy/)
🏗️ **Infrastructure setup**: [iac/](iac/)

## Architecture

```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   ├── api/       # API endpoints
│   │   └── tasks/     # Background tasks
│   └── main.py
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── iac/              # Infrastructure as Code
│   ├── terraform/    # Terraform configurations
│   └── deploy.sh     # Automated deployment
├── deploy/           # Deployment guides
└── docs/             # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details. 