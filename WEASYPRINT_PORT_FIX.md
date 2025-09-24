# WeasyPrint & Port Fix for Railway

## Issues Fixed

### 1. WeasyPrint Import Error ✅
**Problem**: `ModuleNotFoundError: No module named 'weasyprint'`
**Solution**: 
- Restored WeasyPrint to requirements-railway.txt
- Fixed Dockerfile to install WeasyPrint dependencies
- Restored original imports in views.py and utils.py

### 2. Railway Port Configuration ✅
**Problem**: Port handling issues on Railway
**Solution**:
- Enhanced startup script with better port handling
- Added Railway health check configuration
- Improved port environment variable handling

## ✅ **Changes Made**

### 1. Requirements Updated
- **`requirements-railway.txt`**: Added WeasyPrint back
- **Dockerfile**: Added all WeasyPrint system dependencies
- **Dependencies**: libcairo2-dev, libpango1.0-dev, libfontconfig1-dev, etc.

### 2. Code Restored
- **`manual_estimate/views.py`**: Restored original WeasyPrint import
- **`manual_estimate/utils.py`**: Restored original WeasyPrint import
- **PDF Generation**: Back to full functionality

### 3. Port Handling Fixed
- **`start-railway.sh`**: Enhanced port detection and handling
- **`railway.toml`**: Added health check configuration
- **Dynamic Port**: Properly handles Railway's dynamic port assignment

### 4. Dockerfile Enhanced
- **WeasyPrint Dependencies**: All required system libraries
- **Better Package Names**: Updated to correct Debian package names
- **Font Support**: Added fontconfig and xrender libraries

## 🚀 **Expected Results**

### After Deployment:
1. **WeasyPrint will install successfully** ✅
2. **PDF generation will work normally** ✅
3. **Port will be handled correctly** ✅
4. **All endpoints will work** ✅
5. **No more import errors** ✅

### Test Endpoints:
- `https://web-production-c1b96.up.railway.app/test/`
- `https://web-production-c1b96.up.railway.app/status/`
- `https://web-production-c1b96.up.railway.app/debug/`

## 📋 **Deployment Steps**

1. **Push Changes**:
```bash
git add .
git commit -m "Restore WeasyPrint and fix Railway port handling"
git push
```

2. **Wait for Railway Redeploy** (3-5 minutes for WeasyPrint build)

3. **Test Endpoints**:
   - Health check: `/`
   - Simple test: `/test/`
   - Status: `/status/`
   - Debug: `/debug/`

## 🔧 **WeasyPrint Dependencies Added**

### System Libraries:
- `libcairo2-dev` - Cairo graphics library
- `libpango1.0-dev` - Text layout library
- `libgdk-pixbuf-2.0-dev` - Image loading library
- `libfontconfig1-dev` - Font configuration
- `libxrender1` - X11 rendering extension

### Python Package:
- `weasyprint==65.1` - HTML to PDF conversion

## 🎯 **Port Handling**

### Railway Dynamic Port:
- Railway sets `PORT` environment variable
- Startup script detects and uses it
- Fallback to port 8000 if not set
- Health check configured for Railway

### Expected Behavior:
```
Using PORT: 8080
Starting Gunicorn server on port 8080...
```

## 📞 **Troubleshooting**

### If Build Still Fails:
1. Check Railway logs for specific errors
2. Verify all system dependencies are installed
3. Check if WeasyPrint builds successfully

### If Port Issues Persist:
1. Check Railway environment variables
2. Verify PORT is set correctly
3. Check health check endpoint

The deployment should now work perfectly with full WeasyPrint functionality and proper port handling! 🎉
