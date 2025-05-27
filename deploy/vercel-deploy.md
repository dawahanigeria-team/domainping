# DomainPing Vercel Deployment Guide

## 🚀 Deploy Frontend to Vercel

Vercel is excellent for hosting the React frontend with global CDN and automatic deployments.

### Prerequisites
- GitHub account with your DomainPing repository
- Vercel account (free at [vercel.com](https://vercel.com))
- Backend deployed elsewhere (Railway, DigitalOcean, etc.)

### Step 1: Prepare Frontend for Deployment

1. **Create production build configuration:**

Create `frontend/vercel.json`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

2. **Update package.json scripts:**
```json
{
  "scripts": {
    "build": "react-scripts build",
    "start": "react-scripts start"
  }
}
```

### Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Click "New Project"**
3. **Import your DomainPing repository**
4. **Configure project settings:**
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### Step 3: Configure Environment Variables

In Vercel project settings, add:

```env
# Backend API URL (replace with your actual backend URL)
REACT_APP_API_URL=https://your-backend.railway.app

# Optional: Analytics
REACT_APP_ANALYTICS_ID=your-analytics-id
```

### Step 4: Set Up Custom Domain

1. **In Vercel dashboard, go to your project**
2. **Click "Domains" tab**
3. **Add your custom domain** (e.g., `domainping.com`)
4. **Configure DNS records:**
   - Add CNAME record: `www` → `cname.vercel-dns.com`
   - Add A record: `@` → `76.76.19.61`

### Step 5: Enable Automatic Deployments

Vercel automatically deploys when you push to GitHub:
- **Production**: Deploys from `main` branch
- **Preview**: Deploys from feature branches
- **Instant rollbacks**: One-click rollback to previous versions

## 🔧 Advanced Vercel Features

### Edge Functions (API Routes)

Create `frontend/api/health.js` for serverless functions:
```javascript
export default function handler(req, res) {
  res.status(200).json({ 
    status: 'healthy', 
    service: 'DomainPing Frontend',
    timestamp: new Date().toISOString()
  });
}
```

### Performance Optimization

1. **Enable Image Optimization:**
```javascript
// In your React components
import Image from 'next/image'; // If using Next.js

// Or use Vercel's image optimization
<img src="/api/image?url=domain-icon.png&w=64&h=64" alt="Domain" />
```

2. **Bundle Analysis:**
```bash
npm install --save-dev @next/bundle-analyzer
```

### Analytics and Monitoring

Add to your React app:
```javascript
// In src/index.js or App.js
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <>
      <YourApp />
      <Analytics />
    </>
  );
}
```

## 💰 Vercel Pricing

**Free Tier (Hobby):**
- 100GB bandwidth/month
- Unlimited personal projects
- Automatic HTTPS
- Global CDN

**Pro Tier ($20/month):**
- 1TB bandwidth/month
- Team collaboration
- Advanced analytics
- Password protection

## 🚨 Production Checklist

- [ ] Custom domain configured
- [ ] SSL certificate enabled (automatic)
- [ ] Environment variables set
- [ ] Backend API URL configured
- [ ] Analytics enabled
- [ ] Error tracking configured
- [ ] Performance monitoring enabled
- [ ] SEO optimization completed

## 🔄 CI/CD Pipeline

Vercel provides automatic CI/CD:

1. **Push to GitHub** → Automatic build
2. **Pull Request** → Preview deployment
3. **Merge to main** → Production deployment
4. **Rollback** → One-click previous version

### Custom Build Process

Create `frontend/.vercelignore`:
```
node_modules
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

## 🌍 Global Performance

Vercel's Edge Network provides:
- **Global CDN**: 40+ regions worldwide
- **Edge Caching**: Static assets cached globally
- **Smart Routing**: Automatic traffic optimization
- **DDoS Protection**: Built-in security

## 🆘 Troubleshooting

**Common Issues:**

1. **Build fails**: Check package.json and dependencies
2. **API calls fail**: Verify REACT_APP_API_URL
3. **Routing issues**: Check vercel.json rewrites
4. **Environment variables**: Ensure proper naming (REACT_APP_*)

**Performance Issues:**
- Use Vercel Analytics to identify bottlenecks
- Optimize images and assets
- Enable compression and caching

## 🎉 You're Live!

Your DomainPing frontend is now deployed on Vercel with:
- **Global CDN**: Fast loading worldwide
- **Automatic HTTPS**: Secure by default
- **Continuous Deployment**: Updates on every push
- **Preview Deployments**: Test before going live

Access your app at: `https://your-domain.vercel.app` or your custom domain! 