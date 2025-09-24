# Railway Internal Server Error Debug Guide

## Issue
After successful deployment to Railway, accessing `https://web-production-c1b96.up.railway.app/` returns an internal server error.

## ✅ **FIXES APPLIED**

### 1. **Updated ALLOWED_HOSTS**
- Added your specific Railway domain: `web-production-c1b96.up.railway.app`
- Added wildcard patterns for Railway domains

### 2. **Updated CSRF_TRUSTED_ORIGINS**
- Added your Railway domain to trusted origins
- Ensures CSRF protection works correctly

### 3. **Added Debug Endpoint**
- New endpoint: `https://web-production-c1b96.up.railway.app/debug/`
- Provides detailed server status information
- Helps identify the root cause of the error

## 🔍 **DEBUGGING STEPS**

### Step 1: Check Debug Endpoint
Visit: `https://web-production-c1b96.up.railway.app/debug/`

This will show you:
- Server status
- Database connection status
- Environment variables
- Static files status
- Any specific errors

### Step 2: Check Railway Logs
1. Go to your Railway dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Click on the latest deployment
5. Check the logs for errors

### Step 3: Test Basic Endpoints
- **Health Check**: `https://web-production-c1b96.up.railway.app/`
- **Debug Info**: `https://web-production-c1b96.up.railway.app/debug/`
- **Admin**: `https://web-production-c1b96.up.railway.app/admin/`

## 🛠️ **COMMON ISSUES & SOLUTIONS**

### Issue 1: Database Connection Error
**Symptoms**: Database-related errors in logs
**Solution**: 
1. Check if PostgreSQL service is running in Railway
2. Verify `DATABASE_URL` environment variable
3. Run migrations manually

### Issue 2: Static Files Error
**Symptoms**: Static file collection errors
**Solution**:
1. Check if `collectstatic` ran successfully
2. Verify WhiteNoise configuration
3. Check static files permissions

### Issue 3: Environment Variables Missing
**Symptoms**: Missing environment variables in debug endpoint
**Solution**:
1. Set required environment variables in Railway dashboard
2. Redeploy the application

### Issue 4: Import Errors
**Symptoms**: Python import errors in logs
**Solution**:
1. Check if all dependencies are installed
2. Verify all Django apps are properly configured
3. Check for missing files

## 🔧 **REQUIRED ENVIRONMENT VARIABLES**

Make sure these are set in Railway:

```bash
DEBUG=false
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://... (auto-provided by Railway)
CORS_ALLOW_ALL_ORIGINS=true
PAYSTACK_SECRET_KEY=your-paystack-key
PAYSTACK_PUBLIC_KEY=your-paystack-key
AFRICASTALKING_API_KEY=your-sms-key
```

## 📋 **TROUBLESHOOTING CHECKLIST**

- [ ] Check Railway logs for specific errors
- [ ] Visit debug endpoint: `/debug/`
- [ ] Verify environment variables are set
- [ ] Check database connection
- [ ] Verify static files are collected
- [ ] Test basic endpoints
- [ ] Check ALLOWED_HOSTS configuration
- [ ] Verify CSRF_TRUSTED_ORIGINS

## 🚀 **NEXT STEPS**

1. **Push the updated code** to GitHub
2. **Railway will automatically redeploy**
3. **Test the debug endpoint**: `https://web-production-c1b96.up.railway.app/debug/`
4. **Check Railway logs** for any remaining errors
5. **Test the main endpoint**: `https://web-production-c1b96.up.railway.app/`

## 📞 **GETTING HELP**

If the issue persists:

1. **Share the debug endpoint output** with me
2. **Copy the Railway logs** (last 50-100 lines)
3. **Check if the health check works**: `https://web-production-c1b96.up.railway.app/`

The debug endpoint will give us detailed information about what's causing the internal server error.
