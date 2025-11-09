"""
Logging middleware untuk tracking requests.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from scanner.models import ActivityLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware untuk logging request dan response.
    """
    
    def process_request(self, request):
        """Attach timestamp ke request untuk menghitung durasi."""
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """Log response setelah request selesai."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log ke ActivityLog untuk API requests penting
            if request.path.startswith('/api/scans') and request.method == 'POST':
                if request.user.is_authenticated:
                    ActivityLog.objects.create(
                        user=request.user,
                        action='API_SCAN_CREATE',
                        details=f'API request: {request.method} {request.path} - {response.status_code} - {duration:.2f}s'
                    )
            
            # Log ke logger
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s - "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
            )
        
        return response

