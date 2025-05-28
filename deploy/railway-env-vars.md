# Railway Environment Variables Setup

## Required Environment Variables

Add these in your Railway project settings:

### Database Configuration
```
DATABASE_URL=sqlitecloud://your-sqlitecloud-url-here
```

### API Configuration
```
FRONTEND_URL=https://dlzn4ikotqjx.cloudfront.net
```

### Email Configuration (if using SMTP)
```
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=DomainPing
```

### Twilio Configuration (if using SMS)
```
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

### Railway Specific
```
PORT=8000
PYTHONPATH=/app
```

## How to Add in Railway:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add each environment variable above
5. Deploy your service

## Important Notes:

- Railway automatically provides the `PORT` environment variable
- Make sure your `DATABASE_URL` points to your SQLite Cloud instance
- The `FRONTEND_URL` should match your CloudFront distribution URL
- Keep sensitive variables like passwords and tokens secure 