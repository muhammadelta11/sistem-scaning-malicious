# sistem_deteksi_malicious/celery.py

import os
from celery import Celery
import platform
import logging
# import eventlet
# eventlet.monkey_patch()

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_deteksi_malicious.settings')

app = Celery('sistem_deteksi_malicious')

# Load config from Django settings, the CELERY_ namespace keys
app.config_from_object('django.conf:settings', namespace='CELERY')

# ✨ Tambahkan baris ini agar Celery pakai Redis, bukan RabbitMQ
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# Force a Windows-safe pool by default (eventlet/gevent cause issues on Windows)
if platform.system().lower().startswith('win'):
    app.conf.worker_pool = 'solo'
    app.conf.worker_prefetch_multiplier = 1
    logging.getLogger(__name__).info("Celery configured to use 'solo' pool on Windows for compatibility.")

# Ensure we don't use eventlet or gevent
app.conf.worker_pool = 'solo'  # Default to solo pool for compatibility
app.conf.task_always_eager = False  # Set to True for testing (runs tasks synchronously)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
