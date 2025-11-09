"""
Management command untuk memperbaiki permanent storage yang hilang.
Command ini akan:
1. Cari scan history yang completed untuk premium user
2. Cek apakah permanent storage sudah ada
3. Jika belum ada, buat permanent storage dari scan_results_json
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scanner.models import ScanHistory, PermanentScanResult
from scanner.services import PermanentStorageService
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix permanent storage untuk premium user yang scan history sudah completed tapi permanent storage belum ada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username spesifik untuk fix (opsional, jika tidak disediakan akan fix semua premium user)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Hanya tampilkan apa yang akan dilakukan tanpa menyimpan',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - Tidak ada perubahan yang akan disimpan'))
        
        # Get premium users
        if username:
            users = User.objects.filter(username=username, is_premium=True)
        else:
            users = User.objects.filter(is_premium=True)
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('Tidak ada premium user ditemukan'))
            return
        
        self.stdout.write(f'Found {users.count()} premium user(s)')
        
        total_fixed = 0
        total_skipped = 0
        total_errors = 0
        
        for user in users:
            self.stdout.write(f'\nProcessing user: {user.username}')
            
            # Get completed scans untuk user ini
            completed_scans = ScanHistory.objects.filter(
                user=user,
                status='COMPLETED'
            ).order_by('-start_time')
            
            self.stdout.write(f'  Found {completed_scans.count()} completed scan(s)')
            
            for scan in completed_scans:
                # Cek apakah permanent storage sudah ada
                if PermanentScanResult.objects.filter(scan_history=scan).exists():
                    self.stdout.write(f'    ✓ Scan {scan.scan_id} ({scan.domain}) sudah ada permanent storage')
                    total_skipped += 1
                    continue
                
                # Cek apakah scan_results_json ada
                if not scan.scan_results_json:
                    self.stdout.write(self.style.WARNING(f'    ⚠ Scan {scan.scan_id} ({scan.domain}) tidak memiliki scan_results_json'))
                    total_skipped += 1
                    continue
                
                # Parse scan_results_json
                try:
                    results = json.loads(scan.scan_results_json)
                    
                    # Validasi hasil parse
                    if not results or not isinstance(results, dict):
                        self.stdout.write(self.style.WARNING(f'    ⚠ Scan {scan.scan_id} ({scan.domain}) - scan_results_json tidak valid atau kosong'))
                        total_skipped += 1
                        continue
                    
                    # Normalisasi hasil scan (sama seperti di job_runner)
                    from scanner.utils.normalizers import normalize_scan_results
                    normalized_results = normalize_scan_results(results)
                    
                    # Validasi hasil normalisasi
                    if not normalized_results or not isinstance(normalized_results, dict):
                        self.stdout.write(self.style.WARNING(f'    ⚠ Scan {scan.scan_id} ({scan.domain}) - hasil normalisasi tidak valid'))
                        total_skipped += 1
                        continue
                    
                    if dry_run:
                        # Hitung items dan subdomains untuk preview
                        items = normalized_results.get('items', [])
                        if not items:
                            categories = normalized_results.get('categories', {})
                            for cat_code, cat_data in categories.items():
                                if isinstance(cat_data, dict):
                                    items.extend(cat_data.get('items', []))
                        
                        subdomain_results = normalized_results.get('subdomain_results', {})
                        subdomains_count = 0
                        if isinstance(subdomain_results, dict):
                            subdomains_count = len(subdomain_results.get('subdomains', []))
                        
                        self.stdout.write(self.style.WARNING(f'    [DRY RUN] Akan membuat permanent storage untuk scan {scan.scan_id} ({scan.domain})'))
                        self.stdout.write(f'      - Items: {len(items)}, Subdomains: {subdomains_count}')
                        total_fixed += 1
                    else:
                        # Create permanent storage
                        permanent_result = PermanentStorageService.save_scan_result(scan, normalized_results)
                        
                        # Verify saved data
                        permanent_result.refresh_from_db()
                        saved_data = permanent_result.full_results_json
                        if saved_data and isinstance(saved_data, dict) and len(saved_data) > 0:
                            self.stdout.write(self.style.SUCCESS(f'    ✓ Created permanent storage untuk scan {scan.scan_id} ({scan.domain})'))
                            self.stdout.write(f'      - Items: {permanent_result.total_items}, Subdomains: {permanent_result.total_subdomains}')
                            total_fixed += 1
                        else:
                            self.stdout.write(self.style.ERROR(f'    ✗ Permanent storage created tapi full_results_json kosong untuk scan {scan.scan_id}'))
                            total_errors += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Error creating permanent storage untuk scan {scan.scan_id}: {e}'))
                    total_errors += 1
                    logger.error(f"Error fixing permanent storage for scan {scan.scan_id}: {e}", exc_info=True)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  Fixed: {total_fixed}')
        self.stdout.write(f'  Skipped: {total_skipped}')
        self.stdout.write(f'  Errors: {total_errors}')
        self.stdout.write('='*60)

