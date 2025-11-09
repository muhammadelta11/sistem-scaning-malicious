import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Import dari file-file lokal
import data_manager
import core_scanner
from config import MALICIOUS_KEYWORDS

from passlib.context import CryptContext
import sqlite3
from datetime import datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_login():
    username = st.session_state["username_input"]
    password = st.session_state["password_input"]

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, role, organization_name, user_api_key FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        db_hash = user_data[0]
        if pwd_context.verify(password, db_hash):
            # Login Sukses!
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user_data[1]
            st.session_state["organization"] = user_data[2]
            st.session_state["user_api_key"] = user_data[3]
            log_activity(username, user_data[2], 'LOGIN_SUCCESS')
            del st.session_state["password_input"]
            del st.session_state["username_input"]
        else:
            st.error("Username atau password salah.")
            log_activity(username, 'N/A', 'LOGIN_FAIL', 'Password salah')
    else:
        st.error("Username atau password salah.")
        log_activity(username, 'N/A', 'LOGIN_FAIL', 'Username tidak ditemukan')

def create_log_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            organization_name TEXT,
            action TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Panggil fungsi ini sekali untuk membuat tabelnya
create_log_table()


# Di app.py
def log_activity(username, organization, action, details=""):
    """Mencatat aktivitas user ke database log."""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO activity_log (username, organization_name, action, details) VALUES (?, ?, ?, ?)",
            (username, organization, action, details)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Gagal mencatat log: {e}") # Log ke konsol server jika gagal
    # --- GERBANG OTENTIKASI ---
# Inisialisasi SEMUA session state di satu tempat
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "organization" not in st.session_state:
    st.session_state["organization"] = None

# --- TAMBAHKAN INI KEMBALI ---
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None
if 'scanned_domain' not in st.session_state:
    st.session_state.scanned_domain = None
if 'scan_in_progress' not in st.session_state: # <-- INI YANG MENYEBABKAN ERROR
    st.session_state.scan_in_progress = False
if 'enable_verification' not in st.session_state:
    st.session_state.enable_verification = True
# --- SELESAI PENAMBAHAN ---

# Tampilkan halaman login JIKA belum login
if not st.session_state["logged_in"]:
    st.set_page_config(
        page_title="Login - Detektor SEO Poisoning",
        page_icon="🛡️"
    )
    st.title("🛡️ Login Sistem Deteksi")
    st.write("Harap masukkan kredensial Anda untuk mengakses aplikasi.")

    st.text_input("Username:", key="username_input")
    st.text_input(
        "Password:",
        type="password",
        key="password_input",
        on_change=check_login  # Panggil check_login saat ada perubahan
    )

    st.button("Login", on_click=check_login)

    # HENTIKAN eksekusi sisa aplikasi
    st.stop()

# --- APLIKASI UTAMA (HANYA BERJALAN JIKA LOGIN BERHASIL) ---
# Kode di bawah ini hanya akan berjalan jika st.session_state["logged_in"] == True
    # Tampilkan halaman login JIKA belum login
    if not st.session_state["logged_in"]:
        st.set_page_config(
            page_title="Login - Detektor SEO Poisoning",
            page_icon="🛡️"
        )
        st.title("🛡️ Login Sistem Deteksi")
        st.write("Harap masukkan kredensial Anda untuk mengakses aplikasi.")

        st.text_input("Username:", key="username_input")
        st.text_input(
            "Password:",
            type="password",
            key="password_input",
            on_change=check_login  # Panggil check_login saat ada perubahan
        )

        st.button("Login", on_click=check_login)
        
        # HENTIKAN eksekusi sisa aplikasi
        st.stop()

# --- APLIKASI UTAMA (HANYA BERJALAN JIKA LOGIN BERHASIL) ---
# Kode di bawah ini hanya akan berjalan jika st.session_state["logged_in"] == True



# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Detektor SEO Poisoning Komprehensif",
    page_icon="🛡️",
    layout="wide"
)


# --- Muat Resources ---
model, label_mapping, ranking_data = data_manager.load_resources()
reverse_mapping = {v: k for k, v in label_mapping.items()} if label_mapping else {}

