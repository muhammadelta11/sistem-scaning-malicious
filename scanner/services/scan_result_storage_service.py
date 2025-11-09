"""
Service untuk menyimpan hasil scan secara terstruktur ke database.
Menyimpan setiap URL, title, description, label, dan subdomain ke model terpisah.
"""

import logging
from typing import Dict, Any, List
from django.db import transaction
from scanner.models import ScanHistory, ScanResultItem, ScanSubdomain

logger = logging.getLogger(__name__)


class ScanResultStorageService:
    """Service untuk menyimpan hasil scan secara terstruktur ke database."""
    
    @staticmethod
    def save_scan_results(scan_history: ScanHistory, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """
        Simpan semua hasil scan ke database secara terstruktur.
        
        Args:
            scan_history: ScanHistory instance
            scan_results: Hasil scan dalam format dictionary
            
        Returns:
            Dictionary dengan statistik hasil penyimpanan:
            {
                'items_saved': jumlah item yang disimpan,
                'subdomains_saved': jumlah subdomain yang disimpan,
                'items_skipped': jumlah item yang dilewati,
                'subdomains_skipped': jumlah subdomain yang dilewati
            }
        """
        stats = {
            'items_saved': 0,
            'subdomains_saved': 0,
            'items_skipped': 0,
            'subdomains_skipped': 0
        }
        
        try:
            # Normalisasi hasil scan
            from scanner.utils.normalizers import normalize_scan_results
            normalized_results = normalize_scan_results(scan_results)
            
            # Simpan items (URL, title, description, label)
            items_stats = ScanResultStorageService._save_scan_items(scan_history, normalized_results)
            stats['items_saved'] = items_stats['saved']
            stats['items_skipped'] = items_stats['skipped']
            
            # Simpan subdomains
            subdomains_stats = ScanResultStorageService._save_scan_subdomains(scan_history, normalized_results)
            stats['subdomains_saved'] = subdomains_stats['saved']
            stats['subdomains_skipped'] = subdomains_stats['skipped']
            
            logger.info(
                f"Saved scan results for {scan_history.domain} (Scan ID: {scan_history.scan_id}): "
                f"{stats['items_saved']} items, {stats['subdomains_saved']} subdomains"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error saving scan results for {scan_history.scan_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _save_scan_items(scan_history: ScanHistory, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """Simpan semua items (URL, title, description, label) ke database."""
        stats = {'saved': 0, 'skipped': 0}
        
        # Map category codes ke label names
        label_status_map = {
            '0': 'aman',
            '1': 'hack judol',
            '2': 'pornografi',
            '3': 'hacked',
            '4': 'narkoba'
        }
        
        # Kumpulkan items dari categories
        categories = scan_results.get('categories', {})
        items_to_save = []
        
        for cat_code, cat_data in categories.items():
            if not isinstance(cat_data, dict):
                continue
            
            cat_items = cat_data.get('items', [])
            if not cat_items:
                continue
            
            cat_name = cat_data.get('name', '')
            label = label_status_map.get(str(cat_code), cat_name.lower() if cat_name else 'unknown')
            
            # Process setiap item
            for item in cat_items:
                if not isinstance(item, dict):
                    stats['skipped'] += 1
                    continue
                
                # Extract URL
                url = item.get('url') or item.get('link') or ''
                if not url or not url.strip():
                    # Try dari deep_analysis
                    deep_analysis = item.get('deep_analysis', {})
                    if isinstance(deep_analysis, dict):
                        url = deep_analysis.get('url') or ''
                    # Try dari source
                    if not url or not url.strip():
                        source = item.get('source', '')
                        if source and isinstance(source, str) and 'http' in source:
                            url = source
                
                if not url or not url.strip():
                    stats['skipped'] += 1
                    continue
                
                # Extract title
                title = item.get('title') or item.get('headline') or ''
                if not title or not title.strip():
                    snippet = item.get('snippet') or item.get('description') or ''
                    if snippet and isinstance(snippet, str) and snippet.strip():
                        title = snippet[:200].strip()
                if not title:
                    title = 'No Title'
                
                # Extract description
                description = item.get('snippet') or item.get('description') or ''
                
                # Extract verification status
                verification = item.get('verification', {})
                if isinstance(verification, dict):
                    is_live = verification.get('is_live', False)
                    is_cache_only = verification.get('is_cache_only', False)
                    verification_status = item.get('verification_status', 'UNVERIFIED')
                    
                    # Tentukan verification status
                    if is_live and label != 'aman':
                        verification_status = 'LIVE'
                    elif is_cache_only:
                        verification_status = 'CACHE_ONLY'
                    elif verification.get('is_safe', False):
                        verification_status = 'VERIFIED_SAFE'
                else:
                    is_live = item.get('is_live', False)
                    is_cache_only = item.get('is_cache_only', False)
                    verification_status = item.get('verification_status', 'UNVERIFIED')
                
                # Extract keywords found
                keywords_found = item.get('keywords_found', [])
                if not isinstance(keywords_found, list):
                    keywords_found = []
                
                # Extract confidence dan risk score
                confidence_score = item.get('confidence') or item.get('confidence_score')
                risk_score = item.get('risk_score')
                
                # Extract source
                source = item.get('source', '')
                
                # Extract JS analysis
                js_analysis = item.get('js_analysis', {})
                if not isinstance(js_analysis, dict):
                    js_analysis = {}
                
                # Buat ScanResultItem object
                result_item = ScanResultItem(
                    scan_history=scan_history,
                    url=url.strip() if url else '',
                    title=(title.strip()[:1000] if title else 'No Title'),  # Limit title length
                    description=(description.strip()[:5000] if description and description.strip() else None),  # Limit description length
                    label=label,
                    category_code=str(cat_code),
                    category_name=cat_name,
                    verification_status=verification_status,
                    is_live=bool(is_live),
                    is_cache_only=bool(is_cache_only),
                    keywords_found=keywords_found,
                    confidence_score=float(confidence_score) if confidence_score is not None else None,
                    risk_score=int(risk_score) if risk_score is not None else None,
                    source=(source[:100] if source else None),
                    js_analysis=js_analysis
                )
                
                items_to_save.append(result_item)
        
        # Bulk create items dalam transaction
        if items_to_save:
            try:
                with transaction.atomic():
                    # Delete existing items untuk scan ini (jika ada re-scan)
                    ScanResultItem.objects.filter(scan_history=scan_history).delete()
                    # Bulk create items baru
                    ScanResultItem.objects.bulk_create(items_to_save, ignore_conflicts=True)
                    stats['saved'] = len(items_to_save)
                    logger.info(f"Saved {stats['saved']} items for scan {scan_history.scan_id}")
            except Exception as e:
                logger.error(f"Error bulk creating items: {e}", exc_info=True)
                stats['skipped'] += len(items_to_save)
        else:
            logger.warning(f"No items to save for scan {scan_history.scan_id}")
        
        return stats
    
    @staticmethod
    def _save_scan_subdomains(scan_history: ScanHistory, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """Simpan semua subdomains ke database."""
        stats = {'saved': 0, 'skipped': 0}
        
        # Extract subdomains dari subdomain_results
        subdomain_results = scan_results.get('subdomain_results', {})
        if isinstance(subdomain_results, dict):
            subdomains_list = subdomain_results.get('subdomains', [])
        else:
            subdomains_list = []
        
        # Fallback: cek juga key 'subdomains' langsung
        if not subdomains_list:
            subdomains = scan_results.get('subdomains', {})
            if isinstance(subdomains, dict):
                subdomains_list = subdomains.get('subdomains', [])
            elif isinstance(subdomains, list):
                subdomains_list = subdomains
        
        if not subdomains_list:
            logger.info(f"No subdomains found for scan {scan_history.scan_id}")
            return stats
        
        subdomains_to_save = []
        
        for subdomain_data in subdomains_list:
            if not isinstance(subdomain_data, dict):
                stats['skipped'] += 1
                continue
            
            # Extract subdomain name
            subdomain_name = subdomain_data.get('subdomain') or subdomain_data.get('name') or ''
            if not subdomain_name or not subdomain_name.strip():
                stats['skipped'] += 1
                continue
            
            # Extract IP address
            ip_address = subdomain_data.get('ip') or subdomain_data.get('ip_address') or None
            
            # Extract status
            status_str = subdomain_data.get('status', 'UNKNOWN')
            if status_str and isinstance(status_str, str):
                status_str = status_str.upper()
                if status_str not in ['ACTIVE', 'INACTIVE', 'UNKNOWN']:
                    status_str = 'UNKNOWN'
            else:
                # Determine status dari IP address
                if ip_address:
                    status_str = 'ACTIVE'
                else:
                    status_str = 'UNKNOWN'
            
            # Extract discovery method
            discovery_method = subdomain_data.get('discovery_method') or subdomain_data.get('method') or ''
            
            # Buat ScanSubdomain object
            subdomain_obj = ScanSubdomain(
                scan_history=scan_history,
                subdomain=subdomain_name.strip(),
                ip_address=ip_address,
                status=status_str,
                discovery_method=discovery_method[:100] if discovery_method else None
            )
            
            subdomains_to_save.append(subdomain_obj)
        
        # Bulk create subdomains dalam transaction
        if subdomains_to_save:
            try:
                with transaction.atomic():
                    # Delete existing subdomains untuk scan ini (jika ada re-scan)
                    ScanSubdomain.objects.filter(scan_history=scan_history).delete()
                    # Bulk create subdomains baru (gunakan update_or_create untuk unique_together)
                    for subdomain_obj in subdomains_to_save:
                        ScanSubdomain.objects.update_or_create(
                            scan_history=scan_history,
                            subdomain=subdomain_obj.subdomain,
                            defaults={
                                'ip_address': subdomain_obj.ip_address,
                                'status': subdomain_obj.status,
                                'discovery_method': subdomain_obj.discovery_method
                            }
                        )
                    stats['saved'] = len(subdomains_to_save)
                    logger.info(f"Saved {stats['saved']} subdomains for scan {scan_history.scan_id}")
            except Exception as e:
                logger.error(f"Error saving subdomains: {e}", exc_info=True)
                stats['skipped'] += len(subdomains_to_save)
        else:
            logger.warning(f"No subdomains to save for scan {scan_history.scan_id}")
        
        return stats
    
    @staticmethod
    def get_scan_items(scan_history: ScanHistory, label=None, verification_status=None) -> List[ScanResultItem]:
        """
        Ambil items hasil scan dari database dengan filter opsional.
        
        Args:
            scan_history: ScanHistory instance
            label: Filter berdasarkan label (opsional)
            verification_status: Filter berdasarkan verification status (opsional)
            
        Returns:
            List of ScanResultItem objects
        """
        queryset = ScanResultItem.objects.filter(scan_history=scan_history)
        
        if label:
            queryset = queryset.filter(label=label)
        
        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)
        
        return list(queryset)
    
    @staticmethod
    def get_scan_subdomains(scan_history: ScanHistory, status=None) -> List[ScanSubdomain]:
        """
        Ambil subdomains hasil scan dari database dengan filter opsional.
        
        Args:
            scan_history: ScanHistory instance
            status: Filter berdasarkan status (opsional)
            
        Returns:
            List of ScanSubdomain objects
        """
        queryset = ScanSubdomain.objects.filter(scan_history=scan_history)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return list(queryset)
    
    @staticmethod
    def backfill_scan_from_json(scan_history: ScanHistory) -> Dict[str, int]:
        """
        Backfill data dari JSON ke model terstruktur untuk scan lama.
        Berguna untuk scan yang dilakukan sebelum implementasi model terstruktur.
        
        Args:
            scan_history: ScanHistory instance yang akan di-backfill
            
        Returns:
            Dictionary dengan statistik hasil backfill
        """
        if not scan_history.scan_results_json:
            logger.warning(f"No JSON data to backfill for scan {scan_history.scan_id}")
            return {'items_saved': 0, 'subdomains_saved': 0, 'items_skipped': 0, 'subdomains_skipped': 0}
        
        # Check if already has structured data
        if ScanResultItem.objects.filter(scan_history=scan_history).exists():
            logger.info(f"Scan {scan_history.scan_id} already has structured data, skipping backfill")
            return {'items_saved': 0, 'subdomains_saved': 0, 'items_skipped': 0, 'subdomains_skipped': 0}
        
        try:
            import json
            scan_results = json.loads(scan_history.scan_results_json)
            
            # Normalisasi hasil scan
            from scanner.utils.normalizers import normalize_scan_results
            normalized_results = normalize_scan_results(scan_results)
            
            # Simpan menggunakan method yang sama dengan scan baru
            stats = ScanResultStorageService.save_scan_results(scan_history, normalized_results)
            
            logger.info(
                f"Backfilled scan {scan_history.scan_id}: "
                f"{stats['items_saved']} items, {stats['subdomains_saved']} subdomains"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error backfilling scan {scan_history.scan_id}: {e}", exc_info=True)
            return {'items_saved': 0, 'subdomains_saved': 0, 'items_skipped': 0, 'subdomains_skipped': 0}

