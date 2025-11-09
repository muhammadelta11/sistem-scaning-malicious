"""
Service untuk mengelola kuota scan user.
"""

import logging
from typing import Optional, Dict, Any
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from scanner.models import UserScanQuota

User = get_user_model()
logger = logging.getLogger(__name__)


class QuotaService:
    """Service untuk mengelola kuota scan user."""
    
    @staticmethod
    def get_or_create_quota(user) -> UserScanQuota:
        """
        Get atau create quota untuk user.
        
        Args:
            user: User instance
            
        Returns:
            UserScanQuota instance
        """
        quota, created = UserScanQuota.objects.get_or_create(
            user=user,
            defaults={
                'quota_limit': 10,  # Default 10 scans
                'reset_period': 'monthly',
                'last_reset': timezone.now(),
            }
        )
        
        if created:
            # Set next reset time
            quota._calculate_next_reset()
            quota.save()
            logger.info(f"Created quota for user {user.username}: {quota.quota_limit} scans")
        # Note: Tidak ada auto-fix untuk quota_limit=0 yang sudah ada
        # Admin bisa set unlimited (0) untuk client user jika diperlukan
        
        return quota
    
    @staticmethod
    def check_quota(user) -> Dict[str, Any]:
        """
        Cek apakah user masih memiliki kuota untuk scan.
        
        Args:
            user: User instance
            
        Returns:
            dict dengan status kuota
        """
        quota = QuotaService.get_or_create_quota(user)
        
        # Check and reset if needed
        quota._check_and_reset()
        
        can_scan = quota.can_scan()
        
        return {
            'can_scan': can_scan,
            'quota_limit': quota.quota_limit,
            'used_quota': quota.used_quota,
            'remaining_quota': quota.remaining_quota,
            'is_unlimited': quota.is_unlimited,
            'reset_period': quota.get_reset_period_display(),
            'next_reset': quota.next_reset,
            'last_reset': quota.last_reset,
        }
    
    @staticmethod
    def use_quota(user, count=1) -> bool:
        """
        Gunakan kuota scan user.
        
        Args:
            user: User instance
            count: Jumlah kuota yang digunakan (default: 1)
            
        Returns:
            True jika berhasil, False jika kuota habis
        """
        # Use database transaction with select_for_update to prevent race conditions
        with transaction.atomic():
            # Lock the quota row for update to prevent concurrent modifications
            try:
                quota = UserScanQuota.objects.select_for_update().get(user=user)
            except UserScanQuota.DoesNotExist:
                # Create quota if it doesn't exist
                quota = UserScanQuota.objects.create(
                    user=user,
                    quota_limit=10,
                    reset_period='monthly',
                    last_reset=timezone.now()
                )
                quota._calculate_next_reset()
                quota.save()
                logger.info(f"Created quota for user {user.username}: {quota.quota_limit} scans")
            
            # Check and reset if needed (this will save if reset happens)
            quota._check_and_reset()
            
            # Check if user can scan
            if quota.is_unlimited:
                logger.info(f"User {user.username} has unlimited quota (quota_limit={quota.quota_limit}), skipping quota usage")
                return True
            
            if quota.is_exceeded:
                logger.warning(f"Quota exceeded for user {user.username}: {quota.used_quota}/{quota.quota_limit}")
                return False
            
            # Get before value for logging
            before_used = quota.used_quota
            
            # Increment used_quota
            quota.used_quota += count
            quota.save(update_fields=['used_quota', 'updated_at'])
            
            logger.info(f"Used quota for user {user.username}: {count} scan(s) used. Before: {before_used}/{quota.quota_limit}, After: {quota.used_quota}/{quota.quota_limit}, Remaining: {quota.remaining_quota}")
            
            # Verify the save worked
            quota.refresh_from_db(fields=['used_quota', 'updated_at'])
            if quota.used_quota == before_used:
                logger.error(f"ERROR: Quota did not increment for {user.username}! Still at {quota.used_quota}/{quota.quota_limit}")
                return False
            
            return True
    
    @staticmethod
    def update_quota(user, quota_limit: Optional[int] = None, 
                     reset_period: Optional[str] = None,
                     used_quota: Optional[int] = None) -> UserScanQuota:
        """
        Update kuota user (untuk admin).
        
        Args:
            user: User instance
            quota_limit: Batas kuota (0 = unlimited)
            reset_period: Periode reset ('daily', 'weekly', 'monthly', 'yearly', 'never')
            used_quota: Reset used quota ke nilai tertentu
            
        Returns:
            Updated UserScanQuota instance
        """
        quota = QuotaService.get_or_create_quota(user)
        
        # Track changes untuk logging
        old_limit = quota.quota_limit
        old_period = quota.reset_period
        
        if quota_limit is not None:
            quota.quota_limit = int(quota_limit)
        
        if reset_period is not None:
            quota.reset_period = reset_period
        
        # Recalculate next_reset if quota_limit or reset_period changed
        if quota_limit is not None or reset_period is not None:
            quota._calculate_next_reset()
        
        if used_quota is not None:
            quota.used_quota = int(used_quota)
        
        # Save dengan update_fields untuk memastikan semua field tersimpan
        quota.save(update_fields=['quota_limit', 'used_quota', 'reset_period', 'next_reset', 'updated_at'])
        
        logger.info(f"Updated quota for user {user.username}: limit={old_limit}→{quota.quota_limit}, reset={old_period}→{quota.reset_period}, used={quota.used_quota}")
        return quota
    
    @staticmethod
    def reset_quota(user) -> UserScanQuota:
        """
        Reset kuota user ke 0.
        
        Args:
            user: User instance
            
        Returns:
            Updated UserScanQuota instance
        """
        quota = QuotaService.get_or_create_quota(user)
        quota.used_quota = 0
        quota.last_reset = timezone.now()
        quota._calculate_next_reset()
        quota.save()
        
        logger.info(f"Reset quota for user {user.username}")
        return quota

