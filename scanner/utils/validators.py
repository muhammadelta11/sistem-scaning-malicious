"""
Validators untuk aplikasi scanner.
"""

import re
from urllib.parse import urlparse


def validate_domain(domain: str) -> bool:
    """
    Validasi format domain.
    
    Args:
        domain: Domain yang akan divalidasi
        
    Returns:
        True jika valid, False jika tidak
    """
    if not domain or not isinstance(domain, str):
        return False
    
    # Hapus whitespace
    domain = domain.strip()
    
    # Hapus http:// atau https:// jika ada
    domain = re.sub(r'^https?://', '', domain)
    
    # Hapus trailing slash
    domain = domain.rstrip('/')
    
    # Pattern untuk domain valid
    # Mengizinkan: domain.com, subdomain.domain.com, domain.co.id
    domain_pattern = re.compile(
        r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    
    return bool(domain_pattern.match(domain))


def sanitize_domain(domain: str) -> str:
    """
    Sanitize domain (hapus http://, https://, trailing slash, dll).
    
    Args:
        domain: Domain yang akan disanitize
        
    Returns:
        Domain yang sudah disanitize
    """
    if not domain:
        return ''
    
    # Hapus whitespace
    domain = domain.strip()
    
    # Hapus http:// atau https://
    domain = re.sub(r'^https?://', '', domain)
    
    # Hapus www.
    domain = re.sub(r'^www\.', '', domain)
    
    # Hapus trailing slash
    domain = domain.rstrip('/')
    
    # Hapus path jika ada
    parsed = urlparse(f'https://{domain}')
    domain = parsed.netloc or domain
    
    return domain.lower()

