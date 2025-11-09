"""
Helper functions untuk aplikasi scanner.
"""

from urllib.parse import urlparse


def format_domain(domain: str) -> str:
    """
    Format domain untuk ditampilkan.
    
    Args:
        domain: Domain yang akan diformat
        
    Returns:
        Domain yang sudah diformat
    """
    if not domain:
        return ''
    
    domain = domain.strip().lower()
    
    # Tambahkan www. jika tidak ada subdomain
    if '.' in domain and domain.count('.') == 1:
        domain = f'www.{domain}'
    
    return domain


def get_domain_from_url(url: str) -> str:
    """
    Ekstrak domain dari URL.
    
    Args:
        url: URL lengkap
        
    Returns:
        Domain dari URL
    """
    if not url:
        return ''
    
    try:
        parsed = urlparse(url)
        return parsed.netloc or ''
    except Exception:
        return ''

