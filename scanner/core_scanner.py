#Berisi semua logika inti untuk pemindaian, validasi, dan analisis.

import pandas as pd
from serpapi.google_search import GoogleSearch
import time
import requests
from bs4 import BeautifulSoup
import re
import math
from datetime import datetime
import whois
import networkx as nx
from urllib.parse import urljoin, urlparse
import urllib.robotparser
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
import logging
import functools
import socket
import dns.resolver
from django.core.cache import cache
import tldextract
import asyncio
import httpx

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import konstanta dari config.py
from .config import MALICIOUS_KEYWORDS, ABUSEIPDB_API_KEY, BLACKLIST_SOURCES, USE_NATIVE_FLOW
from .api_cache import get_cached_search_result, set_cached_search_result
SAFE_DOMAINS = [
    'google-analytics.com', 'googletagmanager.com', 'cdnjs.cloudflare.com',
    'bootstrapcdn.com', 'jquery.com', 'gstatic.com'
]

warnings.filterwarnings('ignore')

STRIP_PARAMS = {
    'utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','fbclid','utm_name','utm_id','utm_reader'
}

UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
]

def get_active_malicious_keywords():
    """Ambil keywords aktif dari DB dan cache di memori."""
    try:
        # Import lokal untuk menghindari circular import saat migrate/collectstatic
        from .models import MaliciousKeyword
        active = list(MaliciousKeyword.objects.filter(is_active=True).values_list('keyword', flat=True))
        return [str(k).lower() for k in active if k]
    except Exception:
        # Jika DB belum siap, fallback ke kosong
        return []

def get_dynamic_keywords():
    """Gabungkan keyword dari config dan database (aktif)."""
    try:
        db_keys = get_active_malicious_keywords()
    except Exception:
        db_keys = []
    base = [str(k).lower() for k in MALICIOUS_KEYWORDS]
    # gabungkan unik, pertahankan urutan dasar
    merged = list(dict.fromkeys(base + db_keys))
    return merged

def canonicalize_url(raw_url: str) -> str:
    """
    Canonicalize URL with smart query parameter handling.
    CRITICAL: Preserves query params that contain malicious keywords!
    """
    try:
        parsed = urlparse(raw_url)
        scheme = parsed.scheme or 'https'
        netloc = parsed.netloc.lower()
        if netloc.endswith(':80'):
            netloc = netloc[:-3]
        if netloc.endswith(':443'):
            netloc = netloc[:-4]
        path = parsed.path or '/'
        
        # CRITICAL FIX: Check if query params contain malicious keywords
        malicious_keywords = ['bokep', 'gacor', 'slot', 'judi', 'porn', 'xxx', 'hacked', 'deface', 'casino']
        query_params = parsed.query
        
        # Preserve query params if they contain malicious keywords
        should_preserve_query = False
        if query_params:
            query_lower = query_params.lower()
            if any(kw in query_lower for kw in malicious_keywords):
                should_preserve_query = True
                logging.debug(f"Preserving malicious query params: {query_params}")
        
        if should_preserve_query:
            # PRESERVE the full URL with params
            return f"{scheme}://{netloc}{path}?{query_params}"
        else:
            # Original behavior: strip safe params
            query_pairs = [(k, v) for k, v in re.findall(r'([^=&?#]+)=([^&#]*)', parsed.query) if k not in STRIP_PARAMS]
            query = '&'.join([f"{k}={v}" for k, v in sorted(query_pairs)])
            return urlparse(f"{scheme}://{netloc}{path}")._replace(query=query, fragment='').geturl().rstrip('/')
    except Exception:
        return raw_url

def deduplicate_results(items: list) -> list:
    seen = set()
    unique = []
    for item in items or []:
        url = canonicalize_url(item.get('url') or item.get('link') or '')
        if not url or url in seen:
            continue
        seen.add(url)
        item['url'] = url
        unique.append(item)
    return unique

def is_url_from_domain(url: str, base_domain: str, include_subdomains: bool = True) -> bool:
    try:
        netloc = urlparse(url).netloc.lower()
        if not netloc:
            return False
        ext_target = tldextract.extract(netloc)
        ext_base = tldextract.extract(base_domain.lower())
        registrable_target = f"{ext_target.domain}.{ext_target.suffix}".lstrip('.')
        registrable_base = f"{ext_base.domain}.{ext_base.suffix}".lstrip('.')
        if registrable_target != registrable_base:
            return False
        if include_subdomains:
            return True
        return ext_target.subdomain == ''
    except Exception:
        return base_domain in url

def extract_urls_from_sitemap(domain: str) -> list:
    urls = []
    for path in ['sitemap.xml', 'sitemap_index.xml']:
        try:
            r = requests.get(f"https://{domain}/{path}", timeout=8)
            if r.status_code != 200:
                continue
            text = r.text
            if '<urlset' in text or '<sitemapindex' in text:
                soup = BeautifulSoup(text, 'xml')
                for loc in soup.find_all('loc'):
                    u = canonicalize_url(loc.text.strip())
                    if is_url_from_domain(u, domain, True):
                        urls.append(u)
        except Exception:
            continue
    # unique preserve order
    seen = set()
    result = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result

async def _fetch_httpx(client: httpx.AsyncClient, url: str, timeout: float = 8.0):
    try:
        r = await client.get(url, timeout=timeout, headers={'User-Agent': UA_LIST[0]})
        if r.status_code >= 400:
            return None
        return r.text
    except Exception:
        return None

async def _crawl_domain_fast_async(domain: str, max_pages: int = 50):
    start = f"https://{domain}"
    to_visit = [start]
    visited = set()
    found = []
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        while to_visit and len(visited) < max_pages:
            batch = []
            while to_visit and len(batch) < 8:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                batch.append(url)
            pages = await asyncio.gather(*[_fetch_httpx(client, u) for u in batch])
            for url, html in zip(batch, pages):
                if not html:
                    continue
                soup = BeautifulSoup(html, 'html.parser')
                text_l = soup.get_text(separator=' ', strip=True).lower()
                dyn_keywords = get_dynamic_keywords()
                if any(kw in text_l for kw in dyn_keywords):
                    found.append({'url': canonicalize_url(url), 'title': soup.title.get_text() if soup.title else 'No Title', 'snippet': text_l[:200], 'source': 'crawler_fast'})
                for a in soup.find_all('a', href=True):
                    abs_url = urljoin(url, a['href'])
                    abs_url = canonicalize_url(abs_url)
                    if is_url_from_domain(abs_url, domain, True) and abs_url not in visited and abs_url not in to_visit:
                        to_visit.append(abs_url)
    return found

def crawl_domain_fast(domain: str, max_pages: int = 50):
    try:
        return asyncio.run(_crawl_domain_fast_async(domain, max_pages=max_pages))
    except RuntimeError:
        # event loop already running (e.g., inside certain environments)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_crawl_domain_fast_async(domain, max_pages=max_pages))

def deep_crawl_unindexed_pages(domain: str, max_pages: int = 100, scan_id: None = None):
    """
    Deep crawling untuk menemukan halaman yang tidak terindex Google.
    Mencari halaman yang tersembunyi, tidak ada di sitemap, atau tidak terlink dari homepage.
    
    Args:
        domain: Domain target
        max_pages: Maksimal halaman yang akan di-crawl
        scan_id: ID scan untuk tracking progress
        
    Returns:
        List halaman yang ditemukan dengan indikasi konten ilegal
    """
    logging.info(f"Memulai deep crawl untuk menemukan halaman tidak terindex di {domain}")
    driver = setup_selenium_driver()
    if not driver:
        logging.error("Gagal setup Selenium driver untuk deep crawl")
        return []
    
    found_pages = []
    visited = set()
    to_visit = [f"https://{domain}"]
    
    # Import illegal content detector
    try:
        from .illegal_content_detector import IllegalContentDetector
        detector = IllegalContentDetector()
    except Exception as e:
        logging.error(f"Error importing illegal content detector: {e}")
        detector = None
    
    try:
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            # Update progress
            if scan_id:
                cache.set(f'scan_progress_{scan_id}', {
                    'status': 'PROCESSING',
                    'phase': 'Deep Crawl',
                    'current': len(visited),
                    'total': max_pages,
                    'message': f"Deep crawling halaman {len(visited)}/{max_pages}: {current_url}"
                }, timeout=3600)
            
            try:
                driver.get(current_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Tunggu JavaScript selesai loading
                time.sleep(2)
                
                page_source = driver.page_source
                
                # Analisis konten ilegal
                if detector:
                    illegal_result = detector.detect_illegal_content(page_source, current_url)
                    
                    # Jika ditemukan konten ilegal, tambahkan ke hasil
                    if illegal_result.get('illegal_categories') and len(illegal_result['illegal_categories']) > 0:
                        soup = BeautifulSoup(page_source, 'html.parser')
                        title_tag = soup.find('title')
                        title = title_tag.get_text(strip=True) if title_tag else 'No Title'
                        
                        found_pages.append({
                            'url': current_url,
                            'title': title,
                            'snippet': soup.get_text(strip=True)[:200],
                            'source': 'deep_crawl_unindexed',
                            'illegal_categories': illegal_result['illegal_categories'],
                            'confidence_score': illegal_result.get('confidence_score', 0.0),
                            'injection_detected': illegal_result.get('injection_detected', False),
                            'hidden_content': illegal_result.get('hidden_content', {}),
                            'detection_details': illegal_result
                        })
                        
                        logging.info(f"Ditemukan konten ilegal di halaman tidak terindex: {current_url}")
                        logging.info(f"  Kategori: {illegal_result['illegal_categories']}")
                        logging.info(f"  Confidence: {illegal_result.get('confidence_score', 0.0)}")
                
                # Cari link baru untuk dikunjungi
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        
                        # Normalisasi URL
                        abs_url = urljoin(current_url, href)
                        abs_url = canonicalize_url(abs_url)
                        
                        # Pastikan link internal
                        if is_url_from_domain(abs_url, domain, include_subdomains=True):
                            if abs_url not in visited and abs_url not in to_visit:
                                to_visit.append(abs_url)
                    except:
                        continue
                
            except Exception as e:
                logging.warning(f"Error crawling {current_url}: {e}")
                continue
        
        logging.info(f"Deep crawl selesai. Ditemukan {len(found_pages)} halaman dengan konten ilegal")
        
    finally:
        driver.quit()
    
    return found_pages

def discover_unindexed_pages(domain: str, primary_key: str = None, fallback_key: str = None, scan_id: None = None):
    """
    Temukan halaman yang tidak terindex Google dengan berbagai metode:
    1. Deep crawling domain
    2. Analisis sitemap untuk URL yang tidak terindex
    3. Analisis robots.txt untuk menemukan path tersembunyi
    4. Brute force path umum untuk konten ilegal
    """
    logging.info(f"Memulai discovery halaman tidak terindex untuk {domain}")
    discovered_pages = []
    
    # 1. Deep crawl
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Unindexed Discovery',
            'message': f"Mencari halaman tidak terindex di {domain}..."
        }, timeout=3600)
    
    crawled_pages = deep_crawl_unindexed_pages(domain, max_pages=100, scan_id=scan_id)
    discovered_pages.extend(crawled_pages)
    
    # 2. Analisis sitemap untuk menemukan URL yang tidak terindex Google
    try:
        if scan_id:
            cache.set(f'scan_progress_{scan_id}', {
                'status': 'PROCESSING',
                'phase': 'Sitemap Analysis',
                'message': 'Menganalisis sitemap untuk URL tidak terindex...'
            }, timeout=3600)
        
        sitemap_urls = extract_urls_from_sitemap(domain)
        
        # Untuk setiap URL di sitemap, cek apakah terindex Google
        if primary_key and sitemap_urls:
            logging.info(f"Memeriksa {len(sitemap_urls)} URL dari sitemap")
            unindexed_from_sitemap = []
            
            for url in sitemap_urls[:50]:  # Limit untuk menghindari rate limit
                try:
                    # Cek apakah URL terindex di Google
                    params = {
                        "engine": "google",
                        "q": f'site:{url}',
                        "api_key": primary_key,
                        "num": 1
                    }
                    search = GoogleSearch(params)
                    results = search.get_dict()
                    
                    if not results.get('organic_results'):
                        # URL tidak terindex, tambahkan ke daftar untuk di-scan
                        unindexed_from_sitemap.append(url)
                        logging.info(f"Ditemukan URL tidak terindex: {url}")
                
                except Exception as e:
                    logging.debug(f"Error checking indexation for {url}: {e}")
                    continue
            
            # Scan URL yang tidak terindex
            if unindexed_from_sitemap:
                try:
                    from .illegal_content_detector import IllegalContentDetector
                    detector = IllegalContentDetector()
                    
                    for url in unindexed_from_sitemap[:20]:  # Limit scan
                        try:
                            response = requests.get(url, timeout=10, headers={'User-Agent': UA_LIST[0]})
                            if response.status_code == 200:
                                illegal_result = detector.detect_illegal_content(response.text, url)
                                
                                if illegal_result.get('illegal_categories'):
                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    title_tag = soup.find('title')
                                    title = title_tag.get_text(strip=True) if title_tag else 'No Title'
                                    
                                    discovered_pages.append({
                                        'url': url,
                                        'title': title,
                                        'snippet': soup.get_text(strip=True)[:200],
                                        'source': 'sitemap_unindexed',
                                        'illegal_categories': illegal_result['illegal_categories'],
                                        'confidence_score': illegal_result.get('confidence_score', 0.0),
                                        'detection_details': illegal_result
                                    })
                        except Exception as e:
                            logging.debug(f"Error scanning unindexed URL {url}: {e}")
                            continue
                
                except Exception as e:
                    logging.warning(f"Error in unindexed URL scanning: {e}")
        
    except Exception as e:
        logging.warning(f"Error analyzing sitemap: {e}")
    
    # 3. Brute force path umum untuk konten ilegal
    try:
        if scan_id:
            cache.set(f'scan_progress_{scan_id}', {
                'status': 'PROCESSING',
                'phase': 'Path Discovery',
                'message': 'Mencari path tersembunyi dengan konten ilegal...'
            }, timeout=3600)
        
        # Path umum untuk konten ilegal (sering disembunyikan di path tersembunyi)
        suspicious_paths = [
            '/admin/', '/wp-admin/', '/hidden/', '/private/', '/secret/',
            '/test/', '/dev/', '/staging/', '/backup/', '/old/',
            '/tmp/', '/temp/', '/cache/', '/logs/', '/config/',
            '/api/admin', '/api/test', '/api/dev',
            '/slot', '/judi', '/casino', '/poker', '/togel',
            '/bokep', '/porn', '/xxx', '/adult',
            '/drugs', '/narkoba', '/scam', '/fraud',
            '/.hidden/', '/.private/', '/.secret/',
        ]
        
        discovered_paths = []
        for path in suspicious_paths[:30]:  # Limit untuk performa
            test_url = f"https://{domain}{path}"
            try:
                response = requests.head(test_url, timeout=5, headers={'User-Agent': UA_LIST[0]}, allow_redirects=True)
                if response.status_code == 200:
                    discovered_paths.append(test_url)
            except:
                continue
        
        # Scan path yang ditemukan
        if discovered_paths:
            try:
                from .illegal_content_detector import IllegalContentDetector
                detector = IllegalContentDetector()
                
                for url in discovered_paths[:20]:  # Limit scan
                    try:
                        response = requests.get(url, timeout=10, headers={'User-Agent': UA_LIST[0]})
                        if response.status_code == 200:
                            illegal_result = detector.detect_illegal_content(response.text, url)
                            
                            if illegal_result.get('illegal_categories'):
                                soup = BeautifulSoup(response.text, 'html.parser')
                                title_tag = soup.find('title')
                                title = title_tag.get_text(strip=True) if title_tag else 'No Title'
                                
                                discovered_pages.append({
                                    'url': url,
                                    'title': title,
                                    'snippet': soup.get_text(strip=True)[:200],
                                    'source': 'path_discovery',
                                    'illegal_categories': illegal_result['illegal_categories'],
                                    'confidence_score': illegal_result.get('confidence_score', 0.0),
                                    'detection_details': illegal_result
                                })
                    except Exception as e:
                        logging.debug(f"Error scanning discovered path {url}: {e}")
                        continue
            
            except Exception as e:
                logging.warning(f"Error in path discovery scanning: {e}")
    
    except Exception as e:
        logging.warning(f"Error in path discovery: {e}")
    
    logging.info(f"Discovery halaman tidak terindex selesai. Ditemukan {len(discovered_pages)} halaman dengan konten ilegal")
    return discovered_pages

