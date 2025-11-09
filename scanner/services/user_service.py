"""
Service untuk menangani operasi user.
"""

import logging
from typing import List, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from scanner.models import ActivityLog
from scanner.exceptions import ResourceNotFound, PermissionDenied

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """Service untuk mengelola users."""
    
    @staticmethod
    def get_all_users() -> List:
        """
        Mendapatkan semua users.
        
        Returns:
            List of User instances
        """
        return list(User.objects.all().order_by('-date_joined'))
    
    @staticmethod
    def get_user(user_id: int) -> Optional:
        """
        Mendapatkan user berdasarkan ID.
        
        Args:
            user_id: ID user
            
        Returns:
            User instance atau None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def create_user(username: str, email: str, password: str, **kwargs) -> User:
        """
        Membuat user baru.
        
        Args:
            username: Username
            email: Email
            password: Password
            **kwargs: Field tambahan (organization_name, role, dll)
            
        Returns:
            User instance
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
        
        # Log aktivitas
        ActivityLog.objects.create(
            user=None,  # System action
            action='CREATE_USER',
            details=f'Created user: {username}'
        )
        
        logger.info(f"User created: {username}")
        return user
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> User:
        """
        Update user.
        
        Args:
            user_id: ID user
            **kwargs: Field yang akan diupdate
            
        Returns:
            Updated User instance
            
        Raises:
            ResourceNotFound: Jika user tidak ditemukan
        """
        user = UserService.get_user(user_id)
        if not user:
            raise ResourceNotFound(f"User dengan ID {user_id} tidak ditemukan")
        
        # Handle password separately
        if 'password' in kwargs:
            user.set_password(kwargs.pop('password'))
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.save()
        
        # Log aktivitas
        ActivityLog.objects.create(
            user=None,
            action='UPDATE_USER',
            details=f'Updated user: {user.username}'
        )
        
        logger.info(f"User updated: {user.username}")
        return user
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Menghapus user.
        
        Args:
            user_id: ID user
            
        Returns:
            True jika berhasil
            
        Raises:
            ResourceNotFound: Jika user tidak ditemukan
        """
        user = UserService.get_user(user_id)
        if not user:
            raise ResourceNotFound(f"User dengan ID {user_id} tidak ditemukan")
        
        username = user.username
        user.delete()
        
        # Log aktivitas
        ActivityLog.objects.create(
            user=None,
            action='DELETE_USER',
            details=f'Deleted user: {username}'
        )
        
        logger.info(f"User deleted: {username}")
        return True
    
    @staticmethod
    def reset_password(user_id: int, new_password: str) -> User:
        """
        Reset password user.
        
        Args:
            user_id: ID user
            new_password: Password baru
            
        Returns:
            Updated User instance
            
        Raises:
            ResourceNotFound: Jika user tidak ditemukan
        """
        user = UserService.get_user(user_id)
        if not user:
            raise ResourceNotFound(f"User dengan ID {user_id} tidak ditemukan")
        
        user.set_password(new_password)
        user.save()
        
        # Log aktivitas
        ActivityLog.objects.create(
            user=None,
            action='RESET_PASSWORD',
            details=f'Reset password for user: {user.username}'
        )
        
        logger.info(f"Password reset for user: {user.username}")
        return user

