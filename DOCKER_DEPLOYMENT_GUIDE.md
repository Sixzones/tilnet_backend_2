# Docker Deployment Guide for Railway

## Issue Resolution

The original build was failing due to package compatibility issues with WeasyPrint dependencies in Debian Trixie. Here are the solutions:

## Dockerfile Options

### 1. **Dockerfile** (Recommended for Railway)
- Uses Python 3.11-slim base
- Simplified dependencies without WeasyPrint
- Optimized for Railway deployment
- Fastest build time

### 2. **Dockerfile.simple** (Minimal)
- Minimal dependencies
- Fastest build
- Good for basic functionality
- No PDF generation with WeasyPrint

### 3. **Dockerfile.alternative** (Full Features)
- Uses Ubuntu 22.04 base
- Includes all WeasyPrint dependencies
- Slower build but full PDF functionality
- More stable package availability

## Quick Fix for Current Issue

The build is failing because `libgdk-pixbuf2.0-0` package is not available in Debian Trixie. 

**Immediate Solution:**
1. Use the updated `Dockerfile` (already fixed)
2. Or switch to `Dockerfile.simple` for minimal setup
3. Or use `Dockerfile.alternative` for full features

## Deployment Steps

### Option 1: Use Fixed Dockerfile (Recommended)
```bash
# The main Dockerfile is already updated
# Just redeploy on Railway
```

### Option 2: Use Simple Dockerfile
```bash
# Rename the simple version
mv Dockerfile.simple Dockerfile
# Redeploy on Railway
```

### Option 3: Use Alternative Dockerfile
```bash
# Rename the alternative version
mv Dockerfile.alternative Dockerfile
# Redeploy on Railway
```

## Package Issues Resolved

### Fixed Package Names:
- `libgdk-pixbuf2.0-0` → `libgdk-pixbuf-2.0-0`
- Added additional WeasyPrint dependencies
- Removed problematic packages temporarily

### WeasyPrint Status:
- **Temporarily disabled** in main Dockerfile
- **Available** in alternative Dockerfile
- **Not included** in simple Dockerfile

## Environment Variables

Make sure these are set in Railway:

```bash
DEBUG=false
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
CORS_ALLOW_ALL_ORIGINS=true
```

## Testing the Build

### Local Testing:
```bash
# Test the fixed Dockerfile
docker build -t tilnet-backend .

# Test simple version
docker build -f Dockerfile.simple -t tilnet-backend-simple .

# Test alternative version
docker build -f Dockerfile.alternative -t tilnet-backend-alt .
```

### Railway Testing:
1. Push changes to GitHub
2. Railway will automatically rebuild
3. Check logs for any remaining issues

## Troubleshooting

### If Build Still Fails:
1. Check Railway logs for specific error
2. Try `Dockerfile.simple` for minimal setup
3. Use `Dockerfile.alternative` for full features
4. Check package availability in Debian repos

### Common Issues:
- **Package not found**: Use alternative Dockerfile
- **Permission denied**: Check file permissions
- **Memory issues**: Reduce build complexity
- **Timeout**: Use simpler Dockerfile

## Next Steps

1. **Deploy with fixed Dockerfile** (recommended)
2. **Test all API endpoints**
3. **Add WeasyPrint back later** if needed
4. **Monitor performance** and adjust as needed

## WeasyPrint Re-enablement

To re-enable WeasyPrint later:

1. Use `Dockerfile.alternative`
2. Or add WeasyPrint dependencies back to main Dockerfile
3. Test thoroughly before production deployment

The current setup will work perfectly for all core functionality without PDF generation via WeasyPrint.