def fetch_with_user_agents(url: str, timeout: int = 8):
    variants = []
    for ua in UA_LIST:
        try:
            r = requests.get(url, timeout=timeout, headers={'User-Agent': ua}, allow_redirects=True)
            text = r.text or ''
            variants.append({'ua': ua, 'status': r.status_code, 'len': len(text), 'hash': hash(text), 'text': text.lower()})
        except Exception:
            variants.append({'ua': ua, 'error': True})
    return variants

def quick_verification(url: str, cache_data: dict):
    variants = fetch_with_user_agents(url)
    cache_text = f"{cache_data.get('title','')} {cache_data.get('snippet','')}".lower()
    dyn_keywords = get_dynamic_keywords()
    cache_has_keywords = any(kw in cache_text for kw in dyn_keywords)
    ok_variants = [v for v in variants if not v.get('error')]
    live_hits = any(any(kw in v.get('text','') for kw in dyn_keywords) for v in ok_variants)
    large_diff = len(set([v['hash'] for v in ok_variants])) > 1 if len(ok_variants) >= 2 else False
    need_headless = (not live_hits and cache_has_keywords) or large_diff
    status = 'live_malicious' if live_hits else ('cache_only' if cache_has_keywords and not live_hits else 'clean')
    return {'live_hits': live_hits, 'need_headless': need_headless, 'variants': variants, 'status': status}

def enumerate_subdomains(domain, primary_key, fallback_key=None):
    """
    Enumerasi subdomain menggunakan berbagai teknik:
    - DNS lookup untuk subdomain umum
    - Web search menggunakan SerpAPI
    - Brute force dengan wordlist sederhana
    - Validasi DNS untuk subdomain yang ditemukan
    """
    logging.info(f"Memulai enumerasi subdomain untuk {domain}")
    found_subdomains = set()

    # 1. DNS Lookup untuk subdomain umum (Enhanced - 100+ entries)
    common_subdomains = [
        # Basic
        'www', 'api', 'cdn', 'assets', 'static', 'media', 'images', 'img', 'files', 'upload',
        # Email & Communication
        'mail', 'email', 'smtp', 'pop', 'pop3', 'imap', 'webmail', 'exchange', 'owa', 'zimbra',
        # Admin & Control
        'admin', 'administrator', 'manage', 'management', 'panel', 'dashboard', 'control',
        # Services
        'ftp', 'file', 'download', 'backup',
        'blog', 'news', 'forum', 'community', 'wiki', 'docs', 'documentation',
        'shop', 'store', 'cart', 'buy', 'checkout', 'payment', 'pay', 'ecommerce',
        # Development
        'dev', 'develop', 'development', 'stage', 'staging', 'test', 'testing', 'qa', 'beta', 'alpha',
        # Security
        'secure', 'ssl', 'ssl-', 'tsa', 'cert', 'vpn', 'remote',
        # Access
        'login', 'signin', 'auth', 'authentication', 'portal', 'access',
        # Mobile & Applications
        'mobile', 'm', 'app', 'apps', 'application', 'wap', 'wap2', 'iphone', 'android',
        # Common services
        'cpanel', 'whm', 'plesk', 'hosting', 'server', 'ns1', 'ns2', 'dns',
        # Indonesian specific
        'pengumuman', 'artikel', 'berita', 'kontak', 'tentang', 'info', 'layanan',
        # University specific (untuk .ac.id)
        'elearning', 'simak', 'pmb', 'sip', 'student', 'dosen', 'academic',
        'perpus', 'perpustakaan', 'library', 'lab', 'laboratorium', 'research',
        # Additional
        'old', 'legacy', 'archive', 'archive2', 'mirror', 'temp', 'tmp', 'backup', 'demo'
    ]

    for sub in common_subdomains:
        subdomain = f"{sub}.{domain}"
        try:
            # Coba resolve A record
            answers = dns.resolver.resolve(subdomain, 'A')
            if answers:
                found_subdomains.add(subdomain)
                logging.info(f"Ditemukan subdomain via DNS: {subdomain}")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            continue
        except Exception as e:
            logging.debug(f"Error checking {subdomain}: {e}")
            continue

    # 2. Web Search menggunakan SerpAPI untuk menemukan subdomain
    # Ambil konfigurasi dari database
    config = get_system_config()
    USE_SUBDOMAIN_SEARCH = config.enable_subdomain_search if config else False
    
    try:
        if not USE_SUBDOMAIN_SEARCH:
            logging.info("Subdomain search via SerpAPI disabled untuk hemat quota. Hanya menggunakan DNS lookup.")
        else:
            search_queries = [
                f'site:{domain} -www.{domain}',
                # f'inurl:{domain} subdomain',  # Remove query ini untuk hemat quota
                # f'{domain} subdomain list'  # Remove query ini untuk hemat quota
            ]

        for query in search_queries if USE_SUBDOMAIN_SEARCH else []:
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": primary_key,
                    "num": 20
                }

                search = GoogleSearch(params)
                results = search.get_dict()

                if 'error' in results:
                    if fallback_key and ("quota" in str(results['error']).lower() or "forbidden" in str(results['error']).lower()):
                        params["api_key"] = fallback_key
                        search = GoogleSearch(params)
                        results = search.get_dict()

                organic_results = results.get('organic_results', [])
                for result in organic_results:
                    url = result.get('link', '')
                    if url:
                        parsed = urlparse(url)
                        if parsed.netloc and parsed.netloc.endswith(f'.{domain}'):
                            subdomain = parsed.netloc
                            if subdomain != domain and subdomain not in found_subdomains:
                                found_subdomains.add(subdomain)
                                logging.info(f"Ditemukan subdomain via search: {subdomain}")

            except Exception as e:
                logging.warning(f"Error in web search for subdomains: {e}")
                continue

    except Exception as e:
        logging.error(f"Web search for subdomains failed: {e}")

    # 3. Certificate Transparency Logs (FREE, very effective!)
    try:
        ct_log_url = f"https://crt.sh/?q=%.{domain}&output=json"
        ct_response = requests.get(ct_log_url, timeout=15)
        if ct_response.status_code == 200:
            ct_data = ct_response.json()
            ct_subdomains_found = 0
            for entry in ct_data:
                name_value = entry.get('name_value', '')
                if name_value:
                    # Handle multiple names per certificate
                    for name in name_value.split('\n'):
                        name = name.strip().lower()
                        if name and name != domain:
                            # Extract subdomain menggunakan tldextract untuk akurasi lebih baik
                            try:
                                extracted = tldextract.extract(name)
                                extracted_domain = tldextract.extract(domain.lower())
                                
                                # Bandingkan domain dan suffix
                                if extracted.domain == extracted_domain.domain and extracted.suffix == extracted_domain.suffix:
                                    # Jika ada subdomain, tambahkan ke set
                                    if extracted.subdomain:
                                        # Skip wildcard
                                        if extracted.subdomain.startswith('*'):
                                            continue
                                        # Reconstruct full subdomain
                                        subdomain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
                                        if subdomain != domain and subdomain not in found_subdomains:
                                            found_subdomains.add(subdomain)
                                            ct_subdomains_found += 1
                                            logging.debug(f"Ditemukan subdomain via CT logs: {subdomain}")
                            except Exception as e:
                                logging.debug(f"Error processing CT log entry {name}: {e}")
                                continue
            if ct_subdomains_found > 0:
                logging.info(f"Ditemukan {ct_subdomains_found} subdomain dari Certificate Transparency Logs")
    except Exception as e:
        logging.debug(f"CT logs check failed: {e}")

    # 4. Validasi DNS untuk semua subdomain yang ditemukan
    validated_subdomains = []
    for subdomain in found_subdomains:
        try:
            # Coba resolve untuk memastikan subdomain aktif
            ip = socket.gethostbyname(subdomain)
            validated_subdomains.append({
                'subdomain': subdomain,
                'ip': ip,
                'status': 'active'
            })
        except socket.gaierror:
            # Jika tidak bisa resolve, tetap sertakan tapi mark sebagai inactive
            validated_subdomains.append({
                'subdomain': subdomain,
                'ip': None,
                'status': 'inactive'
            })

    logging.info(f"Enumerasi subdomain selesai. Ditemukan {len(validated_subdomains)} subdomain")
    
    # Techniques used tracking
    techniques_used = []
    if common_subdomains:
        techniques_used.append('dns_lookup')
    if USE_SUBDOMAIN_SEARCH:
        techniques_used.append('web_search')
    techniques_used.append('certificate_transparency')
    
    return {
        'total_subdomains': len(validated_subdomains),
        'subdomains': validated_subdomains,
        'techniques_used': techniques_used
    }

