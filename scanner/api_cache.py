"""
Modul caching untuk hasil API Search untuk mengurangi penggunaan quota SerpAPI.
Menyimpan hasil search dalam cache Redis/Database dengan TTL.
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# TTL untuk cache hasil search (dalam detik)
SEARCH_CACHE_TTL = 7 * 24 * 3600  # 7 hari

def get_cache_key(query: str, engine: str = 'google') -> str:
    """
    Generate cache key untuk query tertentu.
    
    Args:
        query: Query search string
        engine: Search engine (google, bing, dll)
        
    Returns:
        Cache key string
    """
    # Normalisasi query untuk consistency
    normalized_query = query.strip().lower()
    
    # Hash query untuk key yang unik
    query_hash = hashlib.md5(normalized_query.encode('utf-8')).hexdigest()
    
    return f'search_api_cache_{engine}_{query_hash}'

def get_cached_search_result(query: str, engine: str = 'google'):
    """
    Ambil hasil search dari cache jika ada.
    
    Args:
        query: Query search string
        engine: Search engine
        
    Returns:
        Hasil search atau None jika tidak ada di cache
    """
    cache_key = get_cache_key(query, engine)
    
    try:
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache HIT untuk query: {query[:100]}")
            return cached_result  # Return full cached data
        else:
            logger.debug(f"Cache MISS untuk query: {query[:100]}")
            return None
    except Exception as e:
        logger.error(f"Error reading cache: {e}")
        return None

def set_cached_search_result(query: str, result: dict, engine: str = 'google', ttl: int = None):
    """
    Simpan hasil search ke cache.
    
    Args:
        query: Query search string
        result: Hasil search dari API
        engine: Search engine
        ttl: Time to live dalam detik (default: SEARCH_CACHE_TTL)
    """
    cache_key = get_cache_key(query, engine)
    
    if ttl is None:
        ttl = SEARCH_CACHE_TTL
    
    try:
        # Tambahkan metadata cache
        cached_data = {
            'query': query,
            'engine': engine,
            'result': result,
            'cached_at': datetime.now().isoformat(),
            'ttl': ttl
        }
        
        cache.set(cache_key, cached_data, timeout=ttl)
        logger.info(f"Hasil search di-cache untuk query: {query[:100]}")
    except Exception as e:
        logger.error(f"Error setting cache: {e}")

def clear_search_cache(query: str = None, engine: str = None):
    """
    Clear cache search (specific atau all).
    
    Args:
        query: Query spesifik yang akan di-clear (None untuk all)
        engine: Engine spesifik yang akan di-clear (None untuk all)
    """
    try:
        if query:
            cache_key = get_cache_key(query, engine or 'google')
            cache.delete(cache_key)
            logger.info(f"Cache cleared untuk query: {query[:100]}")
        else:
            # Clear all cache (harus hati-hati dengan ini)
            logger.warning("Attempting to clear ALL search cache")
            # Implementation tergantung pada cache backend
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

def get_cache_stats():
    """
    Get statistics tentang cache usage.
    """
    # Implementation tergantung pada cache backend
    # Redis: bisa gunakan SCAN untuk count keys dengan pattern
    # Database: query count dari table cache
    return {
        'cache_backend': settings.CACHES['default']['BACKEND'],
        'ttl': SEARCH_CACHE_TTL,
        'note': 'Cache stats implementation depends on backend'
    }

def cache_search_result(func):
    """
    Decorator untuk otomatis cache hasil search API.
    
    Usage:
        @cache_search_result
        def my_search_function(query, api_key):
            # search logic
            return results
    """
    def wrapper(*args, **kwargs):
        # Extract query from args/kwargs
        # Assume query is first positional arg or in kwargs
        query = args[0] if args else kwargs.get('query', '')
        engine = kwargs.get('engine', 'google')
        
        # Try to get from cache
        cached_result = get_cached_search_result(query, engine)
        if cached_result:
            return cached_result.get('result')
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Cache result
        if result:
            set_cached_search_result(query, result, engine)
        
        return result
    
    return wrapper

