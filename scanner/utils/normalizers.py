"""
Utility untuk normalisasi dan validasi data scan results.
Memastikan data dari database memiliki struktur yang lengkap dan konsisten.
"""

import logging

logger = logging.getLogger(__name__)


def normalize_scan_results(results):
    """
    Normalisasi dan validasi scan results dari database.
    Menambahkan default values untuk field yang missing atau None.
    
    Args:
        results: Dictionary hasil scan (dari scan_results_json)
        
    Returns:
        Dictionary hasil scan yang sudah dinormalisasi
    """
    if not results or not isinstance(results, dict):
        return _get_empty_results()
    
    # Normalisasi final_conclusion
    if 'final_conclusion' not in results or not results['final_conclusion']:
        results['final_conclusion'] = _get_default_final_conclusion()
    else:
        results['final_conclusion'] = _normalize_final_conclusion(results['final_conclusion'])
    
    # Normalisasi categories
    if 'categories' not in results:
        results['categories'] = {}
    
    # Normalisasi domain_info
    if 'domain_info' not in results:
        results['domain_info'] = {}
    
    # Normalisasi subdomain_results
    if 'subdomain_results' not in results:
        results['subdomain_results'] = {
            'total_subdomains': 0,
            'subdomains': [],
            'techniques_used': []
        }
    else:
        results['subdomain_results'] = _normalize_subdomain_results(results['subdomain_results'])
    
    # Normalisasi graph_analysis
    if 'graph_analysis' not in results:
        results['graph_analysis'] = {}
    
    # Ensure numeric fields
    if 'total_pages' not in results or results['total_pages'] is None:
        results['total_pages'] = 0
    
    if 'verified_scan' not in results:
        results['verified_scan'] = False
    
    if 'timed_out' not in results:
        results['timed_out'] = False
    
    # Normalisasi categories items
    if results.get('categories'):
        for cat_code, category in results['categories'].items():
            if not isinstance(category, dict):
                continue
            
            # Ensure category has name
            if 'name' not in category or not category['name']:
                category['name'] = 'Unknown'
            
            # Normalisasi items dalam category
            if 'items' not in category:
                category['items'] = []
            else:
                category['items'] = [_normalize_item(item) for item in category['items'] if isinstance(item, dict)]
    
    return results


def _normalize_final_conclusion(fc):
    """Normalisasi final_conclusion dengan default values."""
    if not isinstance(fc, dict):
        return _get_default_final_conclusion()
    
    # Default values
    defaults = {
        'status': 'AMAN',
        'color': 'green',
        'message': 'Tidak ada konten berbahaya yang terdeteksi',
        'risk_score': 0,
        'stats': {
            'total': 0,
            'live_malicious': 0,
            'cache_only': 0,
            'clean': 0
        }
    }
    
    # Merge dengan defaults
    normalized = {**defaults, **fc}
    
    # Normalisasi stats
    if 'stats' not in normalized or not isinstance(normalized['stats'], dict):
        normalized['stats'] = defaults['stats']
    else:
        stats_defaults = defaults['stats']
        normalized['stats'] = {**stats_defaults, **normalized['stats']}
        
        # Ensure all stats values are integers
        for key in ['total', 'live_malicious', 'cache_only', 'clean']:
            if normalized['stats'][key] is None:
                normalized['stats'][key] = 0
            else:
                try:
                    normalized['stats'][key] = int(normalized['stats'][key])
                except (ValueError, TypeError):
                    normalized['stats'][key] = 0
    
    # Ensure status and message are strings
    if normalized.get('status') is None:
        normalized['status'] = defaults['status']
    else:
        normalized['status'] = str(normalized['status'])
    
    if normalized.get('message') is None:
        normalized['message'] = defaults['message']
    else:
        normalized['message'] = str(normalized['message'])
    
    # Ensure risk_score is integer
    if normalized.get('risk_score') is None:
        normalized['risk_score'] = 0
    else:
        try:
            normalized['risk_score'] = int(normalized['risk_score'])
        except (ValueError, TypeError):
            normalized['risk_score'] = 0
    
    # Ensure color is string
    if normalized.get('color') is None:
        normalized['color'] = defaults['color']
    else:
        normalized['color'] = str(normalized['color'])
    
    return normalized


