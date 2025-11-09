"""
Management command untuk verifikasi permanent storage.
Command ini akan memverifikasi bahwa semua data hasil scan tersimpan dengan benar di permanent storage.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scanner.models import ScanHistory, PermanentScanResult
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifikasi permanent storage untuk premium user - pastikan semua data tersimpan dengan benar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username spesifik untuk verifikasi (opsional, jika tidak disediakan akan verifikasi semua premium user)',
        )
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Tampilkan detail lengkap untuk setiap scan',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        detail = options.get('detail', False)
        
        # Get premium users
        if username:
            users = User.objects.filter(username=username, is_premium=True)
        else:
            users = User.objects.filter(is_premium=True)
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('Tidak ada premium user ditemukan'))
            return
        
        self.stdout.write(f'Found {users.count()} premium user(s)')
        self.stdout.write('='*80)
        
        # Expected fields in scan results
        expected_fields = [
            'categories',
            'domain_info',
            'backlinks',
            'total_pages',
            'verified_scan',
            'graph_analysis',
            'subdomain_results',
            'unindexed_pages',
            'final_conclusion',
            'timed_out'
        ]
        
        total_scans = 0
        total_valid = 0
        total_invalid = 0
        total_missing = 0
        
        for user in users:
            self.stdout.write(f'\nProcessing user: {user.username}')
            
            # Get completed scans dengan permanent storage
            completed_scans = ScanHistory.objects.filter(
                user=user,
                status='COMPLETED'
            ).order_by('-start_time')
            
            permanent_results = PermanentScanResult.objects.filter(
                scan_history__user=user
            ).select_related('scan_history')
            
            self.stdout.write(f'  Found {completed_scans.count()} completed scan(s)')
            self.stdout.write(f'  Found {permanent_results.count()} permanent storage record(s)')
            
            for perm_result in permanent_results:
                scan = perm_result.scan_history
                total_scans += 1
                
                # Verifikasi data
                saved_data = perm_result.full_results_json
                
                if not saved_data:
                    self.stdout.write(self.style.ERROR(f'    ✗ Scan {scan.scan_id} ({scan.domain}) - full_results_json is None or empty'))
                    total_invalid += 1
                    continue
                
                if not isinstance(saved_data, dict):
                    self.stdout.write(self.style.ERROR(f'    ✗ Scan {scan.scan_id} ({scan.domain}) - full_results_json is not a dict'))
                    total_invalid += 1
                    continue
                
                # Cek expected fields
                missing_fields = []
                for field in expected_fields:
                    if field not in saved_data:
                        missing_fields.append(field)
                
                # Verifikasi metadata
                items_count = 0
                if 'categories' in saved_data:
                    categories = saved_data['categories']
                    for cat_code, cat_data in categories.items():
                        if isinstance(cat_data, dict):
                            items_count += len(cat_data.get('items', []))
                
                subdomains_count = 0
                if 'subdomain_results' in saved_data:
                    subdomain_results = saved_data['subdomain_results']
                    if isinstance(subdomain_results, dict):
                        subdomains_count = len(subdomain_results.get('subdomains', []))
                
                # Validasi
                is_valid = True
                issues = []
                
                if missing_fields:
                    is_valid = False
                    issues.append(f"Missing fields: {', '.join(missing_fields)}")
                
                if perm_result.total_items != items_count:
                    is_valid = False
                    issues.append(f"Items count mismatch: DB={perm_result.total_items}, Actual={items_count}")
                
                if perm_result.total_subdomains != subdomains_count:
                    is_valid = False
                    issues.append(f"Subdomains count mismatch: DB={perm_result.total_subdomains}, Actual={subdomains_count}")
                
                if not saved_data.get('categories'):
                    is_valid = False
                    issues.append("Categories is empty")
                
                if not saved_data.get('domain_info'):
                    is_valid = False
                    issues.append("domain_info is empty")
                
                if detail:
                    self.stdout.write(f'\n    Scan {scan.scan_id} ({scan.domain}):')
                    self.stdout.write(f'      - Total Items: {items_count} (DB: {perm_result.total_items})')
                    self.stdout.write(f'      - Total Subdomains: {subdomains_count} (DB: {perm_result.total_subdomains})')
                    self.stdout.write(f'      - Categories: {len(saved_data.get("categories", {}))}')
                    self.stdout.write(f'      - Total Pages: {saved_data.get("total_pages", 0)}')
                    self.stdout.write(f'      - Verified Scan: {saved_data.get("verified_scan", False)}')
                    self.stdout.write(f'      - Has Graph Analysis: {bool(saved_data.get("graph_analysis"))}')
                    self.stdout.write(f'      - Has Subdomain Results: {bool(saved_data.get("subdomain_results"))}')
                    self.stdout.write(f'      - Has Final Conclusion: {bool(saved_data.get("final_conclusion"))}')
                    self.stdout.write(f'      - Has Unindexed Pages: {bool(saved_data.get("unindexed_pages"))}')
                    self.stdout.write(f'      - JSON Size: {len(str(saved_data))} characters')
                
                if is_valid:
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Scan {scan.scan_id} ({scan.domain}) - VALID'))
                    total_valid += 1
                else:
                    self.stdout.write(self.style.ERROR(f'    ✗ Scan {scan.scan_id} ({scan.domain}) - INVALID'))
                    for issue in issues:
                        self.stdout.write(self.style.WARNING(f'      ⚠ {issue}'))
                    total_invalid += 1
                
                # Cek scan yang tidak memiliki permanent storage
                scans_without_storage = []
                for scan in completed_scans:
                    if not PermanentScanResult.objects.filter(scan_history=scan).exists():
                        scans_without_storage.append(scan)
                
                if scans_without_storage:
                    total_missing += len(scans_without_storage)
                    self.stdout.write(self.style.WARNING(f'\n  ⚠ {len(scans_without_storage)} scan(s) without permanent storage:'))
                    for scan in scans_without_storage[:5]:  # Tampilkan maksimal 5
                        self.stdout.write(f'    - {scan.scan_id} ({scan.domain}) - {scan.start_time}')
                    if len(scans_without_storage) > 5:
                        self.stdout.write(f'    ... and {len(scans_without_storage) - 5} more')
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Total Scans Checked: {total_scans}')
        self.stdout.write(self.style.SUCCESS(f'  Valid: {total_valid}'))
        self.stdout.write(self.style.ERROR(f'  Invalid: {total_invalid}'))
        self.stdout.write(self.style.WARNING(f'  Missing Permanent Storage: {total_missing}'))
        self.stdout.write('='*80)

