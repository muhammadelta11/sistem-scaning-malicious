"""
Service untuk mengelola dashboard dan summary hasil scan.
"""

import logging
import os
import pandas as pd
from typing import Dict, Any, Optional
from django.utils import timezone
from django.conf import settings
from scanner.models import DomainScanSummary
from scanner.exceptions import DomainValidationError

logger = logging.getLogger(__name__)


class DashboardService:
    """Service untuk mengelola dashboard dan summary hasil scan."""
    
    @staticmethod
    def update_dashboard_from_scan_results(domain: str, scan_results: Dict[str, Any]) -> DomainScanSummary:
        """
        Update dashboard summary berdasarkan hasil scan.
        
        Args:
            domain: Domain yang di-scan
            scan_results: Hasil scan dalam format dictionary
            
        Returns:
            DomainScanSummary instance
        """
        # Extract category counts from scan results
        categories = scan_results.get('categories', {})
        
        # Count items per category
        hack_judol_count = 0
        pornografi_count = 0
        hacked_count = 0
        
        # Map category codes to names
        for cat_code, cat_data in categories.items():
            cat_name = cat_data.get('name', '').lower()
            item_count = len(cat_data.get('items', []))
            
            if 'hack' in cat_name or 'judol' in cat_name or 'judi' in cat_name:
                hack_judol_count += item_count
            elif 'pornografi' in cat_name or 'porn' in cat_name or 'bokep' in cat_name:
                pornografi_count += item_count
            elif 'hacked' in cat_name or 'deface' in cat_name:
                hacked_count += item_count
        
        total_cases = hack_judol_count + pornografi_count + hacked_count
        
        # Get or create DomainScanSummary
        summary, created = DomainScanSummary.objects.get_or_create(
            domain=domain,
            defaults={
                'total_cases': total_cases,
                'hack_judol': hack_judol_count,
                'pornografi': pornografi_count,
                'hacked': hacked_count,
            }
        )
        
        if not created:
            # Update existing summary
            summary.total_cases = total_cases
            summary.hack_judol = hack_judol_count
            summary.pornografi = pornografi_count
            summary.hacked = hacked_count
            summary.last_scan = timezone.now()
            summary.save()
        
        logger.info(f"Dashboard updated for domain {domain}: {total_cases} cases (hack_judol: {hack_judol_count}, pornografi: {pornografi_count}, hacked: {hacked_count})")
        
        # Auto-export to CSV after DB update
        try:
            DashboardService.export_dashboard_to_csv()
        except Exception as e:
            logger.warning(f"Failed to export dashboard to CSV: {e}")
        
        return summary
    
    @staticmethod
    def get_dashboard_summary(domain: str) -> Optional[DomainScanSummary]:
        """
        Mendapatkan dashboard summary untuk domain tertentu.
        
        Args:
            domain: Domain target
            
        Returns:
            DomainScanSummary instance atau None
        """
        try:
            return DomainScanSummary.objects.get(domain=domain)
        except DomainScanSummary.DoesNotExist:
            return None
    
    @staticmethod
    def format_domain_info(domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format domain info untuk ditampilkan di UI dengan lebih user-friendly.
        
        Args:
            domain_info: Domain info dari whois/scan
            
        Returns:
            Formatted domain info
        """
        formatted = {
            'registrar': domain_info.get('registrar', 'Unknown'),
            'creation_date': domain_info.get('creation_date', 'Unknown'),
            'expiration_date': domain_info.get('expiration_date', 'Unknown'),
            'status': domain_info.get('status', 'Unknown'),
            'name_servers': domain_info.get('name_servers', []),
            'emails': domain_info.get('emails', []),
            'age_days': domain_info.get('age_days'),
            'red_flag': domain_info.get('red_flag'),
        }
        
        # Format blacklist check
        blacklist_check = domain_info.get('blacklist_check', {})
        formatted['blacklist_check'] = {}
        
        for source, result in blacklist_check.items():
            if isinstance(result, dict):
                if 'error' in result:
                    formatted['blacklist_check'][source] = {
                        'status': 'error',
                        'message': result.get('error', 'Unknown error')
                    }
                elif 'is_blacklisted' in result:
                    formatted['blacklist_check'][source] = {
                        'status': 'blacklisted' if result['is_blacklisted'] else 'clean',
                        'abuse_score': result.get('abuse_score', 0),
                        'total_reports': result.get('total_reports', 0),
                        'last_reported': result.get('last_reported', 'N/A'),
                        'country': result.get('country', 'N/A'),
                    }
                else:
                    formatted['blacklist_check'][source] = {
                        'status': 'unknown',
                        'data': result
                    }
            else:
                formatted['blacklist_check'][source] = {
                    'status': 'unknown',
                    'data': result
                }
        
        return formatted
    
    @staticmethod
    def export_dashboard_to_csv():
        """
        Export dashboard data dari database ke CSV file.
        Menyinkronkan CSV dengan data terbaru dari database.
        """
        try:
            # Convert Path to string for os.path.join
            base_dir = str(settings.BASE_DIR) if hasattr(settings.BASE_DIR, '__str__') else settings.BASE_DIR
            csv_path = os.path.join(base_dir, 'dashboard_ranking.csv')
            
            # Get all summaries from database
            summaries = DomainScanSummary.objects.all()
            
            if summaries.count() == 0:
                logger.info("No domain summaries to export to CSV")
                return
            
            # Prepare data for CSV
            data = []
            for summary in summaries:
                data.append({
                    'domain': summary.domain,
                    'jumlah_kasus': summary.total_cases,
                    'hack judol': summary.hack_judol,
                    'hacked': summary.hacked,
                    'pornografi': summary.pornografi,
                    'hack_judol': summary.hack_judol,  # Extra column for compatibility
                    'last_scan': summary.last_scan.strftime('%Y-%m-%d %H:%M:%S') if summary.last_scan else ''
                })
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(data)
            df = df.sort_values('jumlah_kasus', ascending=False)  # Sort by cases descending
            
            # Save to CSV
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Dashboard data exported to CSV: {len(data)} domains written to {csv_path}")
            
        except Exception as e:
            logger.error(f"Error exporting dashboard to CSV: {e}", exc_info=True)
            raise
    
    @staticmethod
    def import_csv_to_database(csv_path=None):
        """
        Import CSV data ke database DomainScanSummary.
        Berguna untuk mengimpor data historis ke database.
        
        Args:
            csv_path: Path ke file CSV (default: scanner/dashboard_ranking.csv)
            
        Returns:
            dict dengan summary hasil import
        """
        try:
            # Determine CSV path
            if csv_path is None:
                # Default: scanner/dashboard_ranking.csv
                scanner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                csv_path = os.path.join(scanner_dir, 'dashboard_ranking.csv')
            
            logger.info(f"Importing CSV data from: {csv_path}")
            
            # Check if file exists
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return {
                    'success': False,
                    'message': f"CSV file not found: {csv_path}",
                    'imported': 0,
                    'skipped': 0,
                    'updated': 0
                }
            
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Read {len(df)} rows from CSV")
            
            # Statistics
            imported_count = 0
            skipped_count = 0
            updated_count = 0
            
            # Import each row
            for index, row in df.iterrows():
                try:
                    domain = str(row['domain']).strip()
                    
                    # Skip empty domains
                    if not domain or domain == 'nan':
                        skipped_count += 1
                        continue
                    
                    # Convert values with safe defaults
                    def safe_int(value):
                        if pd.isna(value) or value == '':
                            return 0
                        try:
                            return int(float(value))
                        except (ValueError, TypeError):
                            return 0
                    
                    hack_judol_val = row.get('hack judol', row.get('hack_judol', 0))
                    total_cases = safe_int(row.get('jumlah_kasus', 0))
                    hack_judol = safe_int(hack_judol_val)
                    pornografi = safe_int(row.get('pornografi', 0))
                    hacked = safe_int(row.get('hacked', 0))
                    
                    # Parse last_scan if available
                    last_scan_str = row.get('last_scan', '')
                    last_scan = None
                    if last_scan_str and str(last_scan_str) != 'nan':
                        try:
                            last_scan = pd.to_datetime(last_scan_str)
                            from django.utils import timezone
                            if timezone.is_naive(last_scan):
                                last_scan = timezone.make_aware(last_scan)
                        except Exception:
                            pass
                    
                    # Get or create DomainScanSummary
                    summary, created = DomainScanSummary.objects.get_or_create(
                        domain=domain,
                        defaults={
                            'total_cases': total_cases,
                            'hack_judol': hack_judol,
                            'pornografi': pornografi,
                            'hacked': hacked,
                        }
                    )
                    
                    if created:
                        imported_count += 1
                        logger.info(f"Imported new domain: {domain} ({total_cases} cases)")
                        
                        # Set last_scan if available
                        if last_scan:
                            summary.last_scan = last_scan
                            summary.save(update_fields=['last_scan'])
                    else:
                        # Update existing summary if CSV has more cases
                        updated_count += 1
                        summary.total_cases = total_cases
                        summary.hack_judol = hack_judol
                        summary.pornografi = pornografi
                        summary.hacked = hacked
                        if last_scan:
                            summary.last_scan = last_scan
                        summary.save()
                        logger.debug(f"Updated domain: {domain} ({total_cases} cases)")
                        
                except Exception as e:
                    logger.error(f"Error importing row {index}: {e}", exc_info=True)
                    skipped_count += 1
                    continue
            
            # Export updated data back to CSV
            try:
                DashboardService.export_dashboard_to_csv()
                logger.info("Re-exported dashboard to CSV after import")
            except Exception as e:
                logger.warning(f"Failed to re-export CSV: {e}")
            
            result = {
                'success': True,
                'message': f"Successfully imported {imported_count} domains, updated {updated_count} domains",
                'imported': imported_count,
                'skipped': skipped_count,
                'updated': updated_count,
                'total_rows': len(df)
            }
            
            logger.info(f"CSV import completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error importing CSV to database: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"Error importing CSV: {str(e)}",
                'imported': 0,
                'skipped': 0,
                'updated': 0
            }