def _normalize_subdomain_results(subdomain_results):
    """Normalisasi subdomain_results dengan default values."""
    if not isinstance(subdomain_results, dict):
        return {
            'total_subdomains': 0,
            'subdomains': [],
            'techniques_used': []
        }
    
    defaults = {
        'total_subdomains': 0,
        'subdomains': [],
        'techniques_used': []
    }
    
    normalized = {**defaults, **subdomain_results}
    
    # Ensure total_subdomains is integer
    if normalized['total_subdomains'] is None:
        normalized['total_subdomains'] = 0
    else:
        try:
            normalized['total_subdomains'] = int(normalized['total_subdomains'])
        except (ValueError, TypeError):
            normalized['total_subdomains'] = 0
    
    # Ensure subdomains is list
    if not isinstance(normalized['subdomains'], list):
        normalized['subdomains'] = []
    
    # Normalisasi setiap subdomain - PERTAHANKAN data asli SEMUA, JANGAN ganti kecuali benar-benar None
    normalized_subdomains = []
    for idx, sub in enumerate(normalized['subdomains']):
        if not isinstance(sub, dict):
            logger.warning(f"Subdomain item #{idx} is not a dict: {type(sub)}")
            continue
        
        # PERTAHANKAN SEMUA field asli - gunakan dict() untuk shallow copy
        normalized_subdomain = dict(sub)  # INI MEMPERTAHANKAN SEMUA DATA ASLI
        
        # JANGAN ganti nilai yang sudah ada, bahkan jika itu string kosong
        # Hanya pastikan tipe data konsisten (convert ke string jika perlu)
        
        # Subdomain - hanya convert ke string, jangan ganti nilai
        if 'subdomain' in normalized_subdomain:
            # Jika ada, pastikan string dan pertahankan nilai asli (bahkan jika kosong)
            normalized_subdomain['subdomain'] = str(normalized_subdomain['subdomain']) if normalized_subdomain['subdomain'] is not None else ''
        # Jangan tambahkan default 'N/A' - biarkan kosong jika memang tidak ada
        
        # IP - hanya convert ke string jika ada, None tetap None (valid untuk inactive)
        if 'ip' in normalized_subdomain:
            if normalized_subdomain['ip'] is not None:
                normalized_subdomain['ip'] = str(normalized_subdomain['ip'])
            # None tetap None (valid untuk inactive subdomains)
        # Jangan tambahkan default 'N/A' - biarkan None jika memang tidak ada
        
        # Status - hanya convert ke string jika ada
        if 'status' in normalized_subdomain:
            if normalized_subdomain['status'] is not None:
                normalized_subdomain['status'] = str(normalized_subdomain['status'])
        # Jangan tambahkan default - biarkan kosong jika memang tidak ada
        
        normalized_subdomains.append(normalized_subdomain)
    
    normalized['subdomains'] = normalized_subdomains
    
    # Ensure techniques_used is list
    if not isinstance(normalized['techniques_used'], list):
        normalized['techniques_used'] = []
    
    return normalized