def scan_subdomain_content(subdomain, primary_key, fallback_key=None, model=None, label_mapping=None, enable_verification=False):
    """
    Scan konten subdomain untuk menemukan konten malicious.
    Menggunakan Google search untuk subdomain dan menganalisis hasilnya.
    
    Args:
        subdomain: Subdomain yang akan di-scan
        primary_key: Primary API key untuk SerpAPI
        fallback_key: Fallback API key (opsional)
        model: ML model untuk klasifikasi
        label_mapping: Mapping label untuk klasifikasi
        enable_verification: Apakah menggunakan verifikasi real-time
        
    Returns:
        List hasil scan subdomain yang mengandung konten malicious
    """
    logging.info(f"Memulai scan konten untuk subdomain: {subdomain}")
    subdomain_results = []
    
    try:
        # Search Google untuk subdomain dengan query malicious keywords
        subdomain_search_results = search_google(subdomain, primary_key, fallback_key)
        
        if not subdomain_search_results:
            logging.debug(f"Tidak ada hasil search untuk subdomain {subdomain}")
            return subdomain_results
        
        # Analisis setiap hasil untuk menemukan konten malicious
        reverse_mapping = {v: k for k, v in label_mapping.items()} if label_mapping else {}
        categories = {label_code: {"name": label_name.replace("_", " ").title(), "items": []}
                      for label_code, label_name in reverse_mapping.items() if label_name != 'aman'}
        
        for result in subdomain_search_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}"
            
            pred = None
            if model:
                try:
                    pred = model.predict([text])[0]
                except Exception as e:
                    logging.debug(f"Model prediction error untuk {result.get('url', '')}: {e}")
            
            # Fallback ke keyword detection jika model tidak ada atau gagal
            if not pred:
                text_l = text.lower()
                pred_label = None
                if any(k in text_l for k in ['porn', 'bokep', 'xxx', 'nonton film dewasa', 'video dewasa']):
                    pred_label = 'pornografi'
                elif any(k in text_l for k in ['hacked', 'deface', 'defaced']):
                    pred_label = 'hacked'
                elif any(k in text_l for k in ['judi', 'togel', 'casino', 'slot', 'gacor', 'sbobet']):
                    pred_label = 'hack judol'
                
                if pred_label:
                    pred = label_mapping.get(pred_label) if label_mapping else None
            
            # Jika ditemukan konten malicious, tambahkan ke hasil
            if pred and pred in categories:
                # Tambahkan metadata bahwa ini dari subdomain
                result['source'] = f"subdomain_{subdomain}"
                result['subdomain'] = subdomain
                
                # Lakukan deep analysis untuk mendapatkan lebih banyak informasi
                try:
                    result['deep_analysis'] = deep_analysis(result['url'])
                except Exception as e:
                    logging.debug(f"Deep analysis error untuk {result.get('url', '')}: {e}")
                    result['deep_analysis'] = {}
                
                subdomain_results.append(result)
                logging.info(f"Ditemukan konten malicious di subdomain {subdomain}: {result.get('url', '')}")
    
    except Exception as e:
        logging.error(f"Error scanning subdomain {subdomain}: {e}", exc_info=True)
    
    logging.info(f"Scan subdomain {subdomain} selesai. Ditemukan {len(subdomain_results)} hasil malicious")
    return subdomain_results

def check_domain_blacklist(domain):
    """Check if domain is blacklisted using configured sources."""
    results = {}
    for source in BLACKLIST_SOURCES:
        if source == 'abuseipdb':
            results[source] = check_abuseipdb(domain)
        # Add more sources here if needed
    
    # Additional FREE blacklist checks (no API key needed)
    try:
        # Check URLHaus (FREE)
        urlhaus_result = check_urlhaus(domain)
        if urlhaus_result:
            results['urlhaus'] = urlhaus_result
    except Exception as e:
        logging.debug(f"URLHaus check failed: {e}")
    
    try:
        # Check VXVault (FREE)
        vxvault_result = check_vxvault(domain)
        if vxvault_result:
            results['vxvault'] = vxvault_result
    except Exception as e:
        logging.debug(f"VXVault check failed: {e}")
    
    return results