# --- Antarmuka Aplikasi ---
st.title("🛡️ Sistem Deteksi SEO Poisoning Komprehensif")
st.markdown("Deteksi konten berbahaya (**judi online, pornografi, hacked, malware**) di domain pendidikan/pemerintahan.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Pemindai Domain", 
    "📊 Dashboard Peringkat", 
    "⚙️ Konfigurasi", 
    "🛡️ Audit Log",
    "👤 Manajemen User"  # <-- TAB BARU
])
# --- TAB 1: PEMINDAI DOMAIN ---
with tab1:
    st.header("🔍 Pindai Domain dengan Verifikasi Real-Time")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        load_dotenv()
        default_api_key = os.getenv("SERPAPI_API_KEY", "")
        # api_key input hidden karena belum berfungsi dengan baik
        api_key = default_api_key  # menggunakan default dari env

        scan_type = st.selectbox(
            "Tipe Scan",
            ["Cepat (Google Only)", "Komprehensif (Google + Crawling)"],
            help="Scan komprehensif akan memakan waktu lebih lama tetapi lebih akurat"
        )

        # Toggle untuk verifikasi real-time
        enable_verification = st.checkbox(
            "Aktifkan Verifikasi Real-Time",
            value=True,
            help="Verifikasi langsung ke website target untuk mengurangi false positive"
        )
        
    with col2:
        domain_input = st.text_input(
            "Domain Target",  
            placeholder="contoh: uns.ac.id",  
            help="Masukkan domain tanpa http://"
        )
        # enable_backlink_analysis = st.checkbox("Aktifkan Analisis Backlink", value=True)
        enable_backlink_analysis = False  # disabled karena belum berfungsi dengan baik

    # Tombol scan dengan opsi verifikasi
    col_scan1, col_scan2 = st.columns([3, 1])
    
    with col_scan1:
        if st.button(
            "🔍 Mulai Pemindaian dengan Verifikasi",  
            type="primary",  
            disabled=st.session_state.scan_in_progress
                    
        ):
            admin_key = st.secrets["SERPAPI_API_KEY"] # Asumsi key admin ada di secrets
            user_key = st.session_state.get("user_api_key", None)

            api_key_to_use = admin_key # Default pakai key admin

            # Jika user punya key, prioritaskan key user
            if st.session_state.role == 'user' and user_key:
                api_key_to_use = user_key
                st.info("Menggunakan API Key pribadi Anda...")
            # Jika user tidak punya key, dia akan otomatis pakai key admin
            # Jika admin, dia akan otomatis pakai key admin
            if not all([api_key_to_use, domain_input]):
                st.warning("Harap isi API Key dan Domain")
            else:
                st.session_state.scan_in_progress = True
                st.session_state.scan_results = None  
                st.session_state.scanned_domain = domain_input
                st.session_state.enable_verification = enable_verification
            key_type_used = 'user_key' if st.session_state.role == 'user' and user_key else 'admin_key'
            log_activity(
                st.session_state['username'], 
                st.session_state['organization'], 
                'START_SCAN', 
                f"domain: {domain_input}, type: {scan_type}, key: {key_type_used}"
            )
            with st.spinner(f"Memulai scan {'dengan verifikasi ' if enable_verification else ''}untuk {domain_input}..."):
                    scan_results = core_scanner.perform_verified_scan(
                        domain_input,  
                        api_key_to_use,  # <-- Kirim key yang benar
                        admin_key,  
                        scan_type,  
                        enable_backlink_analysis,
                        model,  # <-- Kirim model
                        label_mapping, # <-- Kirim mapping
                    )
                    
                    st.session_state.scan_results = scan_results
                    st.session_state.scan_in_progress = False
                    st.rerun()
    
    with col_scan2:
        if st.button(
            "⚡ Scan Cepat (Tanpa Verifikasi)",
            disabled=st.session_state.scan_in_progress
        ):
            # Ambil key admin dari secrets, bukan os.getenv
            admin_key = st.secrets.get("SERPAPI_API_KEY", default_api_key) # Gunakan st.secrets
            user_key = st.session_state.get("user_api_key", None)
            
            api_key_to_use = admin_key # Default
            if st.session_state.role == 'user' and user_key:
                api_key_to_use = user_key
                st.info("Menggunakan API Key pribadi Anda...")  
            if not all([api_key_to_use, domain_input]):
                st.warning("Harap isi API Key dan Domain")
            else:
                st.session_state.scan_in_progress = True
                st.session_state.scan_results = None  
                st.session_state.scanned_domain = domain_input
                st.session_state.enable_verification = False
                
                # --- TAMBAHKAN LOG SCAN ---
                key_type_used = 'user_key' if st.session_state.role == 'user' and user_key else 'admin_key'
                log_activity(
                    st.session_state['username'], 
                    st.session_state['organization'], 
                    'START_SCAN_FAST', # <-- Buat log action yang berbeda
                    f"domain: {domain_input}, type: {scan_type}, key: {key_type_used}"
                )
                with st.spinner(f"Memulai scan cepat untuk {domain_input}..."):
                    scan_results = core_scanner.perform_verified_scan(
                        domain_input,  
                        api_key_to_use,  # <-- Kirim key yang benar
                        admin_key,  
                        scan_type,  
                        enable_backlink_analysis,
                        model,  # <-- Kirim model
                        label_mapping, # <-- Kirim mapping
                        enable_verification=False
                    )
                    
                    st.session_state.scan_results = scan_results
                    st.session_state.scan_in_progress = False
                    st.rerun()

    if st.session_state.scan_in_progress:
        st.warning("Scan gagal... Harap refresh kembali halaman.")

    # Tampilkan hasil scan
    if st.session_state.scan_results is not None:
        st.divider()
        
        if st.session_state.enable_verification:
            st.subheader(f"📋 Hasil Pemindaian dengan Verifikasi untuk: `{st.session_state.scanned_domain}`")
        else:
            st.subheader(f"📋 Hasil Pemindaian Cepat untuk: `{st.session_state.scanned_domain}`")
        
        if isinstance(st.session_state.scan_results, dict) and 'categories' in st.session_state.scan_results:
            results = st.session_state.scan_results
            total_dangerous = sum(len(cat_data['items']) for cat_data in results['categories'].values())
            
            # Tampilkan Summary dengan info verifikasi
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Halaman Di-scan", results['total_pages'])
            with col2:
                st.metric("Halaman Berbahaya Terkonfirmasi" if st.session_state.enable_verification else "Halaman Berbahaya",  
                          total_dangerous)
            with col3:
                st.metric("Backlink Mencurigakan", len(results['backlinks']))
            with col4:
                risk_score = min(100, total_dangerous * 10)
                st.metric("Risk Score", f"{risk_score}/100",  
                          delta="Tinggi" if risk_score > 70 else "Menengah" if risk_score > 30 else "Rendah")
            
            if st.session_state.enable_verification:
                st.info("🎯 **Scan dengan Verifikasi**: Hasil telah diverifikasi langsung dari website target")
            else:
                st.warning("⚡ **Scan Cepat**: Hasil berdasarkan cache Google, mungkin mengandung false positive")
            
            # Tampilkan Domain Info
            if results['domain_info']:
                # --- TAMPIKAN ANALISIS GRAF INTERNAL ---
                if 'graph_analysis' in results and results['graph_analysis']:
                    graph_data = results['graph_analysis']
                    if 'error' in graph_data:
                        st.error(f"Analisis Graf Gagal: {graph_data['error']}")
                    else:
                        with st.expander(f"🕸️ Analisis Graf Struktur Internal (Proaktif) - {graph_data.get('total_nodes', 0)} Halaman Terpetakan", expanded=True):
                            st.info("Mendeteksi halaman 'hantu' dan 'klaster spam' yang mungkin disembunyikan dari menu utama.")
                            
                            # Tampilkan Unlinked Pages
                            orphan_pages = graph_data.get('orphan_pages', [])
                            if orphan_pages:
                                st.warning(f"🚨 Ditemukan {len(orphan_pages)} Unlinked Pages (Orphan Pages)")
                                st.write("Halaman ini tidak memiliki link masuk dari struktur situs utama yang terdeteksi:")
                                st.dataframe(pd.DataFrame(orphan_pages, columns=["URL Unlinked Pages"]), use_container_width=True, height=200)
                            else:
                                st.success("✅ Tidak ditemukan Unlinked Pages (Orphan Pages).")
                            
                            st.divider()
                            
                            # Tampilkan Klaster Terisolasi
                            isolated_clusters = graph_data.get('isolated_clusters', [])
                            if isolated_clusters:
                                st.error(f"🔥 Ditemukan {len(isolated_clusters)} Klaster Terisolasi (Spam Cluster)!")
                                st.write("Grup halaman ini terputus dari situs utama dan saling terhubung satu sama lain (indikasi kuat spam):")
                                for i, cluster in enumerate(isolated_clusters):
                                    st.subheader(f"Klaster {i + 1} ({len(cluster)} halaman)")
                                    st.dataframe(pd.DataFrame(cluster, columns=[f"URL di Klaster {i+1}"]), use_container_width=True, height=200)
                            else:
                                st.success("✅ Tidak ditemukan Klaster Terisolasi.")
                    
                with st.expander("ℹ️ Informasi Domain"):
                    st.json(results['domain_info'])
            
            # TAMPILAN KESIMPULAN AKHIR
            st.divider()
            conclusion = core_scanner.generate_final_conclusion(st.session_state.scan_results)

            # Tampilkan banner kesimpulan
            if conclusion['color'] == 'red':
                st.error(f"## 🚨 {conclusion['status']}")
            elif conclusion['color'] == 'orange':
                st.warning(f"## ⚠️ {conclusion['status']}")
            else:
                st.success(f"## ✅ {conclusion['status']}")

            st.write(conclusion['message'])

            # Tampilkan statistik
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Halaman Di-scan", conclusion['stats']['total'])
            with col2:
                st.metric("Live Malicious", conclusion['stats']['live_malicious'])
            with col3:
                st.metric("Cache Only", conclusion['stats']['cache_only'])
            with col4:
                st.metric("Risk Score", f"{conclusion['risk_score']}/100")

            # Tampilkan detail verifikasi
            with st.expander("🔍 Detail Verifikasi", expanded=True):
                if conclusion['stats']['live_malicious'] > 0:
                    st.error(f"**{conclusion['stats']['live_malicious']} halaman** terkonfirmasi berbahaya di website live")
                if conclusion['stats']['cache_only'] > 0:
                    st.warning(f"**{conclusion['stats']['cache_only']} halaman** hanya ditemukan di cache Google (kemungkinan cloaking)")
                if conclusion['stats']['clean'] > 0:
                    st.success(f"**{conclusion['stats']['clean']} halaman** bersih dari konten berbahaya")

            # Tampilkan rekomendasi berdasarkan status
            st.subheader("🛡️ Rekomendasi")
            if conclusion['status'] == "TIDAK AMAN":
                st.write("""
                - **Segera lakukan security audit** pada halaman yang terkonfirmasi berbahaya
                - **Hapus konten malicious** dari server
                - **Periksa kerentanan** yang mungkin dimanfaatkan hacker
                - **Laporkan insiden** kepada tim IT yang berwenang
                """)
            elif conclusion['status'] == "PERLU PERHATIAN":
                st.write("""
                - **Monitor cache Google** secara berkala
                - **Lakukan pengecekan ulang** dalam beberapa hari
                - **Periksa kemungkinan cloaking** dengan tools lainnya
                - **Tingkatkan keamanan** website untuk mencegah serangan
                """)
            else:
                st.write("""
                - **Pertahankan keamanan** website dengan update rutin
                - **Lakukan scan berkala** untuk memantau adanya ancaman
                - **Backup data** secara teratur
                - **Educate users** tentang keamanan digital
                """)

            # Tampilkan Hasil per Kategori
            for cat_id, cat_data in results['categories'].items():
                if cat_data["items"]:
                    with st.expander(f"🚨 {cat_data['name']} ({len(cat_data['items'])} hasil{' terkonfirmasi' if st.session_state.enable_verification else ''})", expanded=True):
                        for item in cat_data["items"]:
                            with st.container(border=True):
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    # Tampilkan verification status jika ada
                                    if 'verification' in item:
                                        verification = item['verification']
                                        status_emoji = "✅" if verification.get('is_accessible') else "❌"
                                        match_level = verification.get('verification_status', 'unknown')

                                        st.markdown(f"**{item['title']}** {status_emoji}")

                                        if match_level == 'live_malicious':
                                            st.error("🚨 **LIVE MALICIOUS**: Konten berbahaya terkonfirmasi di website live!")
                                        elif match_level == 'cache_only':
                                            st.warning("⚠️ **CACHE ONLY**: Konten berbahaya hanya di cache Google (kemungkinan cloaking)")
                                        else:
                                            st.info("🔵 **CLEAN**: Konten bersih dari keyword berbahaya")

                                    else: # Untuk scan cepat tanpa verifikasi
                                        st.markdown(f"**{item['title']}**")

                                    st.markdown(f"🔗 [{item['url']}]({item['url']})")
                                    st.caption(item['snippet'][:200] + "..." if len(item['snippet']) > 200 else item['snippet'])

                                with col_b:
                                    if st.button("Analisis Mendalam 🔬", key=item['url'], type="secondary"):
                                        st.session_state[f"analyze_{item['url']}"] = True

                                    st.selectbox(
                                        "Validasi Label",
                                        options=list(label_mapping.keys()) if label_mapping else ["hack_judol", "pornografi", "hacked", "aman"],
                                        key=f"label_{item['url']}",
                                        help="Pilih label yang sesuai untuk data ini"
                                    )
                                    # HANYA TAMPILKAN JIKA ADMIN
                                if st.session_state.role == 'admin':
                                    if st.button("✅ Tambah ke Dataset", key=f"add_{item['url']}"):
                                        selected_label = st.session_state[f"label_{item['url']}"]
                                        if data_manager.add_to_dataset( # <-- Panggil dari data_manager
                                            url=item['url'],
                                            title=item['title'],
                                            description=item['snippet'],
                                            label_status=selected_label
                                        ):
                                            st.rerun()

                                # Tampilkan detail verifikasi jika ada
                                if 'verification' in item and st.session_state.enable_verification:
                                    with st.expander("🔍 Detail Verifikasi", expanded=False):
                                        verification = item['verification']
                                        col1, col2 = st.columns(2)

                                        with col1:
                                            st.write("**Cache Data (Google):**")
                                            st.write(f"Title: {item.get('title', 'N/A')}")
                                            st.write(f"Snippet: {item.get('snippet', 'N/A')[:100]}...")
                                            st.write(f"Keywords: {', '.join(verification.get('keywords_found_cache', []))}")

                                        with col2:
                                            st.write("**Live Data:**")
                                            st.write(f"HTTP Status: {verification.get('http_status', 'N/A')}")
                                            st.write(f"Accessible: {'✅ Yes' if verification.get('is_accessible') else '❌ No'}")
                                            st.write(f"Live Title: {verification.get('title', 'N/A')}")
                                            st.write(f"Keywords: {', '.join(verification.get('keywords_found_live', []))}")
                                        # --- TAMPILKAN HASIL ANALISIS JS ---
                                        if 'js_analysis' in verification and verification['js_analysis']:
                                            js_data = verification['js_analysis']
                                            st.divider()
                                            st.write("**Analisis Perilaku JS:**")
                                            
                                            if js_data.get('suspicious_requests'):
                                                st.warning(f"🚨 {len(js_data['suspicious_requests'])} request ke domain eksternal mencurigakan")
                                                
                                            if js_data.get('high_entropy_scripts'):
                                                st.warning(f"Sken {len(js_data['high_entropy_scripts'])} skrip memiliki entropy tinggi (obfuskasi)")
                                            
                                            if js_data.get('dangerous_patterns'):
                                                st.error(f"Pola JS berbahaya (eval, atob, dll) ditemukan!")
                                        # --- SELESAI ---
                                if st.session_state.get(f"analyze_{item['url']}", False):
                                    with st.container(border=True):
                                        st.markdown("##### 🔬 Hasil Analisis Mendalam")
                                        if 'deep_analysis' in item and item['deep_analysis']['status'] == 'success':
                                            analysis = item['deep_analysis']
                                            if analysis['keywords_found']:
                                                st.write("✅ **Kata Kunci Ditemukan:**")
                                                keywords_df = pd.DataFrame(list(analysis['keywords_found'].items()),
                                                                         columns=['Kata Kunci', 'Jumlah'])
                                                st.dataframe(keywords_df, hide_index=True)

                                            if analysis['suspicious_links']:
                                                st.write("✅ **Tautan Mencurigakan Ditemukan:**")
                                                for link in analysis['suspicious_links']:
                                                    st.code(f"{link['text']} -> {link['url']}", language=None)
                                        else:
                                            st.error("Gagal melakukan analisis mendalam")
            
            # Tampilkan Backlink Analysis
            if results['backlinks']:
                with st.expander("🔗 Analisis Backlink Mencurigakan"):
                    for backlink in results['backlinks']:
                        st.write(f"**{backlink['domain']}**")
                        st.caption(f"{backlink['title']}")
                        st.code(backlink['url'], language=None)
            
            # Tombol Simpan ke Dashboard
            st.divider()
            if st.button("💾 Simpan Hasil ke Dashboard", type="primary"):
                current_df = data_manager.load_or_create_dataframe() # <-- Panggil dari data_manager
                
                domain_to_update = st.session_state.scanned_domain
                if domain_to_update in current_df['domain'].values:
                    domain_idx = current_df.index[current_df['domain'] == domain_to_update][0]
                else:
                    new_row = {
                        'domain': domain_to_update,  
                        'jumlah_kasus': 0,  
                        'hack_judol': 0,  
                        'pornografi': 0,  
                        'hacked': 0,
                        'last_scan': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    domain_idx = current_df.index[current_df['domain'] == domain_to_update][0]
                
                # Update counts
                for cat_id, cat_data in results['categories'].items():
                    label_name = reverse_mapping.get(cat_id, '').replace(' ', '_')
                    count = len(cat_data["items"])
                    if count > 0 and label_name in current_df.columns:
                        current_value = current_df.loc[domain_idx, label_name]
                        if pd.isna(current_value):
                            current_value = 0
                        current_df.loc[domain_idx, label_name] = int(current_value) + count
                
                # Hitung total kasus
                hack_judol = current_df.loc[domain_idx, 'hack_judol'] if not pd.isna(current_df.loc[domain_idx, 'hack_judol']) else 0
                pornografi = current_df.loc[domain_idx, 'pornografi'] if not pd.isna(current_df.loc[domain_idx, 'pornografi']) else 0
                hacked = current_df.loc[domain_idx, 'hacked'] if not pd.isna(current_df.loc[domain_idx, 'hacked']) else 0
                
                current_df.loc[domain_idx, 'jumlah_kasus'] = int(hack_judol + pornografi + hacked)
                current_df.loc[domain_idx, 'last_scan'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Konversi semua kolom numerik ke int
                for col in ['jumlah_kasus', 'hack_judol', 'pornografi', 'hacked']:
                    if col in current_df.columns:
                        current_df[col] = current_df[col].fillna(0).astype(int)
                
                current_df.to_csv(data_manager.DATA_FILE, index=False) # <-- Gunakan var dari data_manager
                st.success("✅ Data berhasil disimpan ke dashboard!")
                time.sleep(2)
                st.rerun()
        
        else:
            st.success("✅ Tidak ditemukan konten mencurigakan")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.header("📊 Dashboard Peringkat Domain")
    
    if os.path.exists(data_manager.DATA_FILE): # <-- Gunakan var dari data_manager
        df = data_manager.load_or_create_dataframe() # <-- Panggil dari data_manager
        if not df.empty:
            for col in ['jumlah_kasus', 'hack_judol', 'pornografi', 'hacked']:
                if col in df.columns:
                    df[col] = df[col].fillna(0).astype(int)
            
            df = df.sort_values('jumlah_kasus', ascending=False)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Domain", len(df))
            with col2:
                st.metric("Total Kasus", int(df['jumlah_kasus'].sum()))
            with col3:
                infected_domains = len(df[df['jumlah_kasus'] > 0])
                st.metric("Domain Terinfeksi", infected_domains)
            with col4:
                max_cases = int(df['jumlah_kasus'].max()) if not df.empty else 0
                st.metric("Kasus Tertinggi", max_cases)
            
            st.subheader("Peringkat Domain")
            
            display_df = df.copy()
            
            for col in ['hack_judol', 'pornografi', 'hacked']:
                if col not in display_df.columns:
                    display_df[col] = 0
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "domain": st.column_config.TextColumn("Domain", width="medium"),
                    "jumlah_kasus": st.column_config.NumberColumn("Total Kasus", format="%d"),
                    "hack_judol": st.column_config.NumberColumn("Judi", format="%d"),
                    "pornografi": st.column_config.NumberColumn("Porno", format="%d"),
                    "hacked": st.column_config.NumberColumn("Hacked", format="%d"),
                    "last_scan": st.column_config.DatetimeColumn("Terakhir Scan")
                }
            )
            
            if len(df) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Distribusi Kasus (Top 10)")
                    top_10 = df.head(10).copy()
                    
                    chart_cols = []
                    for col in ['hack_judol', 'pornografi', 'hacked']:
                        if col in top_10.columns:
                            chart_cols.append(col)
                    
                    if chart_cols:
                        chart_data = top_10.set_index('domain')[chart_cols].astype(int)
                        st.bar_chart(chart_data)
                    else:
                        st.info("Tidak ada data untuk ditampilkan di chart")
                
                with col2:
                    st.subheader("Pie Chart Kasus")
                    case_data = {}
                    for col in ['hack_judol', 'pornografi', 'hacked']:
                        if col in df.columns:
                            case_data[col] = int(df[col].sum())
                    
                    if case_data:
                        st.plotly_chart({
                            'data': [{
                                'type': 'pie',
                                'labels': list(case_data.keys()),
                                'values': list(case_data.values())
                            }]
                        }, use_container_width=True)
                    else:
                        st.info("Tidak ada data untuk pie chart")
            else:
                st.info("Tidak cukup data untuk menampilkan chart")
        else:
            st.info("Belum ada data di dashboard. Lakukan pemindaian dan simpan hasilnya.")
    else:
        st.info("Belum ada data di dashboard. Lakukan pemindaian dan simpan hasilnya.")

