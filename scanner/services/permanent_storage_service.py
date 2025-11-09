"""
Service untuk menyimpan hasil scan permanen (Premium Feature).
"""

import logging
import json
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from scanner.models import ScanHistory, PermanentScanResult
from scanner.utils.json_encoder import convert_to_serializable

User = get_user_model()
logger = logging.getLogger(__name__)


class PermanentStorageService:
    """Service untuk mengelola penyimpanan hasil scan permanen."""
    
    @staticmethod
    def save_scan_result(scan_history: ScanHistory, scan_results: Dict[str, Any]) -> PermanentScanResult:
        """
        Simpan hasil scan secara permanen ke database.
        
        Args:
            scan_history: ScanHistory instance
            scan_results: Hasil scan dalam format dictionary
            
        Returns:
            PermanentScanResult instance
        """
        try:
            # Validasi input
            if not scan_results:
                logger.error(f"scan_results is empty or None for scan {scan_history.scan_id}")
                raise ValueError("scan_results cannot be empty or None")
            
            logger.info(f"Starting to save permanent storage for scan {scan_history.scan_id} (domain: {scan_history.domain})")
            logger.debug(f"scan_results type: {type(scan_results)}, keys: {list(scan_results.keys()) if isinstance(scan_results, dict) else 'N/A'}")
            
            # Convert scan_results ke format yang bisa di-serialize (handle numpy types)
            # Penting: JSONField Django tidak bisa handle numpy types langsung
            serializable_results = convert_to_serializable(scan_results)
            
            # Validasi hasil konversi
            if not serializable_results:
                logger.error(f"serializable_results is empty after conversion for scan {scan_history.scan_id}")
                raise ValueError("serializable_results cannot be empty after conversion")
            
            logger.debug(f"Serializable results type: {type(serializable_results)}, keys: {list(serializable_results.keys()) if isinstance(serializable_results, dict) else 'N/A'}")
            
            # Normalisasi data terlebih dahulu untuk memastikan semua field ada
            from scanner.utils.normalizers import normalize_scan_results
            normalized_results = normalize_scan_results(serializable_results)
            
            # Extract metadata dari normalized results
            # Items bisa langsung di root atau di dalam categories
            items = normalized_results.get('items', [])
            categories = normalized_results.get('categories', {})
            
            # Kumpulkan items dari categories dengan format CSV-like
            # SELALU kumpulkan dari categories, bahkan jika ada items di root
            formatted_items = []
            
            # Format label_status dari category code
            label_status_map = {
                '0': 'aman',
                '1': 'hack judol',
                '2': 'pornografi',
                '3': 'hacked',
                '4': 'narkoba'
            }
            
            # Kumpulkan items dari categories dengan format CSV-like
            for cat_code, cat_data in categories.items():
                if not isinstance(cat_data, dict):
                    continue
                    
                cat_items = cat_data.get('items', [])
                if not cat_items:
                    continue
                    
                cat_name = cat_data.get('name', '')
                label_status = label_status_map.get(str(cat_code), cat_name.lower() if cat_name else 'unknown')
                
                # Format setiap item dengan struktur sederhana seperti CSV
                for item in cat_items:
                    if not isinstance(item, dict):
                        continue
                    
                    # Pastikan semua field penting ada dan tidak null
                    # Data sudah dinormalisasi oleh normalize_scan_results, jadi langsung ambil
                    url = item.get('url') or item.get('link') or ''
                    if not url or not url.strip():
                        # Coba dari deep_analysis
                        deep_analysis = item.get('deep_analysis', {})
                        if isinstance(deep_analysis, dict):
                            url = deep_analysis.get('url') or ''
                        # Coba dari source
                        if not url or not url.strip():
                            source = item.get('source', '')
                            if source and isinstance(source, str) and 'http' in source:
                                url = source
                    
                    # Title: cek berbagai sumber (data sudah dinormalisasi)
                    title = item.get('title') or item.get('headline') or ''
                    if not title or not title.strip():
                        # Coba dari snippet sebagai fallback
                        snippet = item.get('snippet') or item.get('description') or ''
                        if snippet and isinstance(snippet, str) and snippet.strip():
                            title = snippet[:100].strip()  # Gunakan 100 karakter pertama snippet
                    if not title or not title.strip():
                        title = 'No Title'
                    
                    # Description: gunakan snippet atau description
                    description = item.get('snippet') or item.get('description') or ''
                    if not description:
                        description = ''
                    
                    # Timestamp: gunakan start_time scan
                    timestamp = scan_history.start_time.isoformat() if scan_history.start_time else ''
                    
                    # Pastikan tidak ada None values dan semua field adalah string
                    formatted_item = {
                        'url': str(url).strip() if url else '',
                        'title': str(title).strip() if title else 'No Title',
                        'description': str(description).strip() if description else '',
                        'timestamp': str(timestamp) if timestamp else '',
                        'label_status': str(label_status).strip() if label_status else 'unknown'
                    }
                    
                    # TAMBAHKAN SEMUA ITEM, bahkan jika URL kosong (untuk tracking)
                    # Tapi prioritaskan yang punya URL
                    formatted_items.append(formatted_item)
            
            # Jika tidak ada items dari categories, coba dari root items
            if not formatted_items and items:
                # Jika ada items di root, format dengan menentukan label_status dari categories
                for item in items:
                    if isinstance(item, dict):
                        # Cari category dari item (bisa dari category_code atau category_name)
                        item_cat_code = item.get('category_code') or item.get('category')
                        item_cat_name = item.get('category_name') or item.get('category')
                        
                        # Tentukan label_status
                        label_status = 'unknown'
                        if item_cat_code:
                            label_status_map = {
                                '0': 'aman',
                                '1': 'hack judol',
                                '2': 'pornografi',
                                '3': 'hacked',
                                '4': 'narkoba'
                            }
                            label_status = label_status_map.get(str(item_cat_code), 'unknown')
                        elif item_cat_name:
                            label_status = str(item_cat_name).lower().strip()
                        
                        # URL: cek berbagai sumber (data sudah dinormalisasi)
                        url = item.get('url') or item.get('link') or ''
                        if not url or not url.strip():
                            # Coba dari deep_analysis
                            deep_analysis = item.get('deep_analysis', {})
                            if isinstance(deep_analysis, dict):
                                url = deep_analysis.get('url') or ''
                            # Coba dari source
                            if not url or not url.strip():
                                source = item.get('source', '')
                                if source and isinstance(source, str) and 'http' in source:
                                    url = source
                        
                        # Title: cek berbagai sumber (data sudah dinormalisasi)
                        title = item.get('title') or item.get('headline') or ''
                        if not title or not title.strip():
                            # Coba dari snippet sebagai fallback
                            snippet = item.get('snippet') or item.get('description') or ''
                            if snippet and isinstance(snippet, str) and snippet.strip():
                                title = snippet[:100].strip()  # Gunakan 100 karakter pertama snippet
                        if not title or not title.strip():
                            title = 'No Title'
                        
                        # Description: gunakan snippet atau description
                        description = item.get('snippet') or item.get('description') or ''
                        if not description:
                            description = ''
                        
                        # Timestamp: gunakan start_time scan
                        timestamp = scan_history.start_time.isoformat() if scan_history.start_time else ''
                        
                        # Pastikan tidak ada None values dan semua field adalah string
                        formatted_item = {
                            'url': str(url).strip() if url else '',
                            'title': str(title).strip() if title else 'No Title',
                            'description': str(description).strip() if description else '',
                            'timestamp': str(timestamp) if timestamp else '',
                            'label_status': str(label_status).strip() if label_status else 'unknown'
                        }
                        
                        # Hanya tambahkan jika URL tidak kosong
                        if formatted_item['url'] and formatted_item['url'].strip():
                            formatted_items.append(formatted_item)
            
            # Subdomains ada di subdomain_results (bukan subdomains langsung)
            # Gunakan normalized_results untuk memastikan data sudah dinormalisasi
            subdomain_results = normalized_results.get('subdomain_results', {})
            if isinstance(subdomain_results, dict):
                subdomains_list = subdomain_results.get('subdomains', [])
            else:
                subdomains_list = []
            
            # Fallback: cek juga key 'subdomains' langsung (untuk backward compatibility)
            if not subdomains_list:
                subdomains = normalized_results.get('subdomains', {})
                if isinstance(subdomains, dict):
                    subdomains_list = subdomains.get('subdomains', [])
                elif isinstance(subdomains, list):
                    subdomains_list = subdomains
            
            # Format subdomains dengan struktur sederhana (pastikan semua field ada dan tidak null)
            formatted_subdomains = []
            for subdomain in subdomains_list:
                if isinstance(subdomain, dict):
                    # Pastikan tidak ada None values
                    subdomain_name = subdomain.get('subdomain') or subdomain.get('name') or ''
                    subdomain_ip = subdomain.get('ip') or ''
                    subdomain_status = subdomain.get('status') or 'unknown'
                    
                    formatted_subdomain = {
                        'subdomain': str(subdomain_name) if subdomain_name else '',
                        'ip': str(subdomain_ip) if subdomain_ip else '',
                        'status': str(subdomain_status) if subdomain_status else 'unknown'
                    }
                    
                    # Hanya tambahkan jika subdomain tidak kosong
                    if formatted_subdomain['subdomain'] and formatted_subdomain['subdomain'].strip():
                        formatted_subdomains.append(formatted_subdomain)
            
            logger.info(f"Extracted metadata - Items: {len(formatted_items)}, Subdomains: {len(formatted_subdomains)}, Categories: {len(categories)}")
            
            # Count items per category (gunakan normalized_results)
            categories_detected = {}
            normalized_categories = normalized_results.get('categories', {})
            for cat_code, cat_data in normalized_categories.items():
                if isinstance(cat_data, dict):
                    cat_items = cat_data.get('items', [])
                    categories_detected[cat_code] = {
                        'name': cat_data.get('name', ''),
                        'count': len(cat_items)
                    }
            
            # Tambahkan formatted_items dan formatted_subdomains ke normalized_results
            # untuk memastikan data tersimpan dalam format yang diinginkan
            normalized_results['formatted_items'] = formatted_items
            normalized_results['formatted_subdomains'] = formatted_subdomains
            
            # Gunakan normalized_results sebagai serializable_results untuk disimpan
            serializable_results = normalized_results
            
            # Validasi data sebelum save
            if not serializable_results:
                logger.error(f"Cannot save empty serializable_results for scan {scan_history.scan_id}")
                raise ValueError("serializable_results is empty, cannot save to database")
            
            # Pastikan serializable_results adalah dict yang valid
            if not isinstance(serializable_results, dict):
                logger.error(f"serializable_results is not a dict: {type(serializable_results)}")
                raise TypeError(f"serializable_results must be a dict, got {type(serializable_results)}")
            
            # Test serialisasi dengan json.dumps untuk memastikan bisa di-serialize
            try:
                test_json = json.dumps(serializable_results)
                logger.debug(f"JSON serialization test passed, size: {len(test_json)} characters")
            except Exception as e:
                logger.error(f"JSON serialization test failed: {e}")
                raise ValueError(f"Cannot serialize scan_results to JSON: {e}")
            
            # Create permanent result dengan serializable results
            try:
                permanent_result, created = PermanentScanResult.objects.get_or_create(
                    scan_history=scan_history,
                    defaults={
                        'full_results_json': serializable_results,  # Gunakan serializable results dengan formatted_items dan formatted_subdomains
                        'total_items': len(formatted_items),  # Gunakan formatted_items count
                        'total_subdomains': len(formatted_subdomains),  # Gunakan formatted_subdomains count
                        'categories_detected': categories_detected,
                    }
                )
                
                if not created:
                    # Update existing result
                    permanent_result.full_results_json = serializable_results  # Gunakan serializable results dengan formatted_items dan formatted_subdomains
                    permanent_result.total_items = len(formatted_items)  # Gunakan formatted_items count
                    permanent_result.total_subdomains = len(formatted_subdomains)  # Gunakan formatted_subdomains count
                    permanent_result.categories_detected = categories_detected
                    # Save dengan semua fields untuk memastikan data tersimpan
                    permanent_result.save()
                    
            except Exception as save_error:
                logger.error(f"Error during database save: {save_error}", exc_info=True)
                raise
            
            # Verify data tersimpan dengan benar - refresh dari database
            permanent_result.refresh_from_db(fields=['full_results_json', 'total_items', 'total_subdomains', 'categories_detected'])
            saved_data = permanent_result.full_results_json
            
            # Validasi bahwa data tersimpan
            if saved_data is None:
                logger.error(f"CRITICAL: full_results_json is None after save for scan {scan_history.scan_id}")
                raise ValueError("full_results_json is None after save - data not saved correctly")
            
            if isinstance(saved_data, dict) and len(saved_data) == 0:
                logger.error(f"CRITICAL: full_results_json is empty dict after save for scan {scan_history.scan_id}")
                raise ValueError("full_results_json is empty dict after save - data not saved correctly")
            
            # Log verification dengan detail
            # Cek formatted_items terlebih dahulu (format CSV-like)
            saved_formatted_items = saved_data.get('formatted_items', []) if isinstance(saved_data, dict) else []
            saved_items = saved_formatted_items if saved_formatted_items else []
            
            # Fallback: jika tidak ada formatted_items, kumpulkan dari categories
            if not saved_items:
                saved_items = saved_data.get('items', []) if isinstance(saved_data, dict) else []
                if not saved_items:
                    saved_categories = saved_data.get('categories', {}) if isinstance(saved_data, dict) else {}
                    for cat_code, cat_data in saved_categories.items():
                        if isinstance(cat_data, dict):
                            cat_items = cat_data.get('items', [])
                            if cat_items:
                                saved_items.extend(cat_items)
            
            # Cek formatted_subdomains terlebih dahulu
            saved_formatted_subdomains = saved_data.get('formatted_subdomains', []) if isinstance(saved_data, dict) else []
            saved_subdomains_list = saved_formatted_subdomains if saved_formatted_subdomains else []
            
            # Fallback: cek subdomain_results
            if not saved_subdomains_list:
                saved_subdomain_results = saved_data.get('subdomain_results', {}) if isinstance(saved_data, dict) else {}
                if isinstance(saved_subdomain_results, dict):
                    saved_subdomains_list = saved_subdomain_results.get('subdomains', [])
                
                # Fallback: cek juga key 'subdomains' langsung
                if not saved_subdomains_list:
                    saved_subdomains = saved_data.get('subdomains', {}) if isinstance(saved_data, dict) else {}
                    if isinstance(saved_subdomains, dict):
                        saved_subdomains_list = saved_subdomains.get('subdomains', [])
                    elif isinstance(saved_subdomains, list):
                        saved_subdomains_list = saved_subdomains
            
            # Verifikasi semua field penting tersimpan
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
            
            missing_fields = []
            for field in expected_fields:
                if field not in saved_data:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"WARNING: Missing fields in saved data: {', '.join(missing_fields)}")
            
            # Log verification dengan detail lengkap
            # Log verification dengan format CSV-like
            saved_formatted_items_count = len(saved_formatted_items) if saved_formatted_items else 0
            saved_formatted_subdomains_count = len(saved_formatted_subdomains) if saved_formatted_subdomains else 0
            
            logger.info(f"✓ Saved permanent scan result for {scan_history.domain} (Scan ID: {scan_history.scan_id})")
            logger.info(f"  - Formatted Items (CSV-like): {len(formatted_items)} → Saved: {saved_formatted_items_count}")
            logger.info(f"  - Formatted Subdomains: {len(formatted_subdomains)} → Saved: {saved_formatted_subdomains_count}")
            logger.info(f"  - Total Items (raw): {len(saved_items)}")
            logger.info(f"  - Total Subdomains (DB): {permanent_result.total_subdomains}")
            logger.info(f"  - Categories: {len(categories_detected)}")
            logger.info(f"  - Total Pages: {saved_data.get('total_pages', 0)}")
            logger.info(f"  - Verified Scan: {saved_data.get('verified_scan', False)}")
            logger.info(f"  - Has Graph Analysis: {bool(saved_data.get('graph_analysis'))}")
            logger.info(f"  - Has Subdomain Results: {bool(saved_data.get('subdomain_results'))}")
            logger.info(f"  - Has Final Conclusion: {bool(saved_data.get('final_conclusion'))}")
            logger.info(f"  - Has Unindexed Pages: {bool(saved_data.get('unindexed_pages'))}")
            logger.info(f"  - Full results JSON size: {len(str(saved_data))} characters")
            logger.info(f"  - Permanent storage ID: {permanent_result.id}")
            
            # Log sample formatted_items untuk verifikasi
            if formatted_items:
                logger.info(f"  - Sample formatted item (first): {formatted_items[0]}")
            if formatted_subdomains:
                logger.info(f"  - Sample formatted subdomain (first): {formatted_subdomains[0]}")
            
            # Final validation
            if len(saved_items) == 0 and len(items) > 0:
                logger.warning(f"WARNING: Items count mismatch - Expected: {len(items)}, Saved: {len(saved_items)}")
            
            if missing_fields:
                logger.warning(f"WARNING: Some expected fields are missing, but core data is saved")
            
            return permanent_result
            
        except Exception as e:
            logger.error(f"Error saving permanent scan result for scan {scan_history.scan_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_scan_result(scan_history: ScanHistory) -> Optional[Dict[str, Any]]:
        """
        Ambil hasil scan permanen dari database.
        
        Args:
            scan_history: ScanHistory instance
            
        Returns:
            Dictionary hasil scan atau None jika tidak ada
        """
        try:
            permanent_result = PermanentScanResult.objects.filter(scan_history=scan_history).first()
            
            if permanent_result:
                return permanent_result.full_results_json
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving permanent scan result: {e}", exc_info=True)
            return None
    
    @staticmethod
    def has_permanent_storage(scan_history: ScanHistory) -> bool:
        """
        Cek apakah scan memiliki penyimpanan permanen.
        
        Args:
            scan_history: ScanHistory instance
            
        Returns:
            True jika ada, False jika tidak
        """
        return PermanentScanResult.objects.filter(scan_history=scan_history).exists()
    
    @staticmethod
    def delete_scan_result(scan_history: ScanHistory) -> bool:
        """
        Hapus hasil scan permanen.
        
        Args:
            scan_history: ScanHistory instance
            
        Returns:
            True jika berhasil dihapus
        """
        try:
            deleted = PermanentScanResult.objects.filter(scan_history=scan_history).delete()
            logger.info(f"Deleted permanent scan result for {scan_history.domain}")
            return deleted[0] > 0
        except Exception as e:
            logger.error(f"Error deleting permanent scan result: {e}", exc_info=True)
            return False

