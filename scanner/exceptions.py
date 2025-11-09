"""
Custom exceptions untuk aplikasi scanner.
"""


class ScannerException(Exception):
    """Base exception untuk semua scanner exceptions."""
    pass


class DomainValidationError(ScannerException):
    """Exception ketika domain tidak valid."""
    pass


class APIKeyError(ScannerException):
    """Exception ketika API key tidak valid atau habis."""
    pass


class ScanProcessingError(ScannerException):
    """Exception ketika scan gagal diproses."""
    pass


class RateLimitExceeded(ScannerException):
    """Exception ketika rate limit terlampaui."""
    pass


class ResourceNotFound(ScannerException):
    """Exception ketika resource tidak ditemukan."""
    pass


class PermissionDenied(ScannerException):
    """Exception ketika permission ditolak."""
    pass

