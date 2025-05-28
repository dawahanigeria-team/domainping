#!/bin/bash

# Railway Deployment Script for DomainPing
# This script helps deploy to Railway with proper configuration

echo "🚂 Railway Deployment Script for DomainPing"
echo "============================================"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Link to project (if not already linked)
echo "🔗 Linking to Railway project..."
railway link

# Set environment variables
echo "🌍 Setting up environment variables..."
echo "Please make sure you have set the following environment variables in Railway dashboard:"
echo "- DATABASE_URL (your SQLite Cloud URL)"
echo "- FRONTEND_URL (your CloudFront URL)"
echo "- SMTP_* variables (if using email)"
echo "- TWILIO_* variables (if using SMS)"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment initiated!"
echo "📊 Check your Railway dashboard for deployment status"
echo "🌐 Your API will be available at: https://your-railway-domain.railway.app" 