# --- TAB 3: KONFIGURASI ---
# --- TAB 3: KONFIGURASI ---
with tab3:
    if st.session_state.role == 'admin':
        # --- TAMPILKAN SEMUA KONTEN KONFIGURASI UNTUK ADMIN ---
        st.header("⚙️ Konfigurasi Sistem (Admin)")
        
        st.subheader("Pengaturan Scanner")
        max_pages = st.slider("Jumlah Maksimum Halaman untuk Crawling", 10, 100, 50, key="admin_max_pages")
        timeout = st.slider("Timeout Request (detik)", 5, 30, 15, key="admin_timeout")
        
        st.subheader("Kata Kunci Deteksi")
        st.info("Kata kunci yang digunakan untuk deteksi konten berbahaya:")
        keywords_df = pd.DataFrame(MALICIOUS_KEYWORDS, columns=["Kata Kunci"])
        st.dataframe(keywords_df, use_container_width=True, hide_index=True)
        
        st.subheader("Informasi Sistem")
        st.write(f"Model ML: {'Tersedia' if model else 'Tidak Tersedia'}")
        st.write(f"Total Domain dalam Database: {len(ranking_data) if not ranking_data.empty else 0}")
        st.write(f"Versi: 2.1 - Enhanced Scanner")

    else:
        # --- SEMBUNYIKAN UNTUK USER BIASA ---
        st.error("⛔ Anda tidak memiliki hak akses untuk melihat halaman ini.")
        st.info(f"Anda login sebagai {st.session_state.username} dari {st.session_state.organization}.")
        