def check_abuseipdb(domain):
    """Check domain against AbuseIPDB blacklist with enhanced error handling."""
    if not ABUSEIPDB_API_KEY or ABUSEIPDB_API_KEY == 'your_abuseipdb_api_key_here':
        return {'error': 'AbuseIPDB API key not configured'}

    try:
        # First, try to resolve domain to IP if needed, but AbuseIPDB can handle domains
        url = "https://api.abuseipdb.com/api/v2/check"
        params = {
            'domain': domain,  # Use 'domain' parameter for better domain support
            'maxAgeInDays': 90
        }
        headers = {
            'Accept': 'application/json',
            'Key': ABUSEIPDB_API_KEY
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            abuse_data = data.get('data', {})
            if abuse_data:
                return {
                    'is_blacklisted': abuse_data.get('abuseConfidenceScore', 0) > 50,
                    'abuse_score': abuse_data.get('abuseConfidenceScore', 0),
                    'total_reports': abuse_data.get('totalReports', 0),
                    'last_reported': abuse_data.get('lastReportedAt', 'N/A'),
                    'country': abuse_data.get('countryCode', 'N/A')
                }
            else:
                return {'error': 'No data returned from AbuseIPDB'}
        elif response.status_code == 401:
            return {'error': 'Invalid AbuseIPDB API key'}
        elif response.status_code == 429:
            return {'error': 'AbuseIPDB rate limit exceeded'}
        elif response.status_code == 422:
            return {'error': 'Invalid domain or parameters'}
        else:
            return {'error': f'AbuseIPDB API error: {response.status_code} - {response.text}'}
    except requests.exceptions.Timeout:
        return {'error': 'Request to AbuseIPDB timed out'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error to AbuseIPDB'}
    except Exception as e:
        logging.warning(f"Unexpected error in check_abuseipdb for {domain}: {e}")
        return {'error': f'Unexpected error: {str(e)}'}

def check_urlhaus(domain):
    """Check domain against URLHaus blacklist (FREE, no API key)."""
    try:
        url = f"https://urlhaus.abuse.ch/api/lookupurl/"
        response = requests.post(url, data={'url': f"https://{domain}"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('query_status') == 'ok':
                if data.get('urlhaus_reference'):
                    return {
                        'is_blacklisted': True,
                        'threat': data.get('threat', 'Unknown'),
                        'urlhaus_reference': data.get('urlhaus_reference'),
                        'url_status': data.get('url_status', 'Unknown')
                    }
                else:
                    return {'is_blacklisted': False}
            else:
                return {'error': f"URLHaus query status: {data.get('query_status')}"}
        else:
            return {'error': f'URLHaus API error: {response.status_code}'}
    except Exception as e:
        return {'error': f'URLHaus request failed: {str(e)}'}

def check_vxvault(domain):
    """Check domain against VXVault blacklist (FREE, no API key)."""
    try:
        url = "http://vxvault.net/URL_List.php"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Simple text search in response
            if domain in response.text:
                return {
                    'is_blacklisted': True,
                    'matched': True,
                    'source': 'VXVault'
                }
            else:
                return {'is_blacklisted': False}
        else:
            return {'error': f'VXVault API error: {response.status_code}'}
    except Exception as e:
        return {'error': f'VXVault request failed: {str(e)}'}

# Cache untuk domain intelligence dan deep analysis
@functools.lru_cache(maxsize=100)
def cached_domain_intelligence(domain):
    """Cache hasil domain intelligence untuk menghindari pemanggilan berulang."""
    try:
        domain_info = whois.whois(domain)
        return {
            'registrar': getattr(domain_info, 'registrar', 'N/A'),
            'creation_date': getattr(domain_info, 'creation_date', 'N/A'),
            'expiration_date': getattr(domain_info, 'expiration_date', 'N/A'),
            'name_servers': getattr(domain_info, 'name_servers', 'N/A'),
            'status': getattr(domain_info, 'status', 'N/A'),
        }
    except Exception as e:
        logging.warning(f"Gagal mendapatkan info domain {domain}: {e}")
        return {'registrar': 'N/A', 'creation_date': 'N/A', 'expiration_date': 'N/A', 'name_servers': 'N/A', 'status': 'N/A'}

@functools.lru_cache(maxsize=50)
def cached_blacklist_check(domain):
    """Cache hasil blacklist check untuk menghindari pemanggilan berulang."""
    return check_domain_blacklist(domain)

@functools.lru_cache(maxsize=200)
def cached_deep_analysis(url):
    """Cache hasil deep analysis untuk menghindari pemanggilan berulang."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.string if soup.title else 'No Title'
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else 'No Description'

        # Analisis tambahan
        has_iframe = len(soup.find_all('iframe')) > 0
        dyn_keywords = get_dynamic_keywords()
        has_suspicious_scripts = any(keyword in soup.get_text().lower() for keyword in dyn_keywords)
        external_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http') and not urlparse(a['href']).netloc.endswith(urlparse(url).netloc)]

        return {
            'title': title[:200],
            'description': description[:500],
            'has_iframe': has_iframe,
            'has_suspicious_scripts': has_suspicious_scripts,
            'external_links_count': len(external_links),
            'response_time': response.elapsed.total_seconds(),
            'status_code': response.status_code
        }
    except Exception as e:
        logging.warning(f"Gagal deep analysis {url}: {e}")
        return {
            'title': 'Error',
            'description': 'Error',
            'has_iframe': False,
            'has_suspicious_scripts': False,
            'external_links_count': 0,
            'response_time': 0,
            'status_code': 0
        }

def setup_selenium_driver():
    """Setup Selenium driver dengan optimasi dan seleniumwire untuk analisis request."""
    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1366,768')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        seleniumwire_options = {
            'disable_encoding': True,
            'ignore_http_methods': ['OPTIONS']
        }

        # Selenium 4+: set page load strategy via options
        try:
            options.page_load_strategy = 'eager'
        except Exception:
            pass

        driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        driver.set_page_load_timeout(15)
        driver.set_script_timeout(10)
        return driver
    except Exception as e:
        logging.error(f"Gagal setup Selenium driver: {e}")
        return None

#fitur josjis peningkatan 1:
def crawl_and_analyze_graph(domain, max_pages=40, scan_id=None):
    """
    Mencrawl domain untuk membangun graf jaringan internal
    dan menganalisisnya untuk menemukan Unlinked Pages & klaster terisolasi.
    """
    logging.info(f"Memulai pemetaan graf untuk {domain} (maks {max_pages} halaman)...")
    driver = setup_selenium_driver()
    if not driver:
        logging.error("Gagal memulai driver untuk analisis graf.")
        return {}

    # Gunakan DiGraph (Directed Graph) karena link memiliki arah
    G = nx.DiGraph()
    homepage = f"https://{domain}"
    homepage_normalized = homepage.rstrip('/') # Normalisasi homepage

    to_visit = [homepage]
    visited = set()

    G.add_node(homepage_normalized) # Tambahkan homepage sebagai node akar

   # --- Tulis progres awal ke cache ---
    if scan_id:
        progress_data = {
            'status': 'PROCESSING',
            'phase': 'Crawling',
            'current': 0,
            'total': max_pages,
            'message': f"Memulai crawler untuk {domain}..."
        }
        cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
    # --- Selesai ---

    try:
        while to_visit and len(visited) < max_pages:
            # --- Tulis progres di dalam loop ---
            if scan_id and len(visited) % 5 == 0: # Update setiap 5 halaman
                progress_data = {
                    'status': 'PROCESSING',
                    'phase': 'Crawling',
                    'current': len(visited),
                    'total': max_pages,
                    'message': f"Mencrawl halaman {len(visited)} dari {max_pages}..."
                }
                cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
            # --- Selesai ---
            current_url = to_visit.pop(0)

            # Normalisasi URL
            current_url_normalized = current_url.split('#')[0].rstrip('/')

            if current_url_normalized in visited:
                continue
            visited.add(current_url_normalized)
            # --- PERUBAHAN DI SINI ---
            # LAPORKAN PROGRES SEBELUM MENCOBA MEMBUKA HALAMAN
            if scan_id:
                progress_data = {
                    'status': 'PROCESSING',
                    'phase': 'Crawling',
                    'current': len(visited),
                    'total': max_pages,
                    'message': f"Mencrawl halaman {len(visited)}/{max_pages}: {current_url_normalized}"
                }
                cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
            # --- BATAS PERUBAHAN ---
            try:
                driver.get(current_url_normalized)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                # Gagal mengakses, lewati halaman ini
                logging.warning(f"Gagal mengakses {current_url_normalized}: {e}")
                continue

            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    # Buat URL absolut dan normalisasi
                    abs_url = urljoin(current_url_normalized, href)
                    abs_url_normalized = abs_url.split('#')[0].rstrip('/')

                    # Pastikan link tersebut adalah internal (milik domain)
                    if is_url_from_domain(abs_url_normalized, domain, include_subdomains=True):
                        # Tambahkan node dan edge (link) ke graf
                        G.add_node(abs_url_normalized)
                        G.add_edge(current_url_normalized, abs_url_normalized)

                        if abs_url_normalized not in visited and abs_url_normalized not in to_visit:
                            to_visit.append(abs_url_normalized)
                except:
                    continue # Abaikan link yang rusak


    finally:
        driver.quit()

    # --- TAHAP ANALISIS GRAF ---
    logging.info("Selesai memetakan. Memulai analisis graf...")
    analysis_results = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'orphan_pages': [],
        'isolated_clusters': []
    }

    # 1. Analisis Unlinked Pages (Orphan Pages)
    # Cari node yang memiliki 0 link masuk (in-degree == 0)
    # Kita juga harus mengecualikan homepage itu sendiri
    for node in G.nodes:
        if node == homepage_normalized:
            continue

        if G.in_degree(node) == 0:
            analysis_results['orphan_pages'].append(node)

    # 2. Analisis Klaster Terisolasi
    # Kita gunakan versi "Undirected" dari graf untuk menemukan "connected components"
    # Ini akan menemukan grup-grup halaman yang saling terhubung
    U = G.to_undirected()

    # Iterasi melalui semua komponen (klaster) yang terhubung
    for component in nx.connected_components(U):
        # 'component' adalah sebuah set dari node-node (halaman)

        # Jika homepage TIDAK ADA di dalam klaster ini,
        # berarti klaster ini TERPUTUS dari situs utama.
        if homepage_normalized not in component:
            # Ini adalah klaster terisolasi!
            analysis_results['isolated_clusters'].append(list(component))

    logging.info("Analisis graf selesai.")
    return analysis_results

def calculate_entropy(text):
    """Menghitung entropy (keteracakan) dari sebuah teks."""
    if not text:
        return 0
    from collections import Counter
    entropy = 0
    length = len(text)
    counts = Counter(text)
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def analyze_js_behavior(driver, page_source, target_domain):
    """
    Menganalisis request jaringan dan konten skrip untuk perilaku berbahaya.
    Enhanced version with lower thresholds and more patterns.
    """
    analysis = {
        'suspicious_requests': [],
        'high_entropy_scripts': [],
        'dangerous_patterns': []
    }
    
    # Lower entropy threshold untuk lebih sensitif
    entropy_threshold = 3.5  # Lowered from 4.5
    minification_threshold = 100  # Scripts > 100 chars with few spaces
    
    # Enhanced dangerous patterns
    dangerous_patterns = [
        (r'eval\s*\(', 'eval() function'),
        (r'atob\s*\(', 'Base64 decoding'),
        (r'document\.write\s*\(', 'Dynamic content injection'),
        (r'String\.fromCharCode\s*\(', 'Character code obfuscation'),
        (r'exec\s*\(', 'Code execution'),
        (r'Function\s*\(', 'Dynamic function creation'),
        (r'setTimeout\s*\(.*["\'].*eval', 'Timed eval execution'),
        (r'setInterval\s*\(.*["\'].*eval', 'Repeated eval execution'),
        (r'unescape\s*\(', 'String unescaping'),
        (r'decodeURIComponent\s*\(', 'URI decoding'),
        (r'\.substr\s*\(.*\)\s*\+\s*\.substr', 'String splitting obfuscation'),
        (r'\\x[0-9a-fA-F]{2}', 'Hex encoding'),
        (r'\\u[0-9a-fA-F]{4}', 'Unicode encoding'),
    ]
    
    # 1. Analisis Request Jaringan (dari selenium-wire)
    for request in driver.requests:
        if request.response:
            try:
                # Cek apakah request ke domain eksternal
                domain = urlparse(request.url).netloc
                if target_domain not in domain and domain not in SAFE_DOMAINS:
                    # Check for tracking/beacon patterns
                    if any(kw in request.url.lower() for kw in ['track', 'beacon', 'pixel', 'telemetry', 'analytics']):
                        analysis['suspicious_requests'].append({
                            'url': request.url,
                            'status_code': request.response.status_code,
                            'content_type': request.response.headers.get('Content-Type'),
                            'reason': 'Tracking/beacon to unknown domain'
                        })
                    else:
                        # Standard suspicious request
                        analysis['suspicious_requests'].append({
                            'url': request.url,
                            'status_code': request.response.status_code,
                            'content_type': request.response.headers.get('Content-Type')
                        })
                    
                    # Cek apakah responsnya sendiri berisi keyword berbahaya
                    content_type = str(request.response.headers.get('Content-Type', ''))
                    if 'javascript' in content_type or 'json' in content_type:
                        try:
                            body = request.response.body.decode('utf-8', errors='ignore')
                            dyn_keywords = get_dynamic_keywords()
                            if any(kw in body.lower() for kw in dyn_keywords):
                                analysis['dangerous_patterns'].append({
                                    'pattern': f"Payload berbahaya dari: {request.url}",
                                    'type': 'network_payload'
                                })
                        except:
                            pass

            except Exception:
                continue # Lanjut jika ada error decoding
                
    # 2. Analisis Skrip In-Page (dari page_source)
    soup = BeautifulSoup(page_source, 'html.parser')
    for script_tag in soup.find_all('script'):
        script_content = script_tag.string
        src = script_tag.get('src', '')
        
        # Check external scripts first
        if src:
            parsed_src = urlparse(src)
            if parsed_src.netloc and target_domain not in parsed_src.netloc:
                if not any(safe_domain in src for safe_domain in SAFE_DOMAINS):
                    analysis['suspicious_requests'].append({
                        'url': src,
                        'reason': 'External script from unknown domain',
                        'type': 'script_load'
                    })
        
        if script_content:
            # Cek Entropy (lowered threshold)
            entropy = calculate_entropy(script_content)
            if entropy > entropy_threshold:
                analysis['high_entropy_scripts'].append({
                    'entropy': round(entropy, 2),
                    'preview': script_content[:100] + '...'
                })
            
            # Cek semua pola berbahaya
            for pattern, description in dangerous_patterns:
                if re.search(pattern, script_content, re.IGNORECASE):
                    analysis['dangerous_patterns'].append({
                        'pattern': description,
                        'type': 'code_pattern',
                        'preview': script_content[:100] + '...'
                    })
            
            # Cek minification (obfuscated code)
            if len(script_content) > minification_threshold:
                space_ratio = script_content.count(' ') / len(script_content)
                if space_ratio < 0.05:  # Less than 5% spaces
                    analysis['dangerous_patterns'].append({
                        'pattern': 'Heavily minified/obfuscated code detected',
                        'type': 'obfuscation',
                        'space_ratio': round(space_ratio, 3)
                    })

    return analysis
# --- KELAS VALIDATOR ---

class ImprovedContentValidator:
    def __init__(self):
        # Keyword patterns untuk flexible matching
        self.keyword_patterns = {
            'slot': ['slot', 'slots', 'slot online', 'game slot'],
            'judi': ['judi', 'judi online', 'taruhan', 'betting'],
            'gacor': ['gacor', 'gacorr', 'gacor hari ini'],
            'pulsa': ['pulsa', 'deposit pulsa', 'pulsa telkomsel'],
            'bokep': ['bokep', 'video dewasa', 'film porno', 'xxx']
        }

    def verify_content_with_selenium(self, url: str, cache_data: dict, driver) -> dict:
        """
        Verifikasi konten menggunakan Selenium untuk mendapatkan halaman yang sudah dirender.
        Ini adalah metode utama untuk melawan cloaking.
        """
        result = {
            'url': url,
            'is_accessible': False,
            'semantic_match': 'low',
            'keywords_match_score': 0,
            'title_similarity': 0,
            'content_similarity': 0,
            'malicious_confirmed': False,
            'match_reason': '',
            'error': None
        }

        try:
            # LANGKAH 1: Gunakan driver yang sudah ada untuk mendapatkan halaman
            driver.get(url)
            # Tunggu hingga halaman (body) dimuat, ini penting untuk SPA atau halaman dengan banyak JS
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # LANGKAH 2: Ambil konten SETELAH dirender oleh browser
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # LANGKAH 2.5: Analisis JavaScript behavior
            target_domain = urlparse(url).netloc
            result['js_analysis'] = analyze_js_behavior(driver, page_source, target_domain)

            # Jika kita berhasil sampai sini, halaman dianggap bisa diakses
            result['is_accessible'] = True

            # LANGKAH 3: Ekstrak konten dari 'soup' hasil Selenium (BUKAN requests)
            live_title_tag = soup.find('title')
            live_title_text = live_title_tag.get_text().strip() if live_title_tag else ''
            live_content = self._extract_main_content(soup)

            # Cache data dari Google
            cache_title = cache_data.get('title', '')
            cache_snippet = cache_data.get('snippet', '')

            # Lakukan perbandingan
            comparison = self._comprehensive_comparison(
                cache_title, cache_snippet,
                live_title_text, live_content
            )
            result.update(comparison)

            # Set verification_status based on results
            if result['malicious_confirmed']:
                result['verification_status'] = 'live_malicious'
            elif result['semantic_match'] == 'high':
                result['verification_status'] = 'live_malicious'
            elif result['semantic_match'] == 'medium':
                result['verification_status'] = 'cache_only'
            else:
                result['verification_status'] = 'clean'

        except Exception as e:
            result['error'] = f"Selenium verification error: {str(e)}"
            result['is_accessible'] = False
            result['verification_status'] = 'clean'  # Default if error

        return result

    def _comprehensive_comparison(self, cache_title, cache_snippet, live_title, live_content):
        cache_text = f"{cache_title} {cache_snippet}".lower()
        live_text = f"{live_title} {live_content}".lower()
        keyword_score = self._calculate_keyword_match_score(cache_text, live_text)
        title_similarity = self._improved_similarity(cache_title, live_title)
        content_similarity = self._improved_similarity(cache_snippet, live_content[:500])
        malicious_confirmed = self._detect_malicious_content(live_text)
        semantic_match = self._determine_semantic_match(
            keyword_score, title_similarity, content_similarity, malicious_confirmed
        )
        return {
            'keywords_match_score': keyword_score,
            'title_similarity': title_similarity,
            'content_similarity': content_similarity,
            'malicious_confirmed': malicious_confirmed,
            'semantic_match': semantic_match
        }

    def _calculate_keyword_match_score(self, cache_text, live_text):
        score = 0
        max_score = len(self.keyword_patterns)
        for category, patterns in self.keyword_patterns.items():
            cache_has_keyword = any(pattern in cache_text for pattern in patterns)
            live_has_keyword = any(pattern in live_text for pattern in patterns)
            if cache_has_keyword and live_has_keyword:
                score += 1
            elif live_has_keyword:
                score += 0.5
        return score / max_score if max_score > 0 else 0

    def _detect_malicious_content(self, live_text):
        live_text_lower = live_text.lower()
        dyn_keywords = get_dynamic_keywords()
        malicious_keywords_found = [kw for kw in dyn_keywords if kw in live_text_lower]
        if len(malicious_keywords_found) >= 2:
            return True
        malicious_patterns = [r'slot.*gacor', r'judi.*online', r'deposit.*pulsa', r'bokep.*online', r'togel.*hari.*ini']
        for pattern in malicious_patterns:
            if re.search(pattern, live_text_lower):
                return True
        return False

    def _improved_similarity(self, text1, text2):
        if not text1 or not text2: return 0.0
        text1_clean = self._preprocess_text(text1)
        text2_clean = self._preprocess_text(text2)
        if not text1_clean or not text2_clean: return 0.0
        words1 = set(re.findall(r'\w+', text1_clean))
        words2 = set(re.findall(r'\w+', text2_clean))
        if not words1 or not words2: return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        base_similarity = len(intersection) / len(union) if union else 0.0
        common_keywords = intersection.intersection(set([kw for patterns in self.keyword_patterns.values() for kw in patterns]))
        if common_keywords:
            base_similarity += len(common_keywords) * 0.1
        return min(1.0, base_similarity)

    def _preprocess_text(self, text):
        if not text: return ""
        text = text.lower()
        text = ' '.join(text.split())
        replacements = {'yg': 'yang', 'dg': 'dengan', 'sdh': 'sudah', 'tdk': 'tidak', 'gk': 'tidak', 'ga': 'tidak'}
        for short, long in replacements.items():
            text = text.replace(short, long)
        return text

    def _determine_semantic_match(self, keyword_score, title_sim, content_sim, malicious_confirmed):
        """
        Improved semantic match determination with better thresholds
        """
        if malicious_confirmed:
            return 'high'

        # More lenient scoring for better detection
        total_score = (keyword_score * 0.5) + (title_sim * 0.25) + (content_sim * 0.25)

        # Lower thresholds to catch more potential matches
        if total_score >= 0.6:
            return 'high'
        elif total_score >= 0.3:
            return 'medium'
        else:
            return 'low'

    def _extract_main_content(self, soup):
        """Extract main content from page"""
        content_selectors = [
            'article',
            'main',
            '.content',
            '#content',
            '.main-content',
            '.post-content',
            '.entry-content',
            'section',
            '.article-content'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 100:
                    return text

        # Fallback to body text
        body = soup.find('body')
        return body.get_text(strip=True) if body else ''

class SimpleContentValidator:
    """Validator sederhana: cek langsung di source code halaman"""

    def verify_live_vs_cache(self, url: str, cache_data: dict, driver) -> dict:
        """
        Verifikasi sederhana:
        - Buka URL live dengan Selenium
        - Cek keyword di page source (seperti Ctrl+U)
        - Bandingkan dengan cache Google
        """
        result = {
            'url': url,
            'is_accessible': False,
            'live_has_keywords': False,
            'cache_has_keywords': False,
            'verification_status': 'unknown',  # 'live_malicious', 'cache_only', 'clean'
            'keywords_found_live': [],
            'keywords_found_cache': [],
            'match_level': 'low',
            'error': None
        }
        result['js_analysis'] = {} # Tambahkan key baru

        try:
            # Step 1: Cek keyword di cache Google
            cache_title = cache_data.get('title', '').lower()
            cache_snippet = cache_data.get('snippet', '').lower()
            cache_text = f"{cache_title} {cache_snippet}"

            cache_keywords = []
            for keyword in MALICIOUS_KEYWORDS:
                if keyword.lower() in cache_text:
                    cache_keywords.append(keyword)

            result['cache_has_keywords'] = len(cache_keywords) > 0
            result['keywords_found_cache'] = cache_keywords
            if hasattr(driver, 'requests'):
                del driver.requests # Hapus request lama

            # Step 2: Buka URL live dan cek source code
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Tunggu sebentar untuk memastikan JavaScript loaded
            time.sleep(3)

            # Ambil page source (seperti Ctrl+U)
            page_source = driver.page_source
            page_source_lower = page_source.lower()

            # Cek keyword di source code
            live_keywords = []
            for keyword in MALICIOUS_KEYWORDS:
                if keyword.lower() in page_source_lower:
                    live_keywords.append(keyword)

            result['is_accessible'] = True
            result['live_has_keywords'] = len(live_keywords) > 0
            result['keywords_found_live'] = live_keywords


            # Step 3: Tentukan status berdasarkan perbandingan
            if result['live_has_keywords'] and result['cache_has_keywords']:
                result['verification_status'] = 'live_malicious'
                result['match_level'] = 'high'
            elif result['live_has_keywords'] and not result['cache_has_keywords']:
                result['verification_status'] = 'live_malicious'  # Baru muncul di live
                result['match_level'] = 'high'
            elif not result['live_has_keywords'] and result['cache_has_keywords']:
                result['verification_status'] = 'cache_only'  # Kemungkinan cloaking
                result['match_level'] = 'medium'
            else:
                result['verification_status'] = 'clean'
                result['match_level'] = 'low'
            # === TAMBAHAN ANALISIS JS ===
            try:
                target_domain = urlparse(url).netloc
                # Panggil fungsi analisis JS yang baru kita buat
                result['js_analysis'] = analyze_js_behavior(driver, page_source, target_domain)
            except Exception as e:
                result['js_analysis'] = {'error': f'Gagal analisis JS: {str(e)}'}
            # ============================

        except Exception as e:
            result['error'] = f"Verification failed: {str(e)}"
            # Jika gagal akses live, anggap hanya cache
            if result['cache_has_keywords']:
                result['verification_status'] = 'cache_only'
                result['match_level'] = 'low'

        return result

# --- FUNGSI HELPER SCANNER ---

def domain_intelligence(domain):
    """Analisis informasi domain"""
    try:
        w = whois.whois(domain)

        creation_date = w.creation_date
        expiration_date = w.expiration_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        creation_str = creation_date.strftime("%Y-%m-%d") if creation_date else "Unknown"
        expiration_str = expiration_date.strftime("%Y-%m-%d") if expiration_date else "Unknown"

        info = {
            'creation_date': creation_str,
            'expiration_date': expiration_str,
            'registrar': str(w.registrar) if w.registrar else "Unknown",
            'name_servers': [str(ns) for ns in w.name_servers] if w.name_servers else [],
            'status': str(w.status) if w.status else "Unknown",
            'emails': [str(email) for email in w.emails] if w.emails else []
        }

        if creation_date:
            age_days = (datetime.now() - creation_date).days
            info['age_days'] = age_days
            if age_days < 30:
                info['red_flag'] = 'new_domain'

        # Add blacklist check
        blacklist_results = cached_blacklist_check(domain)
        info['blacklist_check'] = blacklist_results

        return info
    except Exception as e:
        return {'error': str(e)}

def domain_crawler(domain, max_pages=50):
    """Crawler khusus untuk menemukan lebih banyak halaman dalam domain"""
    driver = setup_selenium_driver()
    if not driver:
        return []
    
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        try:
            rp.read()
        except:
            logging.warning(f"Robots.txt tidak dapat diakses untuk {domain}")
        
        visited = set()
        to_visit = [f"https://{domain}"]
        suspicious_pages = []
        
        while to_visit and len(visited) < max_pages:
            if not to_visit:
                break

            url = to_visit.pop(0)
            if url in visited:
                continue

            if not rp.can_fetch("*", url) if rp else True:
                continue

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and domain in href and href not in visited and href not in to_visit:
                            to_visit.append(href)
                    except:
                        continue

                page_content = driver.page_source.lower()
                dyn_keywords = get_dynamic_keywords()
                if any(keyword in page_content for keyword in dyn_keywords):
                    soup = BeautifulSoup(page_content, 'html.parser')
                    title = soup.find('title')
                    suspicious_pages.append({
                        "url": url,
                        "title": title.get_text() if title else "No Title",
                        "snippet": soup.get_text()[:200] + "..." if soup.get_text() else "No content",
                        "source": "crawler"
                    })

                visited.add(url)
                logging.info(f"Crawled {len(visited)}/{max_pages} pages...")

            except Exception as e:
                continue
                
        return suspicious_pages
        
    finally:
        driver.quit()

def search_multiple_sources(domain, primary_key, fallback_key=None, enable_bing=None):
    """
    Multi-source intelligence gathering: Google, Bing, DuckDuckGo
    dengan fallback API key dan error handling yang robust.
    OPTIMIZED: Bing disabled by default untuk hemat quota.
    """
    # Ambil konfigurasi dari database
    config = get_system_config()
    
    all_results = []

    # Google Search (primary)
    google_results = search_google(domain, primary_key, fallback_key)
    all_results.extend(google_results)

    # Bing Search (secondary) - Check dari config
    if enable_bing is None:
        enable_bing = config.enable_bing_search if config else False
    
    if enable_bing:
        try:
            bing_results = search_bing(domain, primary_key)
            all_results.extend(bing_results)
        except Exception as e:
            logging.warning(f"Bing search failed: {e}")
    else:
        logging.info("Bing search disabled untuk hemat quota SerpAPI")

    # DuckDuckGo Search (tertiary - no API key needed) - Check dari config
    enable_ddg = config.enable_duckduckgo_search if config else True
    if enable_ddg:
        try:
            ddg_results = search_duckduckgo(domain)
            all_results.extend(ddg_results)
        except Exception as e:
            logging.warning(f"DuckDuckGo search failed: {e}")
    else:
        logging.info("DuckDuckGo search disabled")

    # Deduplicate berdasarkan URL
    unique_results = []
    seen_urls = set()
    for result in all_results:
        url = result.get('url')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    logging.info(f"Total unique results from all sources: {len(unique_results)}")
    return unique_results

def get_system_config():
    """Ambil konfigurasi sistem dari database."""
    try:
        from .models import SistemConfig
        return SistemConfig.get_active_config()
    except Exception as e:
        logging.warning(f"Failed to load system config from DB: {e}. Using defaults.")
        return None

def search_google(domain, primary_key, fallback_key, use_cache=None):
    """
    Mencari di Google dengan logika fallback API Key dan penanganan error yang robust.
    Optimized untuk mengurangi penggunaan quota API.
    """
    # Ambil konfigurasi dari database
    config = get_system_config()
    
    # Set defaults jika tidak ada config
    if use_cache is None:
        use_cache = config.enable_api_cache if config else True
    
    # Get cache TTL from config
    cache_ttl_days = config.api_cache_ttl_days if config else 7
    cache_ttl_seconds = cache_ttl_days * 24 * 3600
    
    use_comprehensive = config.use_comprehensive_query if config else True
    max_results = config.max_search_results if config else 100
    
    # Opsimasi: Gabungkan query menjadi lebih sedikit untuk hemat quota
    if use_comprehensive:
        # Query comprehensive untuk semua konten ilegal dalam satu search
        # ENHANCED: Added inurl: queries to catch URLs with keywords in path/params
        queries = [
            f'site:{domain} ("slot gacor" OR "situs judi" OR "deposit pulsa" OR "judi online" OR "casino" OR "poker" OR "togel" OR "gambling" OR "bokep" OR "video dewasa" OR "nonton film dewasa" OR "porn" OR "hacked" OR "defaced" OR "deface")',
            f'inurl:"bokep" site:{domain}',  # Catch URLs with bokep in path/params
            f'inurl:"gacor" site:{domain}',  # Catch URLs with gacor in path/params
            f'inurl:"slot" site:{domain}',   # Catch slot URLs
        ]
    else:
        # Fallback ke query terpisah (mode lama)
        queries = [
            f'site:{domain} "slot gacor" OR "situs judi" OR "deposit pulsa" OR "judi online"',
            f'site:{domain} "bokep" OR "video dewasa" OR "nonton film dewasa" OR "porn"',
            f'site:{domain} "hacked" OR "defaced" OR "deface" OR "hack"',
            f'site:{domain} "casino" OR "poker" OR "togel" OR "gambling"',
            f'inurl:"bokep" site:{domain}',
            f'inurl:"gacor" site:{domain}',
            f'inurl:"slot" site:{domain}'
        ]

    all_results_list = [] # Ganti nama variabel agar tidak bentrok
    unique_links = set()
    current_key = primary_key
    using_fallback = False # Tandai jika sedang pakai fallback

    for i, query in enumerate(queries):
        logging.info(f"Mencari query: '{query}' menggunakan key {'fallback' if using_fallback else 'utama'}")
        
        # Cek cache dulu jika enabled
        if use_cache:
            cached_result = get_cached_search_result(query, 'google')
            if cached_result:
                # cached_result berisi dict dengan key 'result'
                results_dict = cached_result.get('result') if isinstance(cached_result, dict) else cached_result
                if isinstance(results_dict, dict):
                    organic_results = results_dict.get('organic_results', [])
                    for result in organic_results:
                        if not isinstance(result, dict):
                            continue
                        link = result.get('link')
                        if link and link not in unique_links:
                            unique_links.add(link)
                            all_results_list.append({
                                "url": link,
                                "title": result.get('title', 'No Title'),
                                "snippet": result.get('snippet', 'No snippet'),
                                "source": f"google_query_{i+1}_cached"
                            })
                    continue  # Skip API call jika sudah ada di cache
        
        attempt_successful = False
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": current_key,
                "num": max_results  # Dinamis dari konfigurasi sistem
            }

            search = GoogleSearch(params)
            # 1. Dapatkan dictionary hasil UTAMA
            results_dict = search.get_dict()

            if 'error' in results_dict:
                logging.error(f"SerpApi error (utama) for query '{query}': {results_dict['error']}")
                raise Exception(results_dict['error'])

            # 2. Ekstrak organic_results UTAMA
            organic_results = results_dict.get('organic_results', [])
            logging.info(f"Ditemukan {len(organic_results)} hasil organik (utama) untuk query '{query}'")

            for result in organic_results:
                if not isinstance(result, dict):
                    logging.warning(f"Format hasil tidak terduga (utama, bukan dict) dilewati: {result}")
                    continue

                link = result.get('link')
                if link and link not in unique_links:
                    unique_links.add(link)
                    all_results_list.append({ # Tambahkan ke list yang benar
                        "url": link,
                        "title": result.get('title', 'No Title'),
                        "snippet": result.get('snippet', 'No snippet'),
                        "source": f"google_query_{i+1}{'_fallback' if using_fallback else ''}"
                    })
            attempt_successful = True # Percobaan utama berhasil
            
            # Cache hasil untuk query berikutnya dengan TTL dari config
            if use_cache and not using_fallback:
                set_cached_search_result(query, results_dict, 'google', ttl=cache_ttl_seconds)

        except Exception as e:
            error_message = str(e).lower()
            logging.error(f"Exception (utama) saat memproses query '{query}': {e}")

            # --- Logika Fallback ---
            # Hanya coba fallback jika percobaan utama GAGAL TOTAL (attempt_successful = False)
            # dan BUKAN karena kita SUDAH pakai fallback
            if not attempt_successful and not using_fallback and fallback_key is not None and \
               ("quota" in error_message or "forbidden" in error_message or "invalid api key" in error_message):

                logging.warning(f"API Key utama bermasalah ({error_message}). Mencoba fallback untuk query '{query}'")
                current_key = fallback_key
                using_fallback = True # Set flag bahwa kita pakai fallback

                try:
                    # Coba lagi query dengan key fallback
                    params["api_key"] = current_key
                    search_fallback = GoogleSearch(params)
                    # 3. Dapatkan dictionary hasil FALLBACK
                    retry_results_dict = search_fallback.get_dict()

                    if 'error' in retry_results_dict:
                        logging.error(f"SerpApi error (fallback) for query '{query}': {retry_results_dict['error']}")
                        raise Exception(retry_results_dict['error'])

                    # 4. Ekstrak organic_results FALLBACK
                    retry_results = retry_results_dict.get('organic_results', [])
                    logging.info(f"Ditemukan {len(retry_results)} hasil organik (fallback) untuk query '{query}'")

                    for result_retry in retry_results: # Gunakan nama variabel berbeda
                        if not isinstance(result_retry, dict):
                            logging.warning(f"Format hasil tidak terduga (fallback, bukan dict) dilewati: {result_retry}")
                            continue

                        link_retry = result_retry.get('link')
                        if link_retry and link_retry not in unique_links:
                            unique_links.add(link_retry)
                            all_results_list.append({ # Tambahkan ke list yang benar
                                "url": link_retry,
                                "title": result_retry.get('title', 'No Title'),
                                "snippet": result_retry.get('snippet', 'No snippet'),
                                "source": f"google_query_{i+1}_fallback" # Tandai sebagai fallback
                            })
                    # Jika sampai sini, percobaan fallback berhasil
                    attempt_successful = True
                    
                    # Cache hasil fallback juga dengan TTL dari config
                    if use_cache:
                        set_cached_search_result(query, retry_results_dict, 'google', ttl=cache_ttl_seconds)

                except Exception as e2:
                    # Error terjadi bahkan saat fallback
                    logging.error(f"Fallback gagal total untuk query '{query}'. Error: {e2}")

            # Jika error BUKAN karena API key ATAU fallback sudah dicoba/tidak ada
            elif not attempt_successful:
                 logging.error(f"Gagal memproses query '{query}' setelah penanganan awal. Error: {e}")

            # Reset flag fallback untuk query berikutnya jika perlu
            if using_fallback and attempt_successful:
                 using_fallback = False # Kembali ke key utama jika fallback berhasil
                 current_key = primary_key # Reset key ke utama untuk query selanjutnya

    logging.info(f"Total hasil unik ditemukan: {len(all_results_list)}")
    return all_results_list # Kembalikan list yang benar

def search_bing(domain, api_key):
    """Search menggunakan Bing Web Search API"""
    from serpapi.google_search import GoogleSearch  # Menggunakan SerpApi yang sama untuk Bing

    queries = [
        f'site:{domain} slot gacor OR situs judi OR deposit pulsa',
        f'site:{domain} bokep OR video dewasa OR porn',
        f'site:{domain} hacked OR defaced OR casino'
    ]

    results = []
    unique_links = set()

    for i, query in enumerate(queries):
        try:
            params = {
                "engine": "bing",
                "q": query,
                "api_key": api_key,
                "num": 30
            }

            search = GoogleSearch(params)
            search_results = search.get_dict()
            organic_results = search_results.get('organic_results', [])

            for result in organic_results:
                link = result.get('link')
                if link and link not in unique_links:
                    unique_links.add(link)
                    results.append({
                        "url": link,
                        "title": result.get('title', 'No Title'),
                        "snippet": result.get('snippet', 'No snippet'),
                        "source": f"bing_query_{i+1}"
                    })

        except Exception as e:
            logging.warning(f"Bing search failed for query '{query}': {e}")
            continue

    logging.info(f"Bing search found {len(results)} results")
    return results

def search_duckduckgo(domain):
    """Search menggunakan DuckDuckGo (HTML scraping - no API key needed)"""
    import requests
    from bs4 import BeautifulSoup

    queries = [
        f'site:{domain} slot gacor OR judi online',
        f'site:{domain} bokep OR porn',
        f'site:{domain} hacked OR casino'
    ]

    results = []
    unique_links = set()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for i, query in enumerate(queries):
        try:
            url = f"https://duckduckgo.com/html/?q={query}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            for result in soup.find_all('a', class_='result__url'):
                href = result.get('href')
                if href and domain in href and href not in unique_links:
                    unique_links.add(href)

                    # Get title and snippet
                    title_elem = result.find_previous('h2', class_='result__title')
                    title = title_elem.get_text() if title_elem else 'No Title'

                    snippet_elem = result.find_next('a', class_='result__snippet')
                    snippet = snippet_elem.get_text() if snippet_elem else 'No snippet'

                    results.append({
                        "url": href,
                        "title": title,
                        "snippet": snippet,
                        "source": f"duckduckgo_query_{i+1}"
                    })

        except Exception as e:
            logging.warning(f"DuckDuckGo search failed for query '{query}': {e}")
            continue

    logging.info(f"DuckDuckGo search found {len(results)} results")
    return results

def deep_analysis(url):
    """Mengunjungi URL dan menganalisis konten HTML-nya secara mendalam dengan illegal content detection."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, timeout=15, headers=headers, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style", "meta", "link"]):
            script.extract()
        
        page_text = soup.get_text().lower()
        
        keywords_found = {}
        dyn_keywords = get_dynamic_keywords()
        for keyword in dyn_keywords:
            count = page_text.count(keyword)
            if count > 0:
                keywords_found[keyword] = int(count)
        
        suspicious_links = []
        scam_domains = ["sbobet", "judi", "poker", "casino", "togel", "slot", "bokep", "porn", "xxx"]
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(scam_domain in href for scam_domain in scam_domains):
                suspicious_links.append({
                    "url": href,
                    "text": link.get_text(strip=True)[:50]
                })
        
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content.lower()
        
        redirect_history = [resp.url for resp in response.history]
        
        # Integrasi illegal content detection - check dari config
        illegal_detection = {}
        config = get_system_config()
        enable_illegal = config.enable_illegal_content_detection if config else True
        
        if enable_illegal:
            try:
                from .illegal_content_detector import IllegalContentDetector
                detector = IllegalContentDetector()
                illegal_detection = detector.detect_illegal_content(response.text, url)
                
                # Tambahkan struktur analisis halaman
                structure_analysis = detector.analyze_page_structure(response.text, url)
                illegal_detection['structure_analysis'] = structure_analysis
            except Exception as e:
                logging.warning(f"Error in illegal content detection: {e}")
                illegal_detection = {"error": str(e)}
        
        return {
            "status": "success",
            "keywords_found": keywords_found,
            "suspicious_links": suspicious_links[:10],
            "meta_tags": meta_tags,
            "redirects": redirect_history,
            "content_length": int(len(response.text)),
            "response_time": float(response.elapsed.total_seconds()),
            "illegal_content_detection": illegal_detection  # Tambahkan hasil deteksi konten ilegal
        }

    except Exception as e:
        return {"status": "error", "message": f"Gagal mengakses URL: {str(e)}"}

def analyze_backlinks(domain, primary_key):
    """Analisis backlink untuk menemukan pola mencurigakan"""
    try:
        params = {
            "engine": "google_search",
            "q": f"link:{domain}",
            "api_key": primary_key,
            "num": 50
        }
        
        search = GoogleSearch(params)
        results = search.get_dict().get('organic_results', [])
        
        suspicious_backlinks = []
        for result in results:
            link = result.get('link')
            link_domain = urlparse(link).netloc.lower() if link else ''
            
            scam_indicators = ['casino', 'porn', 'gambling', 'judi', 'slot', 'bokep']
            if any(indicator in link_domain for indicator in scam_indicators):
                suspicious_backlinks.append({
                    "url": link,
                    "title": result.get('title'),
                    "domain": link_domain
                })
        
        return suspicious_backlinks
    except Exception as e:
        return []

# --- FUNGSI KESIMPULAN ---

def generate_final_conclusion(scan_results):
    """
    Hasilkan kesimpulan akhir berdasarkan kombinasi
    hasil kompleks dan verifikasi sederhana
    """
    if not scan_results or 'categories' not in scan_results:
        return {
            'status': 'TIDAK DIKENAL',
            'color': 'gray',
            'message': 'Tidak ada data hasil scan',
            'risk_score': 0,
            'stats': {
                'total': 0,
                'live_malicious': 0,
                'cache_only': 0,
                'clean': 0
            }
        }

    total_pages = scan_results.get('total_pages', 0)
    live_malicious_count = 0
    cache_only_count = 0
    clean_count = 0

    # Hitung berdasarkan kategori
    for category in scan_results['categories'].values():
        for item in category['items']:
            verification = item.get('verification', {})
            if verification.get('verification_status') == 'live_malicious':
                live_malicious_count += 1
            elif verification.get('verification_status') == 'cache_only':
                cache_only_count += 1
            else:
                clean_count += 1

    # Hitung risk score berdasarkan konfirmasi live
    # Beri bobot tinggi untuk live malicious, sedang untuk cache only
    risk_score = min(100, (live_malicious_count * 40) + (cache_only_count * 15))

    # Tentukan status akhir
    if live_malicious_count > 0:
        status = "TIDAK AMAN"
        color = "red"
        message = f"🚨 Ditemukan {live_malicious_count} halaman berbahaya yang terkonfirmasi live"
    elif cache_only_count > 3:
        status = "PERLU PERHATIAN"
        color = "orange"
        message = f"⚠️ Terdapat {cache_only_count} halaman mencurigakan di cache Google (kemungkinan cloaking)"
    else:
        status = "AMAN"
        color = "green"
        message = "✅ Domain bersih dari konten berbahaya yang terkonfirmasi live"

    return {
        'status': status,
        'color': color,
        'message': message,
        'risk_score': risk_score,
        'stats': {
            'total': total_pages,
            'live_malicious': live_malicious_count,
            'cache_only': cache_only_count,
            'clean': clean_count
        }
    }


# --- FUNGSI UTAMA SCANNER ---

def perform_verified_scan(domain, primary_api_key, fallback_api_key, scan_type, enable_backlink, model, label_mapping, enable_verification=True, show_all_results=False, scan_id=None): # <-- UBAH DI SINI
    """Enhanced scanning dengan manajemen driver Selenium yang efisien."""

    domain_info = cached_domain_intelligence(domain)

    # Enumerasi subdomain
    subdomain_results = enumerate_subdomains(domain, primary_api_key, fallback_api_key)

    # Initial progress
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Subdomain',
            'message': f"Enumerasi subdomain selesai: {subdomain_results.get('total_subdomains', 0)} ditemukan"
        }, timeout=3600)

    # Scan konten subdomain yang ditemukan (untuk mendeteksi domain pornografi/judi asli)
    # Ambil konfigurasi dari database
    config = get_system_config()
    ENABLE_SUBDOMAIN_CONTENT_SCAN = config.enable_subdomain_content_scan if config else False
    max_subdomains_to_scan_config = config.max_subdomains_to_scan if config else 10
    
    subdomain_content_results = []
    active_subdomains = [sd for sd in subdomain_results.get('subdomains', []) if sd.get('status') == 'active']
    
    if active_subdomains:
        if not ENABLE_SUBDOMAIN_CONTENT_SCAN:
            logging.info(f"Subdomain content scanning disabled. Ditemukan {len(active_subdomains)} subdomain aktif (hemat quota SerpAPI)")
        else:
            if scan_id:
                cache.set(f'scan_progress_{scan_id}', {
                    'status': 'PROCESSING',
                    'phase': 'Subdomain Scan',
                    'message': f"Memindai konten {len(active_subdomains)} subdomain aktif..."
                }, timeout=3600)
            
            logging.info(f"Memulai scan konten untuk {len(active_subdomains)} subdomain aktif")
            
            # Limit jumlah subdomain yang di-scan untuk menghindari timeout
            max_subdomains_to_scan = min(10, len(active_subdomains))  # Maksimal 10 subdomain
            
            for idx, subdomain_info in enumerate(active_subdomains[:max_subdomains_to_scan]):
                subdomain = subdomain_info.get('subdomain')
                if not subdomain:
                    continue
                
                try:
                    # Scan konten subdomain
                    subdomain_results_list = scan_subdomain_content(
                        subdomain, 
                        primary_api_key, 
                        fallback_api_key, 
                        model, 
                        label_mapping, 
                        enable_verification
                    )
                    subdomain_content_results.extend(subdomain_results_list)
                    
                    if scan_id and idx % 2 == 0:  # Update progress setiap 2 subdomain
                        cache.set(f'scan_progress_{scan_id}', {
                            'status': 'PROCESSING',
                            'phase': 'Subdomain Scan',
                            'current': idx + 1,
                            'total': max_subdomains_to_scan,
                            'message': f"Memindai subdomain {idx + 1}/{max_subdomains_to_scan}: {subdomain}"
                        }, timeout=3600)
                        
                    logging.info(f"Scan subdomain {idx + 1}/{max_subdomains_to_scan}: {subdomain} - {len(subdomain_results_list)} hasil")
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logging.error(f"Error scanning subdomain {subdomain}: {e}", exc_info=True)
                    continue
            
            logging.info(f"Scan subdomain selesai. Total hasil ditemukan: {len(subdomain_content_results)}")

    # Gunakan multi-source search untuk mendapatkan lebih banyak hasil
    if scan_type == "Komprehensif (Google + Crawling)":
        all_results = search_multiple_sources(domain, primary_api_key, fallback_api_key)
    else:
        # Untuk scan cepat, tetap gunakan Google saja
        all_results = search_google(domain, primary_api_key, fallback_api_key)
    
    # Gabungkan hasil subdomain dengan hasil domain utama
    if subdomain_content_results:
        logging.info(f"Menggabungkan {len(subdomain_content_results)} hasil dari subdomain ke hasil utama")
        all_results.extend(subdomain_content_results)

    crawled_results = []
    graph_analysis = {} # <-- BUAT VARIABEL BARU
    unindexed_pages = [] # <-- BUAT VARIABEL UNTUK HALAMAN TIDAK TERINDEX
    
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Search',
            'message': 'Mengumpulkan hasil dari mesin pencari...'
        }, timeout=3600)

    if scan_type == "Komprehensif (Google + Crawling)":
        # Get config (already loaded earlier)
        
        # sitemap-based candidates
        if config and config.enable_sitemap_analysis:
            try:
                if scan_id:
                    cache.set(f'scan_progress_{scan_id}', {
                        'status': 'PROCESSING',
                        'phase': 'Sitemap',
                        'message': 'Mengambil sitemap...'
                    }, timeout=3600)
                sitemap_urls = extract_urls_from_sitemap(domain)
                crawled_results.extend([{ 'url': u, 'title': 'Sitemap URL', 'snippet': '', 'source': 'sitemap' } for u in sitemap_urls[:100]])
            except Exception:
                pass
        
        # fast async crawler (requests-first)
        if config and config.enable_deep_crawling:
            try:
                if scan_id:
                    cache.set(f'scan_progress_{scan_id}', {
                        'status': 'PROCESSING',
                        'phase': 'FastCrawl',
                        'message': 'Melakukan crawling cepat...'
                    }, timeout=3600)
                max_crawl = config.max_crawl_pages if config else 50
                crawled_results_fast = crawl_domain_fast(domain, max_pages=max_crawl)
                crawled_results.extend(crawled_results_fast)
            except Exception as e:
                logging.warning(f"Fast crawler failed: {e}")
        
        # Graph analysis
        if config and config.enable_graph_analysis:
            logging.info("Starting comprehensive graph analysis (crawler)...")
            try:
                max_crawl = config.max_crawl_pages if config else 50
                graph_analysis = crawl_and_analyze_graph(domain, max_pages=max_crawl, scan_id=scan_id)
            except Exception as e:
                logging.error(f"Analisis graf internal gagal: {str(e)}")
                graph_analysis = {'error': str(e)}
        
        # Discovery halaman tidak terindex Google untuk menemukan konten ilegal tersembunyi
        if config and config.enable_unindexed_discovery:
            try:
                if scan_id:
                    cache.set(f'scan_progress_{scan_id}', {
                        'status': 'PROCESSING',
                        'phase': 'Unindexed Discovery',
                        'message': 'Mencari halaman tidak terindex dengan konten ilegal...'
                    }, timeout=3600)
                
                logging.info("Memulai discovery halaman tidak terindex untuk konten ilegal...")
                unindexed_pages = discover_unindexed_pages(domain, primary_api_key, fallback_api_key, scan_id=scan_id)
                
                if unindexed_pages:
                    logging.info(f"Ditemukan {len(unindexed_pages)} halaman tidak terindex dengan konten ilegal")
                    # Tambahkan ke all_results
                    all_results.extend(unindexed_pages)
            except Exception as e:
                logging.error(f"Error in unindexed pages discovery: {e}", exc_info=True)
                unindexed_pages = []
    
    backlinks = []
    if enable_backlink or (config and config.enable_backlink_analysis):
        backlinks = analyze_backlinks(domain, primary_api_key)

    # Gabungkan hasil dari multi-source dengan crawled results dan dedup
    all_results = deduplicate_results(all_results + crawled_results)
    
    # Extract subdomains dari URL yang ditemukan dalam hasil scan
    # Ini penting untuk menemukan subdomain yang tidak terdeteksi oleh teknik enumerasi sebelumnya
    extracted_subdomains_from_urls = set()
    for result in all_results:
        url = result.get('url') or result.get('link') or ''
        if url:
            try:
                parsed = urlparse(url)
                netloc = parsed.netloc.lower()
                if netloc and netloc != domain:
                    # Extract subdomain menggunakan tldextract untuk akurasi lebih baik
                    # Contoh: publikasiilmiah.unwahas.ac.id -> publikasiilmiah.unwahas.ac.id
                    extracted = tldextract.extract(netloc)
                    extracted_domain = tldextract.extract(domain.lower())
                    
                    # Bandingkan domain dan suffix
                    if extracted.domain == extracted_domain.domain and extracted.suffix == extracted_domain.suffix:
                        # Jika ada subdomain, tambahkan ke set
                        if extracted.subdomain:
                            # Reconstruct full subdomain
                            subdomain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
                            if subdomain != domain and subdomain not in extracted_subdomains_from_urls:
                                extracted_subdomains_from_urls.add(subdomain)
                                logging.info(f"Ditemukan subdomain dari URL hasil scan: {subdomain}")
                        # Jika netloc sama dengan domain (tanpa subdomain), skip
            except Exception as e:
                logging.debug(f"Error extracting subdomain from URL {url}: {e}")
                continue
    
    # Tambahkan subdomain yang ditemukan dari URL ke subdomain_results
    if extracted_subdomains_from_urls:
        logging.info(f"Menambahkan {len(extracted_subdomains_from_urls)} subdomain dari URL hasil scan ke daftar subdomain")
        existing_subdomains = {sd['subdomain'] for sd in subdomain_results.get('subdomains', [])}
        
        for subdomain in extracted_subdomains_from_urls:
            if subdomain not in existing_subdomains:
                try:
                    # Validasi DNS untuk subdomain yang baru ditemukan
                    ip = socket.gethostbyname(subdomain)
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': ip,
                        'status': 'active'
                    })
                    logging.info(f"Menambahkan subdomain baru dari URL: {subdomain} (IP: {ip})")
                except socket.gaierror:
                    # Jika tidak bisa resolve, tetap sertakan tapi mark sebagai inactive
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': None,
                        'status': 'inactive'
                    })
                    logging.info(f"Menambahkan subdomain baru dari URL (inactive): {subdomain}")
                except Exception as e:
                    logging.debug(f"Error validating subdomain {subdomain}: {e}")
                    # Tetap tambahkan meskipun validasi gagal
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': None,
                        'status': 'unknown'
                    })
        
        # Update total subdomains count
        subdomain_results['total_subdomains'] = len(subdomain_results['subdomains'])
        logging.info(f"Total subdomain setelah menambahkan dari URL: {subdomain_results['total_subdomains']}")

    if not all_results:
        return {"status": "clean", "message": "Tidak ditemukan hasil"}

    reverse_mapping = {v: k for k, v in label_mapping.items()} if label_mapping else {}

    categories = {label_code: {"name": label_name.replace("_", " ").title(), "items": []}
                  for label_code, label_name in reverse_mapping.items() if label_name != 'aman'}

    verified_categories = {}

    # --- MANAJEMEN DRIVER DIMULAI DI SINI ---
    driver = None
    if enable_verification:
        driver = setup_selenium_driver()
        if not driver:
            logging.error("Gagal memulai Selenium Driver. Verifikasi real-time tidak dapat dilakukan.")
            enable_verification = False

    # Inisialisasi validator yang ditingkatkan
    improved_validator = ImprovedContentValidator()

    # --- Tulis progres awal sebelum loop verifikasi ---
    total_to_verify = len(all_results)
    if scan_id:
        progress_data = {
            'status': 'PROCESSING',
            'phase': 'Verification',
            'current': 0,
            'total': total_to_verify,
            'message': f"Mempersiapkan verifikasi {total_to_verify} URL..."
        }
        cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
    # --- Selesai ---

    try:
        for i, result in enumerate(all_results):
            text = f"{result.get('title', '')} {result.get('snippet', '')}"

            pred = None
            if model:
                pred = model.predict([text])[0]

            keywords_found = any(keyword in text.lower() for keyword in MALICIOUS_KEYWORDS)

            if (pred and pred in categories) or keywords_found:
                if not pred:
                    # Set pred based on keywords
                    pred_label = "hack judol" # Default label
                    if "porn" in text.lower() or "bokep" in text.lower(): pred_label = "pornografi"
                    if "hacked" in text.lower() or "deface" in text.lower(): pred_label = "hacked"
                    pred = label_mapping.get(pred_label)
                # Logika untuk menampilkan hasil tanpa verifikasi (Scan Cepat)
                if not enable_verification:
                    result['deep_analysis'] = cached_deep_analysis(result['url'])
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)
                    continue # Lanjut ke item berikutnya

                # --- TIERED VERIFICATION: requests multi-UA terlebih dahulu ---
                verification_result = None
                try:
                    quick = quick_verification(result['url'], result)
                    if not enable_verification:
                        result['verification'] = {'verification_status': quick['status'], 'method': 'requests_multi_ua'}
                    elif quick['need_headless']:
                        verification_result = improved_validator.verify_content_with_selenium(result['url'], result, driver)
                        result['verification'] = verification_result
                    else:
                        result['verification'] = {'verification_status': quick['status'], 'method': 'requests_multi_ua'}
                except Exception as e:
                    logging.warning(f"Quick verification failed, fallback to headless: {e}")
                    if enable_verification and driver:
                        verification_result = improved_validator.verify_content_with_selenium(result['url'], result, driver)
                        result['verification'] = verification_result
                    else:
                        result['verification'] = {'verification_status': 'clean', 'error': str(e)}

                # Tetap lakukan deep analysis untuk informasi tambahan
                result['deep_analysis'] = cached_deep_analysis(result['url'])

                # Tentukan apakah akan menampilkan hasil berdasarkan status verifikasi
                # Jika show_all_results=True, tampilkan semua hasil prediksi malicious
                if show_all_results:
                    # Mode show all: tampilkan semua hasil prediksi malicious
                    result['deep_analysis'] = cached_deep_analysis(result['url'])
                    result['verification'] = verification_result
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)
                elif verification_result['verification_status'] in ['live_malicious', 'cache_only']:
                    # Mode strict: hanya tampilkan yang terverifikasi
                    result['deep_analysis'] = cached_deep_analysis(result['url'])
                    result['verification'] = verification_result
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)

            # --- Tulis progres di dalam loop verifikasi ---
            if scan_id:
                progress_data = {
                    'status': 'PROCESSING',
                    'phase': 'Verification',
                    'current': i + 1,
                    'total': total_to_verify,
                    'message': f"Memverifikasi URL {i + 1} dari {total_to_verify}..."
                }
                cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
            # --- Selesai ---
            logging.info(f"Memverifikasi URL {i + 1}/{len(all_results)}")
            time.sleep(0.1)

    finally:
        # --- PASTIKAN DRIVER SELALU DITUTUP ---
        if driver:
            driver.quit()
            # --- Tulis status Selesai ---
    if scan_id:
        progress_data = {
            'status': 'COMPLETED',
            'phase': 'Done',
            'current': total_to_verify,
            'total': total_to_verify,
            'message': f"Scan Selesai."
        }
        cache.set(f'scan_progress_{scan_id}', progress_data, timeout=3600)
    # --- Selesai ---

    final_conclusion = generate_final_conclusion({
        'categories': verified_categories,
        'total_pages': len(all_results)
    })

    return {
        'categories': verified_categories,
        'domain_info': domain_info,
        'backlinks': backlinks,
        'total_pages': len(all_results),
        'verified_scan': enable_verification,
        'graph_analysis': graph_analysis, # <-- TAMBAHKAN HASIL GRAF DI SINI
        'subdomain_results': subdomain_results,
        'unindexed_pages': unindexed_pages if 'unindexed_pages' in locals() else [], # <-- TAMBAHKAN HALAMAN TIDAK TERINDEX
        'final_conclusion': final_conclusion
    }


