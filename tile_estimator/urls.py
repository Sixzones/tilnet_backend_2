
"""
URL Configuration for tile_estimator project.
"""
import os
import sys
import django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path

import logging
logger = logging.getLogger(__name__)

def health_check(request):
    logger.info("Health check called")
    return HttpResponse("OK")

def debug_info(request):
    """Debug endpoint to check server status"""
    import os
    from django.conf import settings
    
    debug_info = {
        "status": "OK",
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "database_connected": False,
        "static_files": False,
        "environment": {
            "PORT": os.environ.get('PORT', 'Not set'),
            "DATABASE_URL": "Set" if os.environ.get('DATABASE_URL') else "Not set",
            "SECRET_KEY": "Set" if os.environ.get('SECRET_KEY') else "Not set",
        },
        "database_config": str(settings.DATABASES['default']),
        "installed_apps": settings.INSTALLED_APPS,
    }
    
    # Test database connection
    try:
        from django.db import connection
        connection.ensure_connection()
        debug_info["database_connected"] = True
        debug_info["database_type"] = settings.DATABASES['default']['ENGINE']
    except Exception as e:
        debug_info["database_error"] = str(e)
        debug_info["database_connected"] = False
    
    # Test static files
    try:
        import os
        static_root = os.path.join(settings.BASE_DIR, 'staticfiles')
        debug_info["static_files"] = os.path.exists(static_root)
    except Exception as e:
        debug_info["static_error"] = str(e)
    
    from django.http import JsonResponse
    return JsonResponse(debug_info)

def simple_test(request):
    """Simple test endpoint that doesn't require database"""
    return HttpResponse("Simple test endpoint works!")

def status_check(request):
    """Status check endpoint that shows basic Django info"""
    import os
    from django.conf import settings
    
    status = {
        "django_version": django.get_version(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "installed_apps_count": len(settings.INSTALLED_APPS),
        "environment": {
            "PORT": os.environ.get('PORT', 'Not set'),
            "DATABASE_URL": "Set" if os.environ.get('DATABASE_URL') else "Not set",
        }
    }
    
    from django.http import JsonResponse
    return JsonResponse(status)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),
    path('debug/', debug_info),  # Debug endpoint
    path('test/', simple_test),  # Simple test endpoint
    path('status/', status_check),  # Status check endpoint
    path('api/admin/', include('admin_api.urls')),
    path('api/user/', include('accounts.urls')),
    path('api/estimates/', include('estimates.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/manual_estimate/',include('manual_estimate.urls')),
    path('api/projects/', include('projects.urls')),  # New projects URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