# --- TAB 4: AUDIT LOG ---
with tab4:
    if st.session_state.role == 'admin':
        st.header("🛡️ Audit Log Aktivitas User")
        st.info("Menampilkan 50 aktivitas terakhir dari semua instansi.")
        
        try:
            conn = sqlite3.connect('users.db')
            # Ambil 50 log terbaru, diurutkan dari yang paling baru
            log_df = pd.read_sql_query(
                "SELECT timestamp, username, organization_name, action, details FROM activity_log ORDER BY timestamp DESC LIMIT 50",
                conn
            )
            conn.close()
            
            st.dataframe(log_df, use_container_width=True)
            
            if st.button("Refresh Log"):
                st.rerun()
                
        except Exception as e:
            st.error(f"Gagal memuat log: {e}")
            
    else:
        st.error("⛔ Hanya Administrator yang dapat melihat halaman Audit Log.")

# --- TAB 5: MANAJEMEN USER ---
with tab5:
    # Seluruh tab ini hanya untuk admin
    if st.session_state.role == 'admin':
        st.header("👤 Manajemen User")

        conn = None
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # --- 1. CREATE: Tambah User Baru ---
            with st.expander("➕ Tambah User Baru", expanded=False):
                with st.form("tambah_user_form", clear_on_submit=True):
                    st.subheader("Formulir User Baru")
                    new_username = st.text_input("Username Baru")
                    new_password = st.text_input("Password Baru", type="password")
                    new_role = st.selectbox("Peran", ['user', 'admin'], index=0)
                    new_organization = st.text_input("Nama Instansi")
                    
                    submitted = st.form_submit_button("Tambah User")
                    if submitted:
                        if not all([new_username, new_password, new_role, new_organization]):
                            st.error("Harap isi semua field.")
                        else:
                            try:
                                # Hash password
                                password_hash = pwd_context.hash(new_password)
                                c.execute(
                                    "INSERT INTO users (username, password_hash, role, organization_name) VALUES (?, ?, ?, ?)",
                                    (new_username, password_hash, new_role, new_organization)
                                )
                                conn.commit()
                                st.success(f"User '{new_username}' berhasil dibuat!")
                                st.rerun() # Refresh halaman untuk update daftar
                            except sqlite3.IntegrityError:
                                st.error(f"Gagal: Username '{new_username}' sudah ada.")
                            except Exception as e:
                                st.error(f"Terjadi error: {e}")

            # --- 2. READ: Tampilkan Daftar User ---
            st.subheader("Daftar User Terdaftar")
            users_df = pd.read_sql_query(
                # JANGAN PERNAH ambil password_hash
                "SELECT id, username, role, organization_name, user_api_key FROM users", 
                conn
            )
            st.dataframe(users_df, use_container_width=True)

            # --- 3. UPDATE / DELETE: Kelola User yang Ada ---
            with st.expander("✏️ Edit / Hapus User", expanded=False):
                if not users_df.empty:
                    # Buat daftar pilihan user dari dataframe
                    user_list = users_df['username'].tolist()
                    selected_username = st.selectbox("Pilih user untuk dikelola", user_list)
                    
                    if selected_username:
                        # Ambil data user yang dipilih
                        user_data = users_df[users_df['username'] == selected_username].iloc[0]
                        
                        # Form untuk UPDATE
                        with st.form("edit_user_form"):
                            st.subheader(f"Edit User: {user_data['username']}")
                            
                            edit_role = st.selectbox(
                                "Peran", 
                                ['user', 'admin'], 
                                index=0 if user_data['role'] == 'user' else 1
                            )
                            edit_organization = st.text_input(
                                "Instansi", 
                                value=user_data['organization_name']
                            )
                            edit_password = st.text_input(
                                "Reset Password (Biarkan kosong jika tidak ingin ganti)", 
                                type="password"
                            )
                            
                            update_submitted = st.form_submit_button("Update User")
                            if update_submitted:
                                try:
                                    if edit_password:
                                        # Jika password baru diisi, hash dan update
                                        new_hash = pwd_context.hash(edit_password)
                                        c.execute(
                                            "UPDATE users SET role = ?, organization_name = ?, password_hash = ? WHERE username = ?",
                                            (edit_role, edit_organization, new_hash, selected_username)
                                        )
                                    else:
                                        # Jika tidak, update sisanya
                                        c.execute(
                                            "UPDATE users SET role = ?, organization_name = ? WHERE username = ?",
                                            (edit_role, edit_organization, selected_username)
                                        )
                                    conn.commit()
                                    st.success(f"User '{selected_username}' berhasil diupdate.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Gagal update: {e}")

                        # Fitur untuk DELETE
                        st.divider()
                        st.error("Area Berbahaya: Hapus User")
                        
                        # Cek untuk mencegah admin menghapus akunnya sendiri
                        if selected_username == st.session_state['username']:
                            st.warning("Anda tidak dapat menghapus akun Anda sendiri.")
                        else:
                            delete_check = st.checkbox(f"Saya yakin ingin menghapus user '{selected_username}' secara permanen.")
                            if delete_check:
                                if st.button("HAPUS USER PERMANEN", type="primary"):
                                    try:
                                        c.execute("DELETE FROM users WHERE username = ?", (selected_username,))
                                        conn.commit()
                                        st.success(f"User '{selected_username}' telah dihapus.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Gagal menghapus: {e}")
                else:
                    st.info("Belum ada user terdaftar selain Anda.")

        except Exception as e:
            st.error(f"Gagal terhubung ke database user: {e}")
        finally:
            if conn:
                conn.close()

    # Jika bukan admin
    else:
        st.error("⛔ Hanya Administrator yang dapat melihat halaman Manajemen User.")