def _normalize_item(item):
    """Normalisasi item dalam category dengan default values - PERTAHANKAN data asli."""
    if not isinstance(item, dict):
        return {}
    
    # PERTAHANKAN semua field asli dari item, jangan ganti dengan objek baru
    # JANGAN membuat dict baru, gunakan dict() untuk shallow copy
    normalized_item = dict(item)  # Copy semua field asli - INI MEMPERTAHANKAN SEMUA DATA ASLI
    
    # HANYA tambahkan field default yang benar-benar tidak ada
    # JANGAN mengganti nilai yang sudah ada, bahkan jika itu string kosong atau None
    
    # URL - cek jika tidak ada, None, atau empty string
    url_val = normalized_item.get('url')
    if not url_val or (isinstance(url_val, str) and not url_val.strip()) or url_val is None:
        # Coba gunakan 'link' sebagai fallback
        if 'link' in item and item['link']:
            link_val = item['link']
            if link_val and (isinstance(link_val, str) and link_val.strip()):
                normalized_item['url'] = str(link_val).strip()
            elif link_val and link_val is not None:
                normalized_item['url'] = str(link_val)
        # Jika masih tidak ada, coba dari deep_analysis
        if not normalized_item.get('url') or normalized_item.get('url') is None:
            deep_analysis = normalized_item.get('deep_analysis') or item.get('deep_analysis')
            if isinstance(deep_analysis, dict):
                deep_url = deep_analysis.get('url')
                if deep_url and (isinstance(deep_url, str) and deep_url.strip()):
                    normalized_item['url'] = str(deep_url).strip()
                elif deep_url and deep_url is not None:
                    normalized_item['url'] = str(deep_url)
        # Jika masih tidak ada URL, coba cari dari source
        if not normalized_item.get('url') or normalized_item.get('url') is None:
            source = normalized_item.get('source') or item.get('source')
            if source and isinstance(source, str):
                # Jika source berisi URL, coba ekstrak
                if 'http' in source:
                    normalized_item['url'] = source
        # Jika tidak ada, set default agar tidak None
        if not normalized_item.get('url') or normalized_item.get('url') is None:
            normalized_item['url'] = ''
    
    # Title - cek jika tidak ada, None, atau empty string
    title_val = normalized_item.get('title')
    if not title_val or (isinstance(title_val, str) and not title_val.strip()) or title_val is None:
        # Coba gunakan 'headline' sebagai fallback
        if 'headline' in item and item['headline']:
            headline_val = item['headline']
            if headline_val and (isinstance(headline_val, str) and headline_val.strip()):
                normalized_item['title'] = str(headline_val).strip()
            elif headline_val and headline_val is not None:
                normalized_item['title'] = str(headline_val)
        # Jika masih kosong, coba dari deep_analysis
        if not normalized_item.get('title') or normalized_item.get('title') is None:
            deep_analysis = normalized_item.get('deep_analysis') or item.get('deep_analysis')
            if isinstance(deep_analysis, dict):
                deep_title = deep_analysis.get('title')
                if deep_title and (isinstance(deep_title, str) and deep_title.strip()):
                    normalized_item['title'] = str(deep_title).strip()
                elif deep_title and deep_title is not None:
                    normalized_item['title'] = str(deep_title)
        # Jika masih kosong, coba gunakan snippet sebagai fallback
        if not normalized_item.get('title') or normalized_item.get('title') is None:
            snippet_val = normalized_item.get('snippet') or item.get('snippet')
            if snippet_val and isinstance(snippet_val, str) and snippet_val.strip():
                # Gunakan 100 karakter pertama dari snippet sebagai title
                normalized_item['title'] = snippet_val[:100].strip()
        # Jika masih tidak ada title, set default agar tidak None
        if not normalized_item.get('title') or normalized_item.get('title') is None:
            normalized_item['title'] = 'No Title'
    
    # Snippet - hanya tambahkan jika benar-benar tidak ada atau None
    snippet_val = normalized_item.get('snippet')
    if not snippet_val or snippet_val is None:
        normalized_item['snippet'] = ''
    elif isinstance(snippet_val, str) and not snippet_val.strip():
        normalized_item['snippet'] = ''
    
    # Verification - hanya normalisasi struktur jika tidak ada
    if 'verification' not in normalized_item:
        normalized_item['verification'] = {}
    elif not isinstance(normalized_item['verification'], dict):
        # Jika ada tapi bukan dict, tetap pertahankan struktur aslinya
        normalized_item['verification'] = {}
    
    # Hanya tambahkan verification_status jika tidak ada
    if isinstance(normalized_item['verification'], dict) and 'verification_status' not in normalized_item['verification']:
        normalized_item['verification']['verification_status'] = 'unknown'
    
    # Deep analysis - hanya tambahkan jika benar-benar tidak ada
    if 'deep_analysis' not in normalized_item:
        normalized_item['deep_analysis'] = {}
    elif not isinstance(normalized_item['deep_analysis'], dict):
        normalized_item['deep_analysis'] = {}
    
    # JS analysis - hanya tambahkan jika benar-benar tidak ada
    if 'js_analysis' not in normalized_item:
        normalized_item['js_analysis'] = {
            'suspicious_requests': [],
            'high_entropy_scripts': [],
            'dangerous_patterns': []
        }
    elif not isinstance(normalized_item['js_analysis'], dict):
        normalized_item['js_analysis'] = {
            'suspicious_requests': [],
            'high_entropy_scripts': [],
            'dangerous_patterns': []
        }
    
    return normalized_item


def _get_default_final_conclusion():
    """Return default final_conclusion structure."""
    return {
        'status': 'AMAN',
        'color': 'green',
        'message': 'Tidak ada konten berbahaya yang terdeteksi',
        'risk_score': 0,
        'stats': {
            'total': 0,
            'live_malicious': 0,
            'cache_only': 0,
            'clean': 0
        }
    }


def _get_empty_results():
    """Return empty scan results structure."""
    return {
        'categories': {},
        'domain_info': {},
        'backlinks': [],
        'total_pages': 0,
        'verified_scan': False,
        'graph_analysis': {},
        'subdomain_results': {
            'total_subdomains': 0,
            'subdomains': [],
            'techniques_used': []
        },
        'final_conclusion': _get_default_final_conclusion(),
        'timed_out': False
    }

