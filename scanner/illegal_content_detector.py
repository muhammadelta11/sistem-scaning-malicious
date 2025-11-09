"""
Modul untuk deteksi konten ilegal yang komprehensif.
Mendeteksi berbagai jenis konten ilegal termasuk yang disuntikkan atau tersembunyi.
"""

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
from collections import Counter

from .config import ILLEGAL_CONTENT_KEYWORDS, HIDDEN_CONTENT_PATTERNS, INJECTION_PATTERNS

logger = logging.getLogger(__name__)


class IllegalContentDetector:
    """
    Detektor konten ilegal yang komprehensif.
    Mendeteksi berbagai jenis konten ilegal dan pola injeksi.
    """
    
    def __init__(self):
        self.illegal_keywords = ILLEGAL_CONTENT_KEYWORDS
        self.hidden_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in HIDDEN_CONTENT_PATTERNS]
        self.injection_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in INJECTION_PATTERNS]
    
    def detect_illegal_content(self, html_content: str, url: str = "") -> Dict:
        """
        Deteksi konten ilegal dari HTML content.
        
        Args:
            html_content: HTML content dari halaman
            url: URL halaman (untuk konteks)
            
        Returns:
            Dict dengan hasil deteksi:
            {
                'illegal_categories': ['narkoba', 'penipuan', ...],
                'confidence_score': 0.0-1.0,
                'suspicious_elements': [...],
                'hidden_content': {...},
                'injection_detected': bool,
                'details': {...}
            }
        """
        result = {
            'illegal_categories': [],
            'confidence_score': 0.0,
            'suspicious_elements': [],
            'hidden_content': {},
            'injection_detected': False,
            'details': {}
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. Deteksi konten ilegal dari teks yang terlihat
            visible_text = self._extract_visible_text(soup)
            illegal_detection = self._detect_illegal_keywords(visible_text)
            
            # 2. Deteksi konten tersembunyi
            hidden_detection = self._detect_hidden_content(html_content, soup)
            
            # 3. Deteksi injeksi konten
            injection_detection = self._detect_injection(html_content, soup)
            
            # 4. Deteksi konten dalam komentar HTML
            comment_detection = self._detect_comments_content(html_content)
            
            # 5. Deteksi konten dalam meta tags
            meta_detection = self._detect_meta_content(soup)
            
            # 6. Deteksi konten dalam atribut tersembunyi
            attr_detection = self._detect_hidden_attributes(soup)
            
            # Gabungkan hasil
            all_categories = set()
            all_categories.update(illegal_detection['categories'])
            all_categories.update(hidden_detection.get('categories', []))
            all_categories.update(comment_detection.get('categories', []))
            all_categories.update(meta_detection.get('categories', []))
            all_categories.update(attr_detection.get('categories', []))
            
            result['illegal_categories'] = list(all_categories)
            
            # Hitung confidence score
            confidence = 0.0
            confidence += illegal_detection['confidence'] * 0.4  # 40% bobot untuk teks terlihat
            confidence += hidden_detection.get('confidence', 0.0) * 0.25  # 25% untuk konten tersembunyi
            confidence += comment_detection.get('confidence', 0.0) * 0.15  # 15% untuk komentar
            confidence += meta_detection.get('confidence', 0.0) * 0.1  # 10% untuk meta
            confidence += attr_detection.get('confidence', 0.0) * 0.1  # 10% untuk atribut
            
            if injection_detection['detected']:
                confidence += 0.2  # Bonus 20% jika ada injeksi
                result['injection_detected'] = True
            
            result['confidence_score'] = min(1.0, confidence)
            
            # Kumpulkan elemen mencurigakan
            result['suspicious_elements'].extend(illegal_detection.get('elements', []))
            result['suspicious_elements'].extend(hidden_detection.get('elements', []))
            result['suspicious_elements'].extend(comment_detection.get('elements', []))
            
            # Detail
            result['hidden_content'] = hidden_detection
            result['injection_details'] = injection_detection
            result['comment_details'] = comment_detection
            result['meta_details'] = meta_detection
            result['attribute_details'] = attr_detection
            result['visible_text_details'] = illegal_detection
            
            # Tambahkan detail URL untuk tracking
            result['url'] = url
            result['domain'] = urlparse(url).netloc if url else ""
            
        except Exception as e:
            logger.error(f"Error detecting illegal content: {e}", exc_info=True)
            result['error'] = str(e)
        
        return result
    
    def _extract_visible_text(self, soup: BeautifulSoup) -> str:
        """Ekstrak teks yang terlihat dari HTML (exclude script, style, hidden elements)."""
        # Hapus script, style, meta, link
        for tag in soup(["script", "style", "meta", "link", "noscript"]):
            tag.decompose()
        
        # Hapus elemen dengan display:none atau visibility:hidden
        for element in soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden', re.I)):
            element.decompose()
        
        # Hapus elemen dengan class yang umum untuk menyembunyikan konten
        hidden_classes = ['hidden', 'invisible', 'sr-only', 'screen-reader-only']
        for hidden_class in hidden_classes:
            for element in soup.find_all(class_=re.compile(hidden_class, re.I)):
                element.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        return text.lower()
    
    def _detect_illegal_keywords(self, text: str) -> Dict:
        """Deteksi keyword konten ilegal dalam teks."""
        result = {
            'categories': [],
            'confidence': 0.0,
            'keywords_found': {},
            'elements': []
        }
        
        keyword_matches = {}
        total_matches = 0
        
        for category, keywords in self.illegal_keywords.items():
            matches = []
            for keyword in keywords:
                pattern = re.compile(r'\b' + re.escape(keyword.lower()) + r'\b', re.IGNORECASE)
                found = pattern.findall(text)
                if found:
                    matches.extend(found)
                    total_matches += len(found)
            
            if matches:
                keyword_matches[category] = len(set(matches))
                result['categories'].append(category)
                result['keywords_found'][category] = list(set(matches))
        
        # Hitung confidence berdasarkan jumlah keyword yang ditemukan
        if total_matches > 0:
            # Confidence meningkat dengan jumlah keyword yang ditemukan
            # 1-2 keyword: 0.3, 3-5: 0.6, 6+: 0.9
            if total_matches >= 6:
                result['confidence'] = 0.9
            elif total_matches >= 3:
                result['confidence'] = 0.6
            elif total_matches >= 2:
                result['confidence'] = 0.4
            else:
                result['confidence'] = 0.3
        
        # Tambahkan elemen mencurigakan jika confidence tinggi
        if result['confidence'] >= 0.6:
            for category, keywords in result['keywords_found'].items():
                result['elements'].append({
                    'type': 'illegal_keywords',
                    'category': category,
                    'keywords': keywords,
                    'severity': 'high' if result['confidence'] >= 0.9 else 'medium'
                })
        
        return result
    
    def _detect_hidden_content(self, html_content: str, soup: BeautifulSoup) -> Dict:
        """Deteksi konten ilegal yang disembunyikan menggunakan CSS atau teknik lain."""
        result = {
            'categories': [],
            'confidence': 0.0,
            'hidden_elements': [],
            'techniques_used': []
        }
        
        hidden_text_content = []
        
        # Cari elemen dengan style yang menyembunyikan konten
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            for pattern in self.hidden_patterns:
                if pattern.search(style):
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Minimal panjang untuk dianggap signifikan
                        hidden_text_content.append({
                            'element': element.name,
                            'style': style,
                            'text': text[:200],  # Limit panjang teks
                            'technique': pattern.pattern
                        })
                        result['techniques_used'].append(pattern.pattern)
        
        # Cari elemen dengan class hidden
        hidden_classes = ['hidden', 'invisible', 'sr-only', 'd-none']
        for hidden_class in hidden_classes:
            for element in soup.find_all(class_=re.compile(hidden_class, re.I)):
                text = element.get_text(strip=True)
                if text and len(text) > 10:
                    hidden_text_content.append({
                        'element': element.name,
                        'class': hidden_class,
                        'text': text[:200],
                        'technique': 'hidden_class'
                    })
        
        # Cek apakah konten tersembunyi mengandung keyword ilegal
        if hidden_text_content:
            combined_hidden_text = ' '.join([item['text'] for item in hidden_text_content]).lower()
            illegal_check = self._detect_illegal_keywords(combined_hidden_text)
            
            if illegal_check['categories']:
                result['categories'] = illegal_check['categories']
                result['confidence'] = illegal_check['confidence'] * 0.8  # Slightly lower confidence for hidden content
                result['hidden_elements'] = hidden_text_content
                result['elements'] = illegal_check.get('elements', [])
        
        return result
    
    def _detect_injection(self, html_content: str, soup: BeautifulSoup) -> Dict:
        """Deteksi pola injeksi konten (JavaScript, iframe, dll)."""
        result = {
            'detected': False,
            'injection_types': [],
            'suspicious_code': [],
            'details': {}
        }
        
        injection_count = 0
        
        # Cek dalam script tags
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or ''
            for pattern in self.injection_patterns:
                matches = pattern.findall(script_content)
                if matches:
                    injection_count += len(matches)
                    result['injection_types'].append({
                        'type': 'script_injection',
                        'pattern': pattern.pattern,
                        'matches': len(matches),
                        'code_snippet': script_content[:500] if script_content else ''
                    })
                    result['suspicious_code'].append({
                        'element': 'script',
                        'code': script_content[:200],
                        'pattern': pattern.pattern
                    })
        
        # Cek dalam inline styles dengan JavaScript
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            if re.search(r'javascript:|expression\(', style, re.I):
                injection_count += 1
                result['injection_types'].append({
                    'type': 'css_injection',
                    'element': element.name,
                    'style': style[:200]
                })
        
        # Cek iframe dengan src eksternal yang mencurigakan
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                parsed = urlparse(src)
                # Cek jika iframe ke domain eksternal dengan URL mencurigakan
                suspicious_keywords = ['slot', 'judi', 'porn', 'bokep', 'casino', 'togel']
                if any(kw in src.lower() for kw in suspicious_keywords):
                    injection_count += 1
                    result['injection_types'].append({
                        'type': 'iframe_injection',
                        'src': src,
                        'reason': 'suspicious_domain_or_path'
                    })
        
        if injection_count > 0:
            result['detected'] = True
            result['details'] = {
                'total_injections': injection_count,
                'severity': 'high' if injection_count >= 3 else 'medium'
            }
        
        return result
    
    def _detect_comments_content(self, html_content: str) -> Dict:
        """Deteksi konten ilegal dalam HTML comments."""
        result = {
            'categories': [],
            'confidence': 0.0,
            'suspicious_comments': []
        }
        
        # Ekstrak semua HTML comments
        comment_pattern = re.compile(r'<!--(.*?)-->', re.DOTALL)
        comments = comment_pattern.findall(html_content)
        
        suspicious_comments = []
        for comment in comments:
            comment_text = comment.strip()
            if len(comment_text) > 10:  # Minimal panjang
                illegal_check = self._detect_illegal_keywords(comment_text.lower())
                if illegal_check['categories']:
                    suspicious_comments.append({
                        'comment': comment_text[:200],
                        'categories': illegal_check['categories'],
                        'keywords': illegal_check.get('keywords_found', {})
                    })
                    result['categories'].extend(illegal_check['categories'])
        
        if suspicious_comments:
            result['suspicious_comments'] = suspicious_comments
            # Confidence lebih rendah untuk konten dalam komentar
            result['confidence'] = 0.4 if suspicious_comments else 0.0
            result['elements'] = [{
                'type': 'html_comment',
                'count': len(suspicious_comments),
                'severity': 'medium'
            }]
        
        return result
    
    def _detect_meta_content(self, soup: BeautifulSoup) -> Dict:
        """Deteksi konten ilegal dalam meta tags."""
        result = {
            'categories': [],
            'confidence': 0.0,
            'suspicious_meta': []
        }
        
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            # Cek content, description, keywords
            content = meta.get('content', '') or meta.get('value', '')
            name = meta.get('name', '') or meta.get('property', '')
            
            if content:
                illegal_check = self._detect_illegal_keywords(content.lower())
                if illegal_check['categories']:
                    result['suspicious_meta'].append({
                        'name': name,
                        'content': content[:200],
                        'categories': illegal_check['categories']
                    })
                    result['categories'].extend(illegal_check['categories'])
        
        if result['suspicious_meta']:
            result['confidence'] = 0.5  # Medium confidence untuk meta tags
        
        return result
    
    def _detect_hidden_attributes(self, soup: BeautifulSoup) -> Dict:
        """Deteksi konten ilegal dalam atribut tersembunyi (data-*, title, alt, dll)."""
        result = {
            'categories': [],
            'confidence': 0.0,
            'suspicious_attributes': []
        }
        
        # Cek atribut data-*, title, alt, aria-label
        suspicious_attrs = ['data-*', 'title', 'alt', 'aria-label', 'aria-description']
        
        for element in soup.find_all(True):  # Semua elemen
            for attr in element.attrs:
                attr_value = str(element.get(attr, ''))
                
                # Cek data-* attributes
                if attr.startswith('data-') and attr_value:
                    illegal_check = self._detect_illegal_keywords(attr_value.lower())
                    if illegal_check['categories']:
                        result['suspicious_attributes'].append({
                            'element': element.name,
                            'attribute': attr,
                            'value': attr_value[:200],
                            'categories': illegal_check['categories']
                        })
                        result['categories'].extend(illegal_check['categories'])
                
                # Cek title, alt, aria-label
                elif attr in ['title', 'alt', 'aria-label', 'aria-description'] and attr_value:
                    illegal_check = self._detect_illegal_keywords(attr_value.lower())
                    if illegal_check['categories']:
                        result['suspicious_attributes'].append({
                            'element': element.name,
                            'attribute': attr,
                            'value': attr_value[:200],
                            'categories': illegal_check['categories']
                        })
                        result['categories'].extend(illegal_check['categories'])
        
        if result['suspicious_attributes']:
            result['confidence'] = 0.3  # Lower confidence untuk atribut tersembunyi
        
        return result
    
    def analyze_page_structure(self, html_content: str, url: str) -> Dict:
        """
        Analisis struktur halaman untuk menemukan indikasi konten ilegal.
        Termasuk analisis link, form, dan elemen interaktif.
        """
        result = {
            'suspicious_links': [],
            'suspicious_forms': [],
            'external_domains': [],
            'risk_score': 0.0
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analisis link
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Cek jika link mengandung keyword ilegal
                illegal_check = self._detect_illegal_keywords(href.lower() + ' ' + link_text)
                if illegal_check['categories']:
                    parsed = urlparse(href)
                    result['suspicious_links'].append({
                        'url': href,
                        'text': link_text[:100],
                        'domain': parsed.netloc,
                        'categories': illegal_check['categories']
                    })
                    
                    if parsed.netloc and parsed.netloc not in result['external_domains']:
                        result['external_domains'].append(parsed.netloc)
            
            # Analisis form
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '')
                form_text = form.get_text(strip=True).lower()
                
                illegal_check = self._detect_illegal_keywords(action.lower() + ' ' + form_text)
                if illegal_check['categories']:
                    result['suspicious_forms'].append({
                        'action': action,
                        'text': form_text[:200],
                        'categories': illegal_check['categories']
                    })
            
            # Hitung risk score
            risk_factors = 0
            if result['suspicious_links']:
                risk_factors += len(result['suspicious_links']) * 0.1
            if result['suspicious_forms']:
                risk_factors += len(result['suspicious_forms']) * 0.2
            if result['external_domains']:
                risk_factors += len(result['external_domains']) * 0.1
            
            result['risk_score'] = min(1.0, risk_factors)
            
        except Exception as e:
            logger.error(f"Error analyzing page structure: {e}", exc_info=True)
            result['error'] = str(e)
        
        return result