def perform_native_scan(domain, primary_api_key, fallback_api_key, scan_type, enable_backlink, model, label_mapping, enable_verification=True, scan_id=None, max_seconds: int = 1200):
    """Scan flow yang mengikuti sistem 'sistem-nativ' (lebih sederhana dan deterministik)."""
    start_time = time.time()
    # Domain intelligence
    domain_info = domain_intelligence(domain)
    
    # Enumerasi subdomain
    subdomain_results = enumerate_subdomains(domain, primary_api_key, fallback_api_key)
    
    # Progress: Subdomain enumeration
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Subdomain',
            'message': f"Enumerasi subdomain selesai: {subdomain_results.get('total_subdomains', 0)} ditemukan"
        }, timeout=3600)

    # Scan konten subdomain yang ditemukan (untuk mendeteksi domain pornografi/judi asli)
    # Ambil konfigurasi dari database
    config = get_system_config()
    ENABLE_SUBDOMAIN_CONTENT_SCAN = config.enable_subdomain_content_scan if config else False
    max_subdomains_to_scan_config = config.max_subdomains_to_scan if config else 10
    
    subdomain_content_results = []
    active_subdomains = [sd for sd in subdomain_results.get('subdomains', []) if sd.get('status') == 'active']
    
    if active_subdomains:
        if not ENABLE_SUBDOMAIN_CONTENT_SCAN:
            logging.info(f"Subdomain content scanning disabled (hemat quota SerpAPI)")
        elif time.time() - start_time < max_seconds * 0.8:  # Hanya scan subdomain jika masih ada waktu
            if scan_id:
                cache.set(f'scan_progress_{scan_id}', {
                    'status': 'PROCESSING',
                    'phase': 'Subdomain Scan',
                    'message': f"Memindai konten {len(active_subdomains)} subdomain aktif..."
                }, timeout=3600)
            
            logging.info(f"Memulai scan konten untuk {len(active_subdomains)} subdomain aktif")
            
            # Limit jumlah subdomain yang di-scan untuk menghindari timeout
            max_subdomains_to_scan = min(max_subdomains_to_scan_config, len(active_subdomains))
            
            for idx, subdomain_info in enumerate(active_subdomains[:max_subdomains_to_scan]):
                # Cek waktu tersisa
                if time.time() - start_time > max_seconds * 0.85:
                    logging.warning(f"Waktu terbatas, menghentikan scan subdomain setelah {idx} subdomain")
                    break
                
                subdomain = subdomain_info.get('subdomain')
                if not subdomain:
                    continue
                
                try:
                    # Scan konten subdomain
                    subdomain_results_list = scan_subdomain_content(
                        subdomain, 
                        primary_api_key, 
                        fallback_api_key, 
                        model, 
                        label_mapping, 
                        enable_verification
                    )
                    subdomain_content_results.extend(subdomain_results_list)
                    
                    if scan_id and idx % 2 == 0:  # Update progress setiap 2 subdomain
                        cache.set(f'scan_progress_{scan_id}', {
                            'status': 'PROCESSING',
                            'phase': 'Subdomain Scan',
                            'current': idx + 1,
                            'total': max_subdomains_to_scan,
                            'message': f"Memindai subdomain {idx + 1}/{max_subdomains_to_scan}: {subdomain}"
                        }, timeout=3600)
                        
                    logging.info(f"Scan subdomain {idx + 1}/{max_subdomains_to_scan}: {subdomain} - {len(subdomain_results_list)} hasil")
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logging.error(f"Error scanning subdomain {subdomain}: {e}", exc_info=True)
                    continue
            
            logging.info(f"Scan subdomain selesai. Total hasil ditemukan: {len(subdomain_content_results)}")

    # Progress: Search
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Search',
            'message': 'Mengambil hasil Google untuk domain utama...'
        }, timeout=3600)

    # Hanya Google (utama + fallback)
    google_results = search_google(domain, primary_api_key, fallback_api_key)
    
    # Gabungkan hasil subdomain dengan hasil domain utama
    if subdomain_content_results:
        logging.info(f"Menggabungkan {len(subdomain_content_results)} hasil dari subdomain ke hasil utama")
        google_results.extend(subdomain_content_results)

    crawled_results = []
    graph_analysis = {}
    config = get_system_config()  # Get config for native scan
    
    if scan_type == "Komprehensif (Google + Crawling)":
        if scan_id:
            cache.set(f'scan_progress_{scan_id}', {
                'status': 'PROCESSING',
                'phase': 'Crawling',
                'message': 'Crawling domain (Selenium)...'
            }, timeout=3600)
        # Skip crawling if time budget already tight
        if time.time() - start_time < max_seconds * 0.6 and (config and config.enable_deep_crawling):
            max_crawl = config.max_crawl_pages if config else 30
            crawled_results = domain_crawler(domain, max_pages=max_crawl)
        try:
            # Only run graph analysis if time budget still ok
            if time.time() - start_time < max_seconds * 0.75 and (config and config.enable_graph_analysis):
                max_crawl = config.max_crawl_pages if config else 50
                graph_analysis = crawl_and_analyze_graph(domain, max_pages=max_crawl, scan_id=scan_id)
        except Exception as e:
            logging.error(f"Analisis graf internal gagal: {str(e)}")
            graph_analysis = {'error': str(e)}
        
        # Discovery halaman tidak terindex jika masih ada waktu
        try:
            if time.time() - start_time < max_seconds * 0.85 and (config and config.enable_unindexed_discovery):
                if scan_id:
                    cache.set(f'scan_progress_{scan_id}', {
                        'status': 'PROCESSING',
                        'phase': 'Unindexed Discovery',
                        'message': 'Mencari halaman tidak terindex dengan konten ilegal...'
                    }, timeout=3600)
                
                logging.info("Memulai discovery halaman tidak terindex untuk konten ilegal (native mode)...")
                unindexed_pages = discover_unindexed_pages(domain, primary_api_key, fallback_api_key, scan_id=scan_id)
                
                if unindexed_pages:
                    logging.info(f"Ditemukan {len(unindexed_pages)} halaman tidak terindex dengan konten ilegal")
                    # Tambahkan ke google_results
                    google_results.extend(unindexed_pages)
        except Exception as e:
            logging.error(f"Error in unindexed pages discovery (native): {e}", exc_info=True)
            unindexed_pages = []

    all_results = google_results + crawled_results
    
    # Extract subdomains dari URL yang ditemukan dalam hasil scan
    # Ini penting untuk menemukan subdomain yang tidak terdeteksi oleh teknik enumerasi sebelumnya
    extracted_subdomains_from_urls = set()
    for result in all_results:
        url = result.get('url') or result.get('link') or ''
        if url:
            try:
                parsed = urlparse(url)
                netloc = parsed.netloc.lower()
                if netloc and netloc != domain:
                    # Extract subdomain menggunakan tldextract untuk akurasi lebih baik
                    # Contoh: publikasiilmiah.unwahas.ac.id -> publikasiilmiah.unwahas.ac.id
                    extracted = tldextract.extract(netloc)
                    extracted_domain = tldextract.extract(domain.lower())
                    
                    # Bandingkan domain dan suffix
                    if extracted.domain == extracted_domain.domain and extracted.suffix == extracted_domain.suffix:
                        # Jika ada subdomain, tambahkan ke set
                        if extracted.subdomain:
                            # Reconstruct full subdomain
                            subdomain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
                            if subdomain != domain and subdomain not in extracted_subdomains_from_urls:
                                extracted_subdomains_from_urls.add(subdomain)
                                logging.info(f"Ditemukan subdomain dari URL hasil scan: {subdomain}")
                        # Jika netloc sama dengan domain (tanpa subdomain), skip
            except Exception as e:
                logging.debug(f"Error extracting subdomain from URL {url}: {e}")
                continue
    
    # Tambahkan subdomain yang ditemukan dari URL ke subdomain_results
    if extracted_subdomains_from_urls:
        logging.info(f"Menambahkan {len(extracted_subdomains_from_urls)} subdomain dari URL hasil scan ke daftar subdomain")
        existing_subdomains = {sd['subdomain'] for sd in subdomain_results.get('subdomains', [])}
        
        for subdomain in extracted_subdomains_from_urls:
            if subdomain not in existing_subdomains:
                try:
                    # Validasi DNS untuk subdomain yang baru ditemukan
                    ip = socket.gethostbyname(subdomain)
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': ip,
                        'status': 'active'
                    })
                    logging.info(f"Menambahkan subdomain baru dari URL: {subdomain} (IP: {ip})")
                except socket.gaierror:
                    # Jika tidak bisa resolve, tetap sertakan tapi mark sebagai inactive
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': None,
                        'status': 'inactive'
                    })
                    logging.info(f"Menambahkan subdomain baru dari URL (inactive): {subdomain}")
                except Exception as e:
                    logging.debug(f"Error validating subdomain {subdomain}: {e}")
                    # Tetap tambahkan meskipun validasi gagal
                    subdomain_results['subdomains'].append({
                        'subdomain': subdomain,
                        'ip': None,
                        'status': 'unknown'
                    })
        
        # Update total subdomains count
        subdomain_results['total_subdomains'] = len(subdomain_results['subdomains'])
        logging.info(f"Total subdomain setelah menambahkan dari URL: {subdomain_results['total_subdomains']}")
    
    if not all_results:
        return {"status": "clean", "message": "Tidak ditemukan hasil", 'domain_info': domain_info}

    reverse_mapping = {v: k for k, v in label_mapping.items()} if label_mapping else {}
    categories = {label_code: {"name": label_name.replace("_", " ").title(), "items": []}
                  for label_code, label_name in reverse_mapping.items() if label_name != 'aman'}

    verified_categories = {}
    driver = None
    if enable_verification:
        driver = setup_selenium_driver()
        if not driver:
            logging.error("Gagal memulai Selenium Driver. Verifikasi real-time tidak dapat dilakukan.")
            enable_verification = False

    simple_validator = SimpleContentValidator()

    total_to_verify = len(all_results)
    if scan_id:
        cache.set(f'scan_progress_{scan_id}', {
            'status': 'PROCESSING',
            'phase': 'Verification',
            'current': 0,
            'total': total_to_verify,
            'message': f"Memulai verifikasi {total_to_verify} URL..."
        }, timeout=3600)

    timed_out = False
    try:
        for i, result in enumerate(all_results):
            # Enforce max duration
            if time.time() - start_time > max_seconds:
                timed_out = True
                break
            text = f"{result.get('title', '')} {result.get('snippet', '')}"

            pred = None
            if model:
                pred = model.predict([text])[0]
            else:
                # fallback label berdasar keyword sederhana
                text_l = text.lower()
                pred_label = None
                if any(k in text_l for k in ['porn', 'bokep', 'xxx']):
                    pred_label = 'pornografi'
                elif any(k in text_l for k in ['hacked', 'deface', 'defaced']):
                    pred_label = 'hacked'
                elif any(k in text_l for k in ['judi', 'togel', 'casino', 'slot', 'gacor']):
                    pred_label = 'hack judol'
                if pred_label:
                    pred = label_mapping.get(pred_label)

            if pred and pred in categories:
                if not enable_verification:
                    result['deep_analysis'] = deep_analysis(result['url'])
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)
                else:
                    verification_result = simple_validator.verify_live_vs_cache(result['url'], result, driver)
                    result['deep_analysis'] = deep_analysis(result['url'])
                    result['verification'] = verification_result
                    if verification_result['verification_status'] in ['live_malicious', 'cache_only']:
                        if pred not in verified_categories:
                            verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                        verified_categories[pred]["items"].append(result)

            if scan_id:
                cache.set(f'scan_progress_{scan_id}', {
                    'status': 'PROCESSING',
                    'phase': 'Verification',
                    'current': i + 1,
                    'total': total_to_verify,
                    'message': f"Memverifikasi URL {i + 1} dari {total_to_verify}..."
                }, timeout=3600)
            logging.info(f"Memverifikasi URL {i + 1}/{len(all_results)}")
            time.sleep(0.1)

    finally:
        if driver:
            driver.quit()

    final_conclusion = generate_final_conclusion({
        'categories': verified_categories,
        'total_pages': len(all_results)
    })

    return {
        'categories': verified_categories,
        'domain_info': domain_info,
        'backlinks': [],
        'total_pages': len(all_results),
        'verified_scan': enable_verification,
        'graph_analysis': graph_analysis,
        'subdomain_results': subdomain_results,  # Add subdomain results to return
        'unindexed_pages': unindexed_pages if 'unindexed_pages' in locals() else [], # <-- TAMBAHKAN HALAMAN TIDAK TERINDEX
        'final_conclusion': final_conclusion,
        'timed_out': timed_out
    }