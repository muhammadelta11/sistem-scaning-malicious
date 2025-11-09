#Berisi semua logika inti untuk pemindaian, validasi, dan analisis.

import streamlit as st
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

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import konstanta dari config.py
from config import MALICIOUS_KEYWORDS
SAFE_DOMAINS = [
    'google-analytics.com', 'googletagmanager.com', 'cdnjs.cloudflare.com',
    'bootstrapcdn.com', 'jquery.com', 'gstatic.com'
]

warnings.filterwarnings('ignore')

#fitur josjis peningkatan 1:
def crawl_and_analyze_graph(domain, max_pages=50):
    """
    Mencrawl domain untuk membangun graf jaringan internal
    dan menganalisisnya untuk menemukan Unlinked Pages & klaster terisolasi.
    """
    st.info(f"Memulai pemetaan graf untuk {domain} (maks {max_pages} halaman)...")
    driver = setup_selenium_driver()
    if not driver:
        st.error("Gagal memulai driver untuk analisis graf.")
        return {}

    # Gunakan DiGraph (Directed Graph) karena link memiliki arah
    G = nx.DiGraph()
    homepage = f"https://{domain}"
    homepage_normalized = homepage.rstrip('/') # Normalisasi homepage

    to_visit = [homepage]
    visited = set()

    G.add_node(homepage_normalized) # Tambahkan homepage sebagai node akar

    progress_bar = st.progress(0, text="Memetakan struktur domain...")

    try:
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            
            # Normalisasi URL
            current_url_normalized = current_url.split('#')[0].rstrip('/')
            
            if current_url_normalized in visited:
                continue
            
            visited.add(current_url_normalized)

            try:
                driver.get(current_url_normalized)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                # Gagal mengakses, lewati halaman ini
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
                    if domain in urlparse(abs_url_normalized).netloc:
                        # Tambahkan node dan edge (link) ke graf
                        G.add_node(abs_url_normalized)
                        G.add_edge(current_url_normalized, abs_url_normalized)
                        
                        if abs_url_normalized not in visited and abs_url_normalized not in to_visit:
                            to_visit.append(abs_url_normalized)
                except:
                    continue # Abaikan link yang rusak
            
            progress_bar.progress(len(visited) / max_pages, text=f"Memetakan {len(visited)}/{max_pages} halaman...")

    finally:
        driver.quit()
        progress_bar.empty()

    
    # --- TAHAP ANALISIS GRAF ---
    st.info("Selesai memetakan. Memulai analisis graf...")
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

    st.success("Analisis graf selesai.")
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
    Menganalisis request jaringan dan konten skrip
    untuk perilaku berbahaya.
    """
    analysis = {
        'suspicious_requests': [],
        'high_entropy_scripts': [],
        'dangerous_patterns': []
    }
    
    # 1. Analisis Request Jaringan (dari selenium-wire)
    for request in driver.requests:
        if request.response:
            try:
                # Cek apakah request ke domain eksternal
                domain = urlparse(request.url).netloc
                if target_domain not in domain and domain not in SAFE_DOMAINS:
                    # Ini adalah request ke domain pihak ketiga yang tidak dikenal
                    analysis['suspicious_requests'].append({
                        'url': request.url,
                        'status_code': request.response.status_code,
                        'content_type': request.response.headers.get('Content-Type')
                    })
                    
                    # Cek apakah responsnya sendiri berisi keyword berbahaya
                    if 'javascript' in str(request.response.headers.get('Content-Type')) or \
                       'json' in str(request.response.headers.get('Content-Type')):
                        
                        body = request.response.body.decode('utf-8', errors='ignore')
                        if any(kw in body.lower() for kw in MALICIOUS_KEYWORDS):
                            analysis['dangerous_patterns'].append(f"Payload berbahaya dari: {request.url}")

            except Exception:
                continue # Lanjut jika ada error decoding
                
    # 2. Analisis Skrip In-Page (dari page_source)
    soup = BeautifulSoup(page_source, 'html.parser')
    for script_tag in soup.find_all('script'):
        script_content = script_tag.string
        if script_content:
            # Cek Entropy
            entropy = calculate_entropy(script_content)
            if entropy > 4.5: # Threshold entropy (bisa disesuaikan)
                analysis['high_entropy_scripts'].append({
                    'entropy': entropy,
                    'preview': script_content[:100] + '...'
                })
            
            # Cek Pola Berbahaya
            if re.search(r'eval\(|atob\(|document\.write\(|String\.fromCharCode', script_content):
                analysis['dangerous_patterns'].append(f"Pola berbahaya ditemukan: {script_content[:100]}...")

    return analysis
# --- KELAS VALIDATOR ---

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
            del driver.requests # Hapus request lama

            # Step 2: Buka URL live dan cek source code
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Tunggu sebentar untuk memastikan JavaScript loaded
            time.sleep(3)

            # Ambil page source (seperti Ctrl+U)
            # page_source = driver.page_source.lower()
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

def setup_selenium_driver():
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    seleniumwire_options = {
        'disable_encoding': True,  # Untuk bisa membaca response body
        'ignore_http_methods': ['OPTIONS'] # Abaikan request yang tidak perlu
    }
    try:
        driver = webdriver.Chrome(
            options=chrome_options,
            seleniumwire_options=seleniumwire_options
        ) # <-- GANTI DI SINI
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        st.warning(f"Selenium tidak dapat diinisialisasi: {e}")
        return None

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
            st.warning(f"Robots.txt tidak dapat diakses untuk {domain}")
        
        visited = set()
        to_visit = [f"https://{domain}"]
        suspicious_pages = []
        
        progress_bar = st.progress(0, text="Crawling domain...")
        
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
                if any(keyword in page_content for keyword in MALICIOUS_KEYWORDS):
                    soup = BeautifulSoup(page_content, 'html.parser')
                    title = soup.find('title')
                    suspicious_pages.append({
                        "url": url,
                        "title": title.get_text() if title else "No Title",
                        "snippet": soup.get_text()[:200] + "..." if soup.get_text() else "No content",
                        "source": "crawler"
                    })
                
                visited.add(url)
                progress_bar.progress(len(visited)/max_pages, text=f"Crawled {len(visited)} pages...")
                
            except Exception as e:
                continue
                
        return suspicious_pages
        
    finally:
        driver.quit()

def search_google(domain, primary_key, fallback_key):
    """
    Mencari di Google dengan logika fallback API Key dan penanganan error yang robust.
    """
    queries = [
        f'site:{domain} "slot gacor" OR "situs judi" OR "deposit pulsa" OR "judi online"',
        f'site:{domain} "bokep" OR "video dewasa" OR "nonton film dewasa" OR "porn"',
        f'site:{domain} "hacked" OR "defaced" OR "deface" OR "hack"',
        f'site:{domain} "casino" OR "poker" OR "togel" OR "gambling"'
    ]

    all_results_list = [] # Ganti nama variabel agar tidak bentrok
    unique_links = set()
    current_key = primary_key
    using_fallback = False # Tandai jika sedang pakai fallback

    for i, query in enumerate(queries):
        logging.info(f"Mencari query: '{query}' menggunakan key {'fallback' if using_fallback else 'utama'}")
        attempt_successful = False
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": current_key,
                "num": 20
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

        except Exception as e:
            error_message = str(e).lower()
            logging.error(f"Exception (utama) saat memproses query '{query}': {e}")

            # --- Logika Fallback ---
            # Hanya coba fallback jika percobaan utama GAGAL TOTAL (attempt_successful = False)
            # dan BUKAN karena kita SUDAH pakai fallback
            if not attempt_successful and not using_fallback and fallback_key is not None and \
               ("quota" in error_message or "forbidden" in error_message or "invalid api key" in error_message):

                st.warning(f"API Key utama bermasalah ({error_message}). Mencoba fallback...")
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

                except Exception as e2:
                    # Error terjadi bahkan saat fallback
                    st.error(f"Fallback gagal: Query '{query}' gagal dengan kedua API Key. Error: {e2}")
                    logging.error(f"Fallback gagal total untuk query '{query}'. Error: {e2}")
            
            # Jika error BUKAN karena API key ATAU fallback sudah dicoba/tidak ada
            elif not attempt_successful:
                 st.error(f"Gagal memproses query '{query}'. Error: {e}")
                 logging.error(f"Gagal memproses query '{query}' setelah penanganan awal. Error: {e}")
            
            # Reset flag fallback untuk query berikutnya jika perlu
            if using_fallback and attempt_successful:
                 using_fallback = False # Kembali ke key utama jika fallback berhasil
                 current_key = primary_key # Reset key ke utama untuk query selanjutnya

    logging.info(f"Total hasil unik ditemukan: {len(all_results_list)}")
    return all_results_list # Kembalikan list yang benar

def deep_analysis(url):
    """Mengunjungi URL dan menganalisis konten HTML-nya secara mendalam."""
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
        for keyword in MALICIOUS_KEYWORDS:
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
        
        return {
            "status": "success",
            "keywords_found": keywords_found,
            "suspicious_links": suspicious_links[:10],
            "meta_tags": meta_tags,
            "redirects": redirect_history,
            "content_length": int(len(response.text)),
            "response_time": float(response.elapsed.total_seconds())
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
            "num": 20
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

def perform_verified_scan(domain, primary_api_key, fallback_api_key, scan_type, enable_backlink, model, label_mapping, enable_verification=True):
    """Enhanced scanning dengan manajemen driver Selenium yang efisien."""

    domain_info = domain_intelligence(domain)
    # Kirim kedua key ke search_google
    google_results = search_google(domain, primary_api_key, fallback_api_key)

    crawled_results = []
    graph_analysis = {} # <-- BUAT VARIABEL BARU
    if scan_type == "Komprehensif (Google + Crawling)":
        crawled_results = domain_crawler(domain, max_pages=30)
        # 2. Panggil crawler & analisis graf (YANG BARU)
        try:
            # Kita set max_pages lebih banyak untuk graf agar lebih akurat
            graph_analysis = crawl_and_analyze_graph(domain, max_pages=50) 
        except Exception as e:
            st.error(f"Analisis graf internal gagal: {str(e)}")
            graph_analysis = {'error': str(e)}
    backlinks = []
    if enable_backlink:
        backlinks = analyze_backlinks(domain, primary_key)

    all_results = google_results + crawled_results

    if not all_results:
        return {"status": "clean", "message": "Tidak ditemukan hasil"}

    reverse_mapping = {v: k for k, v in label_mapping.items()} if label_mapping else {}

    categories = {label_code: {"name": label_name.replace("_", " ").title(), "items": []}
                  for label_code, label_name in reverse_mapping.items() if label_name != 'aman'}

    verified_categories = {}
    progress_bar = st.progress(0, text="Menganalisis dan memverifikasi konten...")

    # --- MANAJEMEN DRIVER DIMULAI DI SINI ---
    driver = None
    if enable_verification:
        driver = setup_selenium_driver()
        if not driver:
            st.error("Gagal memulai Selenium Driver. Verifikasi real-time tidak dapat dilakukan.")
            enable_verification = False # Matikan verifikasi jika driver gagal

    # Inisialisasi validator sederhana
    simple_validator = SimpleContentValidator()

    try:
        for i, result in enumerate(all_results):
            text = f"{result.get('title', '')} {result.get('snippet', '')}"

            pred = None
            if model:
                pred = model.predict([text])[0]
            elif any(keyword in text.lower() for keyword in MALICIOUS_KEYWORDS):
                # Fallback jika model tidak ada, prediksi berdasarkan keyword
                pred_label = "hack judol" # Default label
                if "porn" in text.lower() or "bokep" in text.lower(): pred_label = "pornografi"
                if "hacked" in text.lower() or "deface" in text.lower(): pred_label = "hacked"
                pred = label_mapping.get(pred_label)

            if pred and pred in categories:
                # Logika untuk menampilkan hasil tanpa verifikasi (Scan Cepat)
                if not enable_verification:
                    result['deep_analysis'] = deep_analysis(result['url'])
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)
                    continue # Lanjut ke item berikutnya

                # --- PROSES VERIFIKASI DENGAN SIMPLE VALIDATOR ---
                verification_result = simple_validator.verify_live_vs_cache(result['url'], result, driver)

                # Tetap lakukan deep analysis untuk informasi tambahan
                result['deep_analysis'] = deep_analysis(result['url'])
                result['verification'] = verification_result

                # Tentukan apakah akan menampilkan hasil berdasarkan status verifikasi
                # Tampilkan semua yang bukan 'clean' (jadi tampilkan live_malicious dan cache_only)
                if verification_result['verification_status'] in ['live_malicious', 'cache_only']:
                    if pred not in verified_categories:
                        verified_categories[pred] = {"name": categories[pred]["name"], "items": []}
                    verified_categories[pred]["items"].append(result)

            progress_bar.progress((i + 1) / len(all_results), text=f"Memverifikasi URL {i + 1}/{len(all_results)}")
            time.sleep(0.1)

    finally:
        # --- PASTIKAN DRIVER SELALU DITUTUP ---
        if driver:
            driver.quit()

    return {
        'categories': verified_categories,
        'domain_info': domain_info,
        'backlinks': backlinks,
        'total_pages': len(all_results),
        'verified_scan': enable_verification,
        'graph_analysis': graph_analysis # <-- TAMBAHKAN HASIL GRAF DI SINI
    }