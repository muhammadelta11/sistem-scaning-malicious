"""
Development settings untuk aplikasi sistem deteksi malicious.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts untuk development dengan Parallels
# Ini memungkinkan akses dari macOS host ke Windows VM
ALLOWED_HOSTS = ['*']  # Untuk development dengan Parallels Desktop
# Atau spesifik: ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '10.211.55.3', '10.211.55.2', '10.37.129.2']

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional middleware for development (optional - requires django-debug-toolbar)
# Uncomment and install django-debug-toolbar if you need it:
# if DEBUG:
#     try:
#         import debug_toolbar
#         INSTALLED_APPS += ['debug_toolbar']
#         MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
#         INTERNAL_IPS = ['127.0.0.1']
#     except ImportError:
#         pass

