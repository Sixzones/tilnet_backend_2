#!/usr/bin/env python
"""
Test script to debug Railway deployment issues
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tile_estimator.settings')

try:
    # Try to import Django
    print("Testing Django import...")
    django.setup()
    print("✅ Django imported successfully")
    
    # Test basic Django functionality
    print("\nTesting Django functionality...")
    from django.conf import settings
    print(f"✅ Settings loaded: DEBUG={settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Test database connection
    print("\nTesting database connection...")
    from django.db import connection
    connection.ensure_connection()
    print("✅ Database connection successful")
    
    # Test installed apps
    print(f"\n✅ Installed apps: {len(settings.INSTALLED_APPS)} apps")
    for app in settings.INSTALLED_APPS:
        print(f"  - {app}")
    
    # Test URL patterns
    print("\nTesting URL patterns...")
    from django.urls import reverse
    from django.http import HttpResponse
    print("✅ URL patterns loaded successfully")
    
    print("\n🎉 All tests passed! Django is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
