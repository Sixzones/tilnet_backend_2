# Tilnet Backend - Railway Deployment Guide

## Overview
This guide will help you deploy your Django backend to Railway with proper configuration for production.

## Pre-deployment Checklist

### ✅ Completed Setup
- [x] Updated Django settings for Railway
- [x] Configured database with environment variables
- [x] Updated CORS settings for Railway domains
- [x] Created Railway configuration file
- [x] Updated Dockerfile for Railway deployment
- [x] Added health check endpoint

## Railway Deployment Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your repository

### 2. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Select the `backend` folder

### 3. Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```bash
# Required Environment Variables
DEBUG=false
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://postgres:HwdCnuWZklkEWApRIhzZjcJMHOhOCMPT@mainline.proxy.rlwy.net:30544/railway
CORS_ALLOW_ALL_ORIGINS=true

# Optional Environment Variables
PAYSTACK_SECRET_KEY=your-paystack-secret-key
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_CALLBACK_URL=https://your-domain.com/api/payments/callback
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-africastalking-api-key
```

### 4. Add PostgreSQL Database
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` environment variable

### 5. Deploy
1. Railway will automatically detect the Dockerfile
2. Click "Deploy" to start the deployment
3. Wait for the build to complete

## Configuration Details

### Database Configuration
- Uses PostgreSQL on Railway
- Automatically configured via `DATABASE_URL` environment variable
- Connection pooling enabled with `conn_max_age=600`
- Health checks enabled

### CORS Settings
- Configured for Railway domains (`*.railway.app`, `*.up.railway.app`)
- Allows all origins in production (configurable via environment variable)
- Supports credentials

### Static Files
- Served via WhiteNoise
- Compressed and cached
- Collected during Docker build

### Security
- CSRF protection enabled
- Trusted origins configured for Railway
- Security headers via middleware

## API Endpoints

### Health Check
- `GET /` - Returns "OK" for health checks

### Authentication
- `POST /api/user/register/` - User registration
- `POST /api/user/login/` - User login
- `POST /api/user/verify-code/` - Phone verification

### Core Features
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/estimates/` - List estimates
- `POST /api/manual_estimate/` - Create manual estimate
- `GET /api/suppliers/` - List suppliers

### Admin
- `GET /api/admin/` - Admin endpoints

## Monitoring & Logs

### Railway Dashboard
- View deployment logs
- Monitor resource usage
- Check environment variables

### Health Monitoring
- Built-in health check endpoint
- Docker health check configured
- Automatic restarts on failure

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Check Dockerfile syntax

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check PostgreSQL service is running
   - Ensure database credentials are correct

3. **CORS Issues**
   - Verify `CORS_ALLOW_ALL_ORIGINS` is set to `true`
   - Check `CORS_ALLOWED_ORIGINS` includes your frontend domain
   - Ensure frontend is making requests to correct Railway URL

4. **Static Files Not Loading**
   - Check `STATIC_ROOT` configuration
   - Verify WhiteNoise is properly configured
   - Ensure `collectstatic` runs during build

### Debugging Commands
```bash
# Check logs in Railway dashboard
# Or use Railway CLI
railway logs

# Connect to running container
railway shell

# Run Django commands
railway run python manage.py migrate
railway run python manage.py collectstatic
```

## Environment-Specific Settings

### Production
- `DEBUG=False`
- `CORS_ALLOW_ALL_ORIGINS=True` (or specific origins)
- Secure `SECRET_KEY`
- Production database URL

### Development
- `DEBUG=True`
- Local database configuration
- Development CORS settings

## Next Steps

1. **Domain Setup**: Configure custom domain in Railway
2. **SSL**: Railway provides automatic SSL certificates
3. **Monitoring**: Set up monitoring and alerts
4. **Backup**: Configure database backups
5. **Scaling**: Adjust resource allocation as needed

## Support
For deployment issues, check:
- [Railway Documentation](https://docs.railway.app/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
