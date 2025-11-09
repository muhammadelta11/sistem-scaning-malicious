from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import ScanHistory
from . import core_scanner
from . import data_manager
from .utils.json_encoder import json_dumps_safe
import logging

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)


def _run_scan(scan_pk, scan_id, domain, primary_key, fallback_key, scan_type, enable_verification, user_id, show_all_results=False):
    User = get_user_model()
    scan_obj = ScanHistory.objects.get(pk=scan_pk)
    user = User.objects.get(pk=user_id)

    try:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Starting',
            'message': f"Menyiapkan scan untuk {domain}..."
        }, timeout=3600)

        model, label_mapping, _ = data_manager.load_resources()
        if not label_mapping:
            label_mapping = {1: 'hack judol', 2: 'pornografi', 3: 'hacked', 0: 'aman'}

        results = core_scanner.perform_native_scan(
            domain, primary_key, fallback_key, scan_type, enable_backlink=False,
            model=model, label_mapping=label_mapping, enable_verification=enable_verification, scan_id=scan_id
        )

        # Normalisasi hasil scan sebelum disimpan (memastikan struktur lengkap)
        from scanner.utils.normalizers import normalize_scan_results
        normalized_results = normalize_scan_results(results)
        
        scan_obj.status = 'COMPLETED'
        scan_obj.end_time = timezone.now()
        # Use safe JSON encoder untuk handle numpy types
        scan_obj.scan_results_json = json_dumps_safe(normalized_results)
        scan_obj.save()

        # Auto-update dashboard jika scan completed
        try:
            from .services import DashboardService
            DashboardService.update_dashboard_from_scan_results(domain, results)
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
        
        # Save permanent storage untuk premium user (untuk backward compatibility)
        if user.is_premium:
            try:
                from .services import PermanentStorageService
                logger.info(f"Attempting to save permanent storage for premium user {user.username} (scan_id: {scan_id})")
                permanent_result = PermanentStorageService.save_scan_result(scan_obj, normalized_results)
                
                # Verify saved data
                if permanent_result and permanent_result.full_results_json:
                    logger.info(f"✓ Successfully saved permanent scan result for premium user {user.username}")
                    logger.info(f"  - Permanent storage ID: {permanent_result.id}")
                    logger.info(f"  - Total items saved: {permanent_result.total_items}")
                    logger.info(f"  - Total subdomains saved: {permanent_result.total_subdomains}")
                else:
                    logger.error(f"✗ Permanent storage created but full_results_json is empty for scan {scan_id}")
                    
            except Exception as e:
                logger.error(f"✗ CRITICAL: Failed to save permanent storage for premium user {user.username}: {e}", exc_info=True)
                # Don't raise - scan tetap berhasil meskipun permanent storage gagal
                # Tapi log error dengan jelas agar bisa di-debug

        user_scans = cache.get(f'user_scans_{user_id}', {})
        if scan_id in user_scans:
            user_scans[scan_id]['status'] = 'completed'
            user_scans[scan_id]['results'] = normalized_results  # Gunakan normalized results
            user_scans[scan_id]['scan_pk'] = scan_obj.pk  # Pastikan scan_pk ada untuk navigasi
            cache.set(f'user_scans_{user_id}', user_scans, timeout=604800)

        cache.set(f'scan_progress_{scan_id}', {
            'status': 'COMPLETED',
            'phase': 'Done',
            'message': 'Scan Selesai.'
        }, timeout=3600)

        logger.info(f"Scan {scan_id}: Completed successfully (thread)")
    except Exception as e:
        logger.error(f"Scan {scan_id}: Error - {e}", exc_info=True)
        scan_obj.status = 'FAILED'
        scan_obj.end_time = timezone.now()
        scan_obj.error_message = str(e)
        scan_obj.save()

        user_scans = cache.get(f'user_scans_{user_id}', {})
        if scan_id in user_scans:
            user_scans[scan_id]['status'] = 'failed'
            user_scans[scan_id]['error'] = str(e)
            cache.set(f'user_scans_{user_id}', user_scans, timeout=604800)

        cache.set(f'scan_progress_{scan_id}', {
            'status': 'FAILED',
            'phase': 'Error',
            'message': str(e)
        }, timeout=3600)


def submit_scan_thread(scan_pk, scan_id, domain, primary_key, fallback_key, scan_type, enable_verification, user_id, show_all_results=False):
    executor.submit(
        _run_scan,
        scan_pk, scan_id, domain, primary_key, fallback_key, scan_type, enable_verification, user_id, show_all_results
    )
    return True


