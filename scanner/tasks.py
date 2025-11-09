from celery import shared_task
from django.utils import timezone
from .models import ScanHistory
from . import core_scanner
from . import data_manager
from .utils.json_encoder import json_dumps_safe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(soft_time_limit=900, time_limit=1200, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_scan_task(scan_pk, scan_id, domain, primary_key, fallback_key, scan_type, enable_backlink, enable_verification, user_id, show_all_results=False):
    """Celery task to run domain scan asynchronously"""
    try:
        from django.core.cache import cache
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the ScanHistory object
        scan_obj = ScanHistory.objects.get(pk=scan_pk)
        user = User.objects.get(pk=user_id)

        # Publish initial progress to cache
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Starting',
            'message': f"Menyiapkan scan untuk {domain}..."
        }, timeout=3600)

        # Load model & mapping
        model, label_mapping, _ = data_manager.load_resources()
        if not label_mapping:
            label_mapping = {1: 'hack judol', 2: 'pornografi', 3: 'hacked', 0: 'aman'}

        # Perform the scan
        # Pilih flow berdasarkan settings.USE_NATIVE_FLOW
        # Allow UI override via cache
        flow_override = cache.get('scanner_use_native_flow')
        use_native = flow_override if flow_override is not None else getattr(settings, 'USE_NATIVE_FLOW', True)
        if use_native:
            scan_results_data = core_scanner.perform_native_scan(
                domain, primary_key, fallback_key, scan_type, enable_backlink,
                model, label_mapping, enable_verification,
                scan_id=scan_id
            )
        else:
            scan_results_data = core_scanner.perform_verified_scan(
                domain, primary_key, fallback_key, scan_type, enable_backlink,
                model, label_mapping, enable_verification, show_all_results,
                scan_id=scan_id
            )

        # Normalisasi hasil scan sebelum disimpan (memastikan struktur lengkap)
        from scanner.utils.normalizers import normalize_scan_results
        normalized_results = normalize_scan_results(scan_results_data)
        
        # Update scan object with results
        scan_obj.status = 'COMPLETED'
        scan_obj.end_time = timezone.now()
        # Use safe JSON encoder untuk handle numpy types
        scan_obj.scan_results_json = json_dumps_safe(normalized_results)
        scan_obj.save()

        # Auto-update dashboard jika scan completed
        try:
            from .services import DashboardService
            DashboardService.update_dashboard_from_scan_results(domain, scan_results_data)
        except Exception as e:
            logger.warning(f"Failed to update dashboard: {e}", exc_info=True)

        # Simpan hasil scan secara terstruktur ke database (SEMUA USER, bukan hanya premium)
        # Ini menyimpan setiap URL, title, description, label, dan subdomain ke tabel terpisah
        try:
            from .services.scan_result_storage_service import ScanResultStorageService
            storage_stats = ScanResultStorageService.save_scan_results(scan_obj, normalized_results)
            logger.info(
                f"✓ Saved structured scan data for {domain} (Scan ID: {scan_id}): "
                f"{storage_stats['items_saved']} items, {storage_stats['subdomains_saved']} subdomains"
            )
        except Exception as e:
            logger.error(f"Failed to save structured scan data: {e}", exc_info=True)
            # Jangan raise exception - scan tetap dianggap berhasil meskipun structured storage gagal

        # Save permanent storage untuk semua user (tidak tergantung kondisi user)
        try:
            from .services import PermanentStorageService
            logger.info(f"Attempting to save permanent storage for user {user.username} (scan_id: {scan_id})")
            permanent_result = PermanentStorageService.save_scan_result(scan_obj, normalized_results)

            # Verify saved data
            if permanent_result and permanent_result.full_results_json:
                logger.info(f"✓ Successfully saved permanent scan result for user {user.username}")
                logger.info(f"  - Permanent storage ID: {permanent_result.id}")
                logger.info(f"  - Total items saved: {permanent_result.total_items}")
                logger.info(f"  - Total subdomains saved: {permanent_result.total_subdomains}")
            else:
                logger.error(f"✗ Permanent storage created but full_results_json is empty for scan {scan_id}")

        except Exception as e:
            logger.error(f"✗ CRITICAL: Failed to save permanent storage for user {user.username}: {e}", exc_info=True)
            # Don't raise - scan tetap berhasil meskipun permanent storage gagal

        # Update cache with normalized results
        user_scans = cache.get(f'user_scans_{user_id}', {})
        if scan_id in user_scans:
            user_scans[scan_id]['status'] = 'completed'
            user_scans[scan_id]['results'] = normalized_results  # Gunakan normalized results
            user_scans[scan_id]['scan_pk'] = scan_obj.pk  # Pastikan scan_pk ada untuk navigasi
            cache.set(f'user_scans_{user_id}', user_scans, timeout=604800)

        # Update cache progress to completed
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'COMPLETED',
            'phase': 'Done',
            'message': 'Scan Selesai.'
        }, timeout=3600)

        # Log activity
        log_details = f"domain: {domain}, type: {scan_type}, status: completed"
        log_activity_db(user, 'SCAN_COMPLETE', log_details)

        logger.info(f"Scan {scan_id}: Completed successfully")

    except Exception as e:
        logger.error(f"Scan {scan_id}: Error - {e}", exc_info=True)

        # Update scan object with error
        scan_obj.status = 'FAILED'
        scan_obj.end_time = timezone.now()
        scan_obj.error_message = str(e)
        scan_obj.save()

        # Update cache with error
        user_scans = cache.get(f'user_scans_{user_id}', {})
        if scan_id in user_scans:
            user_scans[scan_id]['status'] = 'failed'
            user_scans[scan_id]['error'] = str(e)
            cache.set(f'user_scans_{user_id}', user_scans, timeout=604800)

        # Update cache progress to failed
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'FAILED',
            'phase': 'Error',
            'message': str(e)
        }, timeout=3600)

        # Log activity
        log_details = f"domain: {domain}, error: {str(e)}"
        log_activity_db(user, 'SCAN_FAIL', log_details)

def log_activity_db(user_obj, action, details=""):
    """Log activity to database (thread-safe for Celery)"""
    from .models import ActivityLog
    try:
        ActivityLog.objects.create(
            user=user_obj,
            organization_name=user_obj.organization_name if hasattr(user_obj, 'organization_name') else 'N/A',
            action=action,
            details=details
        )
        logger.info(f"Activity logged: {action} for user {user_obj.username}")
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
