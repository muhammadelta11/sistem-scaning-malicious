"""
Django settings untuk sistem deteksi malicious.

File ini sekarang menggunakan modular settings.
Untuk development: gunakan settings/development.py
Untuk production: set DJANGO_ENVIRONMENT=production dan gunakan settings/production.py

Note: Import dilakukan melalui settings/__init__.py
"""

# Import from settings module (via __init__.py)
import os
from pathlib import Path

# Determine environment
ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

# Import appropriate settings
if ENVIRONMENT == 'production':
    from sistem_deteksi_malicious.settings.production import *
else:
    from sistem_deteksi_malicious.settings.development import *
