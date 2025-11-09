"""
Service untuk menangani logika scanning domain.
"""

import uuid
import json
import logging
from typing import Dict, Optional, Any
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings

from scanner.models import ScanHistory
from scanner.exceptions import DomainValidationError, ScanProcessingError
from scanner import core_scanner, data_manager
from scanner.utils.validators import validate_domain
from scanner.job_runner import submit_scan_thread

logger = logging.getLogger(__name__)
User = get_user_model()


class ScanService:
    """Service untuk mengelola scanning domain."""
    
    @staticmethod
    def get_api_key_for_scan(user):
        """
        Get API key untuk scan dengan priority:
        1. User's personal key (user.user_api_key) ← Prioritas tertinggi
        2. Active key dari database (ApiKey model) ← Shared key
        3. Admin key dari .env (settings.ADMIN_SERPAPI_KEY) ← Fallback
        
        Returns:
            tuple: (api_key, key_source)
                - api_key: The actual API key string
                - key_source: "user_personal", "database", atau "admin_env"
        """
        # Priority 1: User's personal key (BARU: dipindah ke priority tertinggi)
        if user.user_api_key:
            logger.info(f"Using user's personal API key for {user.username}")
            return user.user_api_key, "user_personal"
        
        # Priority 2: Try get active API key from database (shared key)
        primary_key = None
        key_source = None
        try:
            from scanner.models import ApiKey
            active_key = ApiKey.objects.filter(is_active=True).first()
            if active_key:
                primary_key = active_key.key_value
                key_source = "database"
                # Update last_used timestamp
                active_key.last_used = timezone.now()
                active_key.save(update_fields=['last_used'])
                logger.info(f"Using active API key from database: {active_key.key_name} (shared key for {user.username})")
        except Exception as e:
            logger.warning(f"Could not get API key from database: {e}")
        
        # Priority 3: Fallback to env key
        if not primary_key:
            admin_key = getattr(settings, 'ADMIN_SERPAPI_KEY', None)
            if admin_key:
                primary_key = admin_key
                key_source = "admin_env"
                logger.info(f"Using admin API key from .env (fallback for {user.username})")
        
        if not primary_key:
            raise ScanProcessingError(
                "No API key available. Please configure API key in database or .env file."
            )
        
        return primary_key, key_source

    @staticmethod
    def create_scan(user, domain: str, scan_type: str, enable_verification: bool = True, 
                   show_all_results: bool = False) -> ScanHistory:
        """
        Membuat scan baru dan memulai proses scanning.
        
        Args:
            user: User yang melakukan scan
            domain: Domain target
            scan_type: Tipe scan (Cepat/Komprehensif)
            enable_verification: Aktifkan verifikasi real-time
            show_all_results: Tampilkan semua hasil terindikasi
            
        Returns:
            ScanHistory instance
            
        Raises:
            DomainValidationError: Jika domain tidak valid
        """
        # Validasi domain
        if not validate_domain(domain):
            raise DomainValidationError(f"Domain tidak valid: {domain}")
        
        # Check quota untuk user (kecuali superuser saja)
        from .quota_service import QuotaService
        if not user.is_superuser:
            quota_status = QuotaService.check_quota(user)
            if not quota_status['can_scan']:
                remaining = quota_status['remaining_quota']
                limit = quota_status['quota_limit']
                reset_period = quota_status['reset_period']
                raise ScanProcessingError(
                    f"Kuota scan habis! Anda telah menggunakan {limit} dari {limit} scan. "
                    f"Kuota akan direset {reset_period.lower()}. "
                    f"Hubungi admin untuk meningkatkan kuota."
                )
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Get API keys with priority: Database → User Key → .env
        primary_key, key_source = ScanService.get_api_key_for_scan(user)
        fallback_key = settings.ADMIN_SERPAPI_KEY
        
        logger.info(f"API key source for scan: {key_source}")
        
        # Create ScanHistory object
        scan_obj = ScanHistory.objects.create(
            scan_id=scan_id,
            user=user,
            domain=domain,
            status='PENDING',
            scan_type=scan_type,
            ran_with_verification=enable_verification,
            showed_all_results=show_all_results
        )
        
        # Prepare scan data for cache
        scan_data = {
            'scan_id': scan_id,
            'scan_pk': scan_obj.pk,  # Primary key untuk navigasi ke detail page
            'domain': domain,
            'status': 'processing',
            'start_time': scan_obj.start_time.isoformat(),
            'results': None,
            'error': None
        }
        
        # Get or create user scans cache
        user_scans = cache.get(f'user_scans_{user.id}', {})
        user_scans[scan_id] = scan_data
        cache.set(f'user_scans_{user.id}', user_scans, timeout=604800)
        
        # Update status to processing
        scan_obj.status = 'PROCESSING'
        scan_obj.save()
        
        # Use quota untuk user (kecuali superuser saja)
        if not user.is_superuser:
            logger.info(f"Attempting to use quota for user {user.username} (is_superuser={user.is_superuser}, is_staff={user.is_staff})")
            quota_used = QuotaService.use_quota(user, count=1)
            logger.info(f"Quota use result for {user.username}: {quota_used}")
            if not quota_used:
                scan_obj.status = 'FAILED'
                scan_obj.error_message = "Kuota scan habis"
                scan_obj.save()
                raise ScanProcessingError("Kuota scan habis. Hubungi admin untuk meningkatkan kuota.")
        else:
            logger.info(f"Skipping quota usage for {user.username} (superuser - unlimited)")
        
        # Run scan asynchronously via thread
        try:
            submit_scan_thread(
                scan_pk=scan_obj.pk,
                scan_id=scan_id,
                domain=domain,
                primary_key=primary_key,
                fallback_key=fallback_key,
                scan_type=scan_type,
                enable_verification=enable_verification,
                user_id=user.id,
                show_all_results=show_all_results
            )
            logger.info(f"Scan {scan_id} submitted for domain {domain}")
        except Exception as e:
            logger.error(f"Error submitting scan {scan_id}: {e}", exc_info=True)
            scan_obj.status = 'FAILED'
            scan_obj.error_message = str(e)
            scan_obj.save()
            raise ScanProcessingError(f"Gagal memulai scan: {str(e)}")
        
        return scan_obj
    
    @staticmethod
    def get_scan(scan_id: str, user) -> Optional[ScanHistory]:
        """
        Mendapatkan scan berdasarkan scan_id.
        
        Args:
            scan_id: ID scan
            user: User yang melakukan request
            
        Returns:
            ScanHistory instance atau None
        """
        try:
            scan = ScanHistory.objects.get(scan_id=scan_id, user=user)
            return scan
        except ScanHistory.DoesNotExist:
            return None
    
    @staticmethod
    def get_scan_progress(scan_id: str) -> Dict[str, Any]:
        """
        Mendapatkan progress scan dari cache.
        
        Args:
            scan_id: ID scan
            
        Returns:
            Dictionary dengan status progress
        """
        progress_data = cache.get(f'scan_progress_{scan_id}')
        
        if not progress_data:
            # Try to get from database
            try:
                scan = ScanHistory.objects.get(scan_id=scan_id)
                if scan.status == 'PROCESSING':
                    progress_data = {
                        'status': 'PROCESSING',
                        'phase': 'Unknown',
                        'message': 'Memproses... (data progres tidak ditemukan)'
                    }
                elif scan.status == 'FAILED':
                    progress_data = {
                        'status': 'FAILED',
                        'phase': 'Error',
                        'message': scan.error_message or 'Gagal.'
                    }
                elif scan.status == 'COMPLETED':
                    progress_data = {
                        'status': 'COMPLETED',
                        'message': 'Selesai.'
                    }
            except ScanHistory.DoesNotExist:
                return {'status': 'NOT_FOUND', 'message': 'Scan tidak ditemukan'}
        
        if not progress_data:
            return {'status': 'PENDING', 'message': 'Memulai...'}
        
        return progress_data
    
    @staticmethod
    def get_user_scans(user, limit: int = 50) -> Dict[str, Any]:
        """
        Mendapatkan semua scan milik user.
        Menggabungkan data dari cache (untuk scan aktif/baru) dan database (untuk scan history).
        
        Args:
            user: User yang melakukan request
            limit: Maksimal jumlah scan yang diambil dari database (default: 50)
            
        Returns:
            Dictionary dengan daftar scan, format: {scan_id: scan_data}
        """
        import json
        from datetime import datetime
        
        # 1. Ambil data dari cache (untuk scan yang sedang berjalan atau baru selesai)
        user_scans = cache.get(f'user_scans_{user.id}', {})
        if not isinstance(user_scans, dict):
            user_scans = {}
        
        # Normalisasi data dari cache juga (untuk memastikan struktur lengkap)
        # Juga tambahkan missing fields dari database jika perlu
        from scanner.utils.normalizers import normalize_scan_results
        for scan_id, scan_data in user_scans.items():
            if isinstance(scan_data, dict) and scan_data.get('results'):
                try:
                    scan_data['results'] = normalize_scan_results(scan_data['results'])
                except Exception as e:
                    logger.warning(f"Error normalizing cache results for scan {scan_id}: {e}")
            
            # Pastikan field penting ada (dari database jika tidak ada di cache)
            if isinstance(scan_data, dict):
                if 'scan_type' not in scan_data or 'ran_with_verification' not in scan_data:
                    try:
                        scan_obj = ScanHistory.objects.get(scan_id=scan_id, user=user)
                        if 'scan_type' not in scan_data:
                            scan_data['scan_type'] = scan_obj.scan_type
                        if 'ran_with_verification' not in scan_data:
                            scan_data['ran_with_verification'] = scan_obj.ran_with_verification
                        if 'end_time' not in scan_data:
                            scan_data['end_time'] = scan_obj.end_time
                    except ScanHistory.DoesNotExist:
                        pass
        
        # 2. Ambil data dari database (untuk scan history yang mungkin sudah expire dari cache)
        db_scans = ScanHistory.objects.filter(user=user).order_by('-start_time')[:limit]
        
        # 3. Konversi database scans ke format yang sama dengan cache
        for scan in db_scans:
            scan_id = scan.scan_id
            
            # Skip jika sudah ada di cache (cache data lebih update)
            if scan_id in user_scans:
                # Update scan_pk jika belum ada di cache data
                if 'scan_pk' not in user_scans[scan_id]:
                    user_scans[scan_id]['scan_pk'] = scan.pk
                continue
            
            # Parse scan results JSON
            results = None
            if scan.scan_results_json:
                try:
                    results = json.loads(scan.scan_results_json)
                    # Normalisasi hasil scan untuk memastikan struktur lengkap
                    from scanner.utils.normalizers import normalize_scan_results
                    results = normalize_scan_results(results)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing scan results for scan {scan_id}: {e}")
                    results = None
            
            # Prioritas utama: ambil dari permanent storage untuk semua user
            try:
                from scanner.services import PermanentStorageService
                permanent_results = PermanentStorageService.get_scan_result(scan)
                if permanent_results:
                    results = permanent_results
                    # Normalisasi hasil scan
                    from scanner.utils.normalizers import normalize_scan_results
                    results = normalize_scan_results(results)
                    logger.info(f"Retrieved scan results from permanent storage for user {user.username} (scan_id: {scan_id})")
            except Exception as e:
                logger.warning(f"Error retrieving permanent storage for scan {scan_id}: {e}")
            
            # Konversi status
            status_map = {
                'PENDING': 'pending',
                'PROCESSING': 'processing',
                'COMPLETED': 'completed',
                'FAILED': 'failed'
            }
            status = status_map.get(scan.status, 'pending')
            
            # Format start_time
            start_time_str = scan.start_time.isoformat() if scan.start_time else datetime.now().isoformat()
            
            # Format end_time
            end_time_str = scan.end_time.isoformat() if scan.end_time else None
            
            # Buat scan data dalam format yang sama dengan cache
            scan_data = {
                'scan_id': scan_id,
                'scan_pk': scan.pk,
                'domain': scan.domain,
                'status': status,
                'start_time': start_time_str,
                'end_time': scan.end_time,  # Keep as datetime object for duration calculation
                'results': results,
                'error': scan.error_message if scan.error_message else None,
                'scan_type': scan.scan_type,
                'ran_with_verification': scan.ran_with_verification,
            }
            
            # Tambahkan ke user_scans (hanya jika belum ada di cache)
            user_scans[scan_id] = scan_data
        
        # 4. Sort berdasarkan start_time (terbaru di atas)
        # Convert to list, sort, then back to dict
        sorted_scans = sorted(
            user_scans.items(),
            key=lambda x: x[1].get('start_time', ''),
            reverse=True
        )
        user_scans = dict(sorted_scans)
        
        return user_scans
    
    @staticmethod
    def get_scan_history(user, limit: int = 10) -> list:
        """
        Mendapatkan riwayat scan user dari database.
        
        Args:
            user: User yang melakukan request
            limit: Jumlah scan yang diambil
            
        Returns:
            List of ScanHistory instances
        """
        return ScanHistory.objects.filter(user=user).order_by('-start_time')[:limit]

