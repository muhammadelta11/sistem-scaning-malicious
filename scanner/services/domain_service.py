"""
Service untuk menangani operasi domain.
"""

import logging
from typing import Dict, Any
from scanner.utils.validators import validate_domain
from scanner.exceptions import DomainValidationError
from scanner import core_scanner

logger = logging.getLogger(__name__)


class DomainService:
    """Service untuk mengelola operasi domain."""
    
    @staticmethod
    def get_domain_intelligence(domain: str) -> Dict[str, Any]:
        """
        Mendapatkan informasi domain (whois, blacklist, dll).
        
        Args:
            domain: Domain target
            
        Returns:
            Dictionary dengan informasi domain
        """
        if not validate_domain(domain):
            raise DomainValidationError(f"Domain tidak valid: {domain}")
        
        try:
            domain_info = core_scanner.domain_intelligence(domain)
            return domain_info
        except Exception as e:
            logger.error(f"Error getting domain intelligence for {domain}: {e}", exc_info=True)
            raise DomainValidationError(f"Gagal mendapatkan informasi domain: {str(e)}")
    
    @staticmethod
    def enumerate_subdomains(domain: str, primary_key: str, fallback_key: str = None) -> Dict[str, Any]:
        """
        Enumerasi subdomain untuk domain tertentu.
        
        Args:
            domain: Domain target
            primary_key: Primary API key
            fallback_key: Fallback API key (opsional)
            
        Returns:
            Dictionary dengan daftar subdomain
        """
        if not validate_domain(domain):
            raise DomainValidationError(f"Domain tidak valid: {domain}")
        
        try:
            subdomain_results = core_scanner.enumerate_subdomains(domain, primary_key, fallback_key)
            return subdomain_results
        except Exception as e:
            logger.error(f"Error enumerating subdomains for {domain}: {e}", exc_info=True)
            raise DomainValidationError(f"Gagal enumerasi subdomain: {str(e)}")

