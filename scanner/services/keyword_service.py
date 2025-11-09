"""
Service untuk menangani operasi keyword.
"""

import logging
from typing import List, Optional
from django.contrib.auth import get_user_model
from scanner.models import MaliciousKeyword
from scanner.exceptions import ResourceNotFound, PermissionDenied
from scanner import core_scanner

logger = logging.getLogger(__name__)
User = get_user_model()


class KeywordService:
    """Service untuk mengelola malicious keywords."""
    
    @staticmethod
    def get_all_keywords(active_only: bool = False) -> List[MaliciousKeyword]:
        """
        Mendapatkan semua keywords.
        
        Args:
            active_only: Hanya ambil keywords yang aktif
            
        Returns:
            List of MaliciousKeyword instances
        """
        queryset = MaliciousKeyword.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        return list(queryset.order_by('-created_at'))
    
    @staticmethod
    def get_keyword(keyword_id: int) -> Optional[MaliciousKeyword]:
        """
        Mendapatkan keyword berdasarkan ID.
        
        Args:
            keyword_id: ID keyword
            
        Returns:
            MaliciousKeyword instance atau None
        """
        try:
            return MaliciousKeyword.objects.get(id=keyword_id)
        except MaliciousKeyword.DoesNotExist:
            return None
    
    @staticmethod
    def create_keyword(keyword: str, category: str, is_active: bool = True, 
                      created_by=None) -> MaliciousKeyword:
        """
        Membuat keyword baru.
        
        Args:
            keyword: Kata kunci
            category: Kategori keyword
            is_active: Apakah keyword aktif
            created_by: User yang membuat keyword
            
        Returns:
            MaliciousKeyword instance
        """
        keyword_obj = MaliciousKeyword.objects.create(
            keyword=keyword,
            category=category,
            is_active=is_active,
            created_by=created_by
        )
        
        # Clear cache untuk memaksa reload keywords
        core_scanner.get_active_malicious_keywords.cache_clear()
        
        logger.info(f"Keyword created: {keyword} ({category})")
        return keyword_obj
    
    @staticmethod
    def update_keyword(keyword_id: int, keyword: str = None, category: str = None, 
                      is_active: bool = None) -> MaliciousKeyword:
        """
        Update keyword.
        
        Args:
            keyword_id: ID keyword
            keyword: Kata kunci baru (opsional)
            category: Kategori baru (opsional)
            is_active: Status aktif baru (opsional)
            
        Returns:
            Updated MaliciousKeyword instance
            
        Raises:
            ResourceNotFound: Jika keyword tidak ditemukan
        """
        keyword_obj = KeywordService.get_keyword(keyword_id)
        if not keyword_obj:
            raise ResourceNotFound(f"Keyword dengan ID {keyword_id} tidak ditemukan")
        
        if keyword is not None:
            keyword_obj.keyword = keyword
        if category is not None:
            keyword_obj.category = category
        if is_active is not None:
            keyword_obj.is_active = is_active
        
        keyword_obj.save()
        
        # Clear cache
        core_scanner.get_active_malicious_keywords.cache_clear()
        
        logger.info(f"Keyword updated: {keyword_obj.keyword}")
        return keyword_obj
    
    @staticmethod
    def delete_keyword(keyword_id: int) -> bool:
        """
        Menghapus keyword.
        
        Args:
            keyword_id: ID keyword
            
        Returns:
            True jika berhasil
            
        Raises:
            ResourceNotFound: Jika keyword tidak ditemukan
        """
        keyword_obj = KeywordService.get_keyword(keyword_id)
        if not keyword_obj:
            raise ResourceNotFound(f"Keyword dengan ID {keyword_id} tidak ditemukan")
        
        keyword_name = keyword_obj.keyword
        keyword_obj.delete()
        
        # Clear cache
        core_scanner.get_active_malicious_keywords.cache_clear()
        
        logger.info(f"Keyword deleted: {keyword_name}")
        return True
    
    @staticmethod
    def toggle_keyword(keyword_id: int) -> MaliciousKeyword:
        """
        Toggle status aktif/nonaktif keyword.
        
        Args:
            keyword_id: ID keyword
            
        Returns:
            Updated MaliciousKeyword instance
            
        Raises:
            ResourceNotFound: Jika keyword tidak ditemukan
        """
        keyword_obj = KeywordService.get_keyword(keyword_id)
        if not keyword_obj:
            raise ResourceNotFound(f"Keyword dengan ID {keyword_id} tidak ditemukan")
        
        keyword_obj.is_active = not keyword_obj.is_active
        keyword_obj.save()
        
        # Clear cache
        core_scanner.get_active_malicious_keywords.cache_clear()
        
        logger.info(f"Keyword toggled: {keyword_obj.keyword} -> {'active' if keyword_obj.is_active else 'inactive'}")
        return keyword_obj

