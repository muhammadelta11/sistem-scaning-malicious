"""
Formatters untuk format data yang ditampilkan di UI.
"""

from typing import Any, Dict


def format_domain_info(domain_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format domain info untuk ditampilkan di UI dengan lebih user-friendly.
    
    Args:
        domain_info: Domain info dari whois/scan
        
    Returns:
        Formatted domain info
    """
    if not isinstance(domain_info, dict):
        return {}
    
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

