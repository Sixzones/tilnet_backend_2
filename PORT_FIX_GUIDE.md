# PORT Variable Fix for Railway

## Issue
Railway was throwing an error: `'$PORT' is not a valid port number.`

## Root Cause
The `$PORT` environment variable was not being properly expanded in the Dockerfile and startup scripts.

## ✅ **FIXED**

### Changes Made:

1. **Dockerfile Updates:**
   - Changed `EXPOSE $PORT` to `EXPOSE 8000`
   - Updated health check to use port 8000
   - Created Railway-specific startup script

2. **Startup Script Updates:**
   - Created `start-railway.sh` with proper PORT handling
   - Uses `${PORT:-8000}` syntax for default fallback
   - Added PORT logging for debugging

3. **Railway Configuration:**
   - Updated `railway.toml` to use the new startup script
   - Simplified start command

## How It Works Now:

1. **Railway sets PORT environment variable** (e.g., PORT=3000)
2. **Startup script reads PORT** and uses it
3. **Gunicorn binds to 0.0.0.0:$PORT**
4. **Dockerfile exposes port 8000** as fallback

## Files Updated:

- ✅ `Dockerfile` - Fixed EXPOSE and health check
- ✅ `start-railway.sh` - New Railway-specific startup script
- ✅ `railway.toml` - Updated start command
- ✅ `start.sh` - Updated with PORT fallback

## Testing:

### Local Test:
```bash
# Test with default port
docker run -p 8000:8000 tilnet-backend

# Test with custom port
docker run -p 3000:3000 -e PORT=3000 tilnet-backend
```

### Railway Test:
1. Push changes to GitHub
2. Railway will automatically rebuild
3. Check logs for "Using PORT: XXXX" message
4. Verify API endpoints work

## Expected Output:
```
Starting Tilnet Django Backend...
Using PORT: 3000
Running database migrations...
Collecting static files...
Starting Gunicorn server on port 3000...
```

## Troubleshooting:

### If PORT still not working:
1. Check Railway logs for PORT value
2. Verify environment variables are set
3. Check if startup script is executable
4. Try manual port binding

### Debug Commands:
```bash
# Check if PORT is set
echo $PORT

# Test startup script manually
./start-railway.sh

# Check Gunicorn binding
netstat -tlnp | grep :8000
```

## ✅ **Ready to Deploy**

The PORT issue is now fixed! Railway should be able to deploy successfully.

**Next Steps:**
1. Push changes to GitHub
2. Railway will rebuild automatically
3. Check deployment logs
4. Test API endpoints
