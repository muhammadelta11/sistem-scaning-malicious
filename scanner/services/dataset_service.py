"""
Service untuk mengelola dataset training.
"""

import logging
from scanner import data_manager
from scanner.exceptions import PermissionDenied, ScannerException

logger = logging.getLogger(__name__)


class DatasetService:
    """Service untuk mengelola dataset training."""
    
    @staticmethod
    def add_to_dataset(url: str, title: str, description: str, label_status: str, user) -> bool:
        """
        Menambahkan data ke dataset training.
        Hanya admin yang bisa melakukan ini.
        
        Args:
            url: URL yang akan ditambahkan
            title: Title dari URL
            description: Description dari URL
            label_status: Label status (malicious/clean)
            user: User yang melakukan action
            
        Returns:
            True jika berhasil, False jika gagal
            
        Raises:
            PermissionDenied: Jika user bukan admin
        """
        # Check permission - hanya admin yang bisa
        if not user.is_admin:
            raise PermissionDenied("Hanya admin yang dapat menambahkan data ke dataset.")
        
        try:
            success = data_manager.add_to_dataset(url, title, description, label_status)
            
            if success:
                logger.info(f"Data added to dataset by {user.username}: {url} ({label_status})")
            else:
                logger.warning(f"Failed to add data to dataset: {url} (may already exist)")
            
            return success
            
        except ValueError as e:
            # Validation error - return False instead of raising
            logger.error(f"Validation error adding to dataset: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding to dataset: {e}", exc_info=True)
            # Don't re-raise, return False to show user-friendly message
            raise ScannerException(f"Gagal menambahkan data ke dataset: {str(e)}")
    
    @staticmethod
    def get_dataset_stats() -> dict:
        """
        Mendapatkan statistik dataset.
        
        Returns:
            Dictionary dengan statistik dataset
        """
        try:
            df = data_manager.load_or_create_dataset()
            
            return {
                'total_records': len(df),
                'by_label': df['label_status'].value_counts().to_dict() if 'label_status' in df.columns else {},
                'latest_date': df['timestamp'].max() if 'timestamp' in df.columns and len(df) > 0 else None,
            }
        except Exception as e:
            logger.error(f"Error getting dataset stats: {e}", exc_info=True)
            return {
                'total_records': 0,
                'by_label': {},
                'latest_date': None,
            }

