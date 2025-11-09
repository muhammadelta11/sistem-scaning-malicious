"""
Rate limiting middleware untuk API endpoints.
"""

import time
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware untuk rate limiting berdasarkan user.
    
    Rate limit: 100 requests per 60 detik per user.
    """
    
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    
    def process_request(self, request):
        """Proses request untuk rate limiting."""
        # Skip untuk admin dan staff
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return None
        
        # Skip untuk non-API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Skip untuk unauthenticated users (akan ditangani oleh authentication)
        if not request.user.is_authenticated:
            return None
        
        # Rate limit key berdasarkan user ID
        cache_key = f'rate_limit_{request.user.id}'
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        if count >= self.RATE_LIMIT_REQUESTS:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': f'Maksimal {self.RATE_LIMIT_REQUESTS} requests per {self.RATE_LIMIT_WINDOW} detik'
                },
                status=429
            )
        
        # Increment count
        cache.set(cache_key, count + 1, self.RATE_LIMIT_WINDOW)
        
        return None