# --- Footer ---
st.sidebar.markdown("---")
# Pastikan session state sudah ada sebelum diakses
if "username" in st.session_state:
    st.sidebar.info(f"Login sebagai: **{st.session_state.username}**")
if "role" in st.session_state:
    st.sidebar.info(f"Peran: **{st.session_state.role}**")

# Tampilkan menu API Key HANYA untuk 'user'
if st.session_state.role == 'user':
    st.sidebar.subheader("API Key Anda")
    
    current_key = st.session_state.get("user_api_key", "")
    if current_key:
        st.sidebar.success("API Key Anda sudah tersimpan.")
        st.sidebar.text_input("API Key Anda", value=current_key, type="password", disabled=True, key="api_key_display")
    else:
        st.sidebar.warning("Anda belum memiliki API Key pribadi. Scan akan menggunakan kuota admin.")
    
    with st.sidebar.expander("Ganti/Tambah API Key"):
        new_key = st.text_input("Masukkan SerpApi Key Baru", type="password", key="api_key_input")
        
        if st.button("Simpan Key"):
            if new_key:
                try:
                    # --- LOGIKA UPDATE DATABASE (TAMBAHKAN INI) ---
                    conn = sqlite3.connect('users.db')
                    c = conn.cursor()
                    c.execute(
                        "UPDATE users SET user_api_key = ? WHERE username = ?",
                        (new_key, st.session_state['username'])
                    )
                    conn.commit()
                    conn.close()
                    
                    # Update session state juga
                    st.session_state['user_api_key'] = new_key
                    
                    st.sidebar.success("Key berhasil disimpan!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Gagal menyimpan key: {e}")
            else:
                st.sidebar.error("Key tidak boleh kosong.")
st.sidebar.divider() # Garis pemisah
if st.sidebar.button("🚪 Logout"):
    # Log aktivitas logout
    log_activity(
        st.session_state['username'], 
        st.session_state['organization'], 
        'LOGOUT'
    )
    
    # Reset SEMUA state yang berhubungan dengan user
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.session_state["organization"] = None
    st.session_state["user_api_key"] = None
    
    # Hapus juga state aplikasi agar bersih saat user lain login
    st.session_state.scan_results = None
    st.session_state.scanned_domain = None
    st.session_state.scan_in_progress = False
    
    st.success("Anda berhasil logout.")
    time.sleep(1) # Beri jeda sebentar agar user bisa membaca pesan
    st.rerun() # Refresh halaman untuk kembali ke layar login
# --- SELESAI PENAMBAHAN ---  
st.sidebar.info(
    
    "🛡️ **Sistem Deteksi SEO Poisoning v2.1**\n\n"
    "**Fitur Baru:** Real-Time Content Verification\n"
    "Mengurangi false positive dengan verifikasi langsung ke website target"
)