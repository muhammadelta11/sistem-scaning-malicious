"""
Management command untuk export scan results ke CSV format.
Mengambil data dari permanent storage dan format seperti CSV.
"""

from django.core.management.base import BaseCommand
from scanner.models import ScanHistory, PermanentScanResult
import csv
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export scan results ke CSV format (seperti labeling_judol_dan_aman-26.csv)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scan-id',
            type=str,
            help='Scan ID untuk export (opsional, jika tidak disediakan akan list semua scan)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='scan_results_export.csv',
            help='Output file path (default: scan_results_export.csv)',
        )

    def handle(self, *args, **options):
        scan_id = options.get('scan_id')
        output_file = options.get('output')
        
        if scan_id:
            # Export scan tertentu
            try:
                scan = ScanHistory.objects.get(scan_id=scan_id)
                self.export_scan(scan, output_file)
            except ScanHistory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Scan dengan ID {scan_id} tidak ditemukan'))
        else:
            # List semua scan
            scans = ScanHistory.objects.filter(status='COMPLETED').order_by('-start_time')[:10]
            self.stdout.write(f'Found {scans.count()} completed scans')
            for scan in scans:
                self.stdout.write(f'  - {scan.scan_id} ({scan.domain}) - {scan.start_time}')
            self.stdout.write(self.style.WARNING('\nGunakan --scan-id untuk export scan tertentu'))
    
    def export_scan(self, scan, output_file):
        """Export scan results ke CSV format."""
        try:
            # Cek permanent storage
            permanent_result = PermanentScanResult.objects.filter(scan_history=scan).first()
            
            if not permanent_result:
                self.stdout.write(self.style.WARNING(f'Scan {scan.scan_id} tidak memiliki permanent storage'))
                return
            
            saved_data = permanent_result.full_results_json
            
            if not saved_data:
                self.stdout.write(self.style.WARNING(f'Scan {scan.scan_id} tidak memiliki data di permanent storage'))
                return
            
            # Ambil formatted_items (format CSV-like)
            formatted_items = saved_data.get('formatted_items', [])
            
            # Jika tidak ada formatted_items, format dari categories
            if not formatted_items:
                categories = saved_data.get('categories', {})
                formatted_items = []
                
                for cat_code, cat_data in categories.items():
                    if isinstance(cat_data, dict):
                        cat_items = cat_data.get('items', [])
                        cat_name = cat_data.get('name', '')
                        
                        # Format label_status
                        label_status_map = {
                            '0': 'aman',
                            '1': 'hack judol',
                            '2': 'pornografi',
                            '3': 'hacked',
                            '4': 'narkoba'
                        }
                        label_status = label_status_map.get(str(cat_code), cat_name.lower() if cat_name else 'unknown')
                        
                        for item in cat_items:
                            if isinstance(item, dict):
                                formatted_item = {
                                    'url': item.get('url') or item.get('link') or '',
                                    'title': item.get('title') or item.get('headline') or 'No Title',
                                    'description': item.get('snippet') or item.get('description') or '',
                                    'timestamp': scan.start_time.isoformat() if scan.start_time else '',
                                    'label_status': label_status
                                }
                                if formatted_item['url']:
                                    formatted_items.append(formatted_item)
            
            # Ambil formatted_subdomains
            formatted_subdomains = saved_data.get('formatted_subdomains', [])
            
            # Jika tidak ada formatted_subdomains, format dari subdomain_results
            if not formatted_subdomains:
                subdomain_results = saved_data.get('subdomain_results', {})
                if isinstance(subdomain_results, dict):
                    subdomains_list = subdomain_results.get('subdomains', [])
                    for subdomain in subdomains_list:
                        if isinstance(subdomain, dict):
                            formatted_subdomain = {
                                'subdomain': subdomain.get('subdomain') or subdomain.get('name') or '',
                                'ip': subdomain.get('ip') or '',
                                'status': subdomain.get('status') or 'unknown'
                            }
                            if formatted_subdomain['subdomain']:
                                formatted_subdomains.append(formatted_subdomain)
            
            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['url', 'title', 'description', 'timestamp', 'label_status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for item in formatted_items:
                    writer.writerow(item)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Exported {len(formatted_items)} items ke {output_file}'))
            
            # Export subdomains ke file terpisah
            if formatted_subdomains:
                subdomain_file = output_file.replace('.csv', '_subdomains.csv')
                with open(subdomain_file, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['subdomain', 'ip', 'status']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for subdomain in formatted_subdomains:
                        writer.writerow(subdomain)
                
                self.stdout.write(self.style.SUCCESS(f'✓ Exported {len(formatted_subdomains)} subdomains ke {subdomain_file}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting scan: {e}'))
            logger.error(f"Error exporting scan {scan.scan_id}: {e}", exc_info=True)

