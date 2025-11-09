# config.py
"""
Menyimpan semua konstanta dan konfigurasi aplikasi.
"""

import os
from pathlib import Path

# Base directory untuk data files (relative to scanner app)
BASE_DIR = Path(__file__).resolve().parent.parent  # Parent dari scanner app (project root)

DATA_FILE = os.path.join(BASE_DIR, 'dashboard_ranking_data_multi.csv')
DATASET_FILE = os.path.join(BASE_DIR, 'labeling_judol_dan_aman-26.csv')
MODEL_FILE = os.path.join(BASE_DIR, 'seo_poisoning_best_model.joblib')

MALICIOUS_KEYWORDS = [
    "slot", "gacor", "judi", "poker", "casino", "togel", "sbobet",
    "deposit pulsa", "bokep", "porn", "xxx", "nonton film dewasa",
    "hacked", "defaced", "deface", "gambling", "betting", "taruhan"
]

# Keywords untuk berbagai jenis konten ilegal
ILLEGAL_CONTENT_KEYWORDS = {
    'narkoba': [
        "sabu", "ganja", "heroin", "kokain", "ekstasi", "pil koplo", "narkoba",
        "drugs", "narkotika", "psikotropika", "jual sabu", "beli sabu", 
        "distributor narkoba", "supplier drugs", "dealer narkoba",
        "meth", "amphetamine", "crystal meth", "shabu", "ganja kering",
        "ekstasi pil", "lsd", "marijuana", "cannabis", "cocaine"
    ],
    'penipuan': [
        "penipuan", "scam", "fraud", "phishing", "penipuan online", 
        "tricker", "bohong", "tipu", "modus penipuan", "penipuan bank",
        "penipuan pinjaman", "penipuan investasi", "binary scam",
        "ponzi scheme", "pyramid scheme", "investment scam",
        "money laundering", "pencucian uang", "penipuan identitas"
    ],
    'phising': [
        "phishing", "phising", "login bank", "verifikasi rekening",
        "blokir akun", "aktivasi ulang", "konfirmasi data", 
        "reset password", "update informasi", "suspensi akun",
        "klaim hadiah", "undian berhadiah", "lotre online"
    ],
    'terorisme': [
        "bom", "teror", "terror", "radikal", "jihad", "isis", 
        "pembunuhan", "kekerasan", "senjata api", "pembakaran",
        "anarkis", "provokasi", "kerusuhan", "baku tembak"
    ],
    'pemalsuan': [
        "fake", "palsu", "kw", "replika", "imitasi", "copy",
        "sertifikat palsu", "ijazah palsu", "dokumen palsu",
        "identitas palsu", "kartu kredit palsu", "uang palsu"
    ],
    'perdagangan_manusia': [
        "human trafficking", "perdagangan manusia", "penjualan manusia",
        "trafik", "prostitusi paksa", "perbudakan", "eksploitasi seksual"
    ],
    'konten_kekerasan': [
        "kekerasan", "pembunuhan", "penyiksaan", "penganiayaan",
        "kekerasan seksual", "kekerasan fisik", "sadisme", "torture",
        "extreme violence", "murder", "kill", "blood", "gore"
    ],
    'prostitusi': [
        "prostitusi", "pelacuran", "psikotropika", "wanita panggilan",
        "escort", "call girl", "hooker", "prostitute", "sex worker",
        "tante girang", "sugar daddy", "sugar mommy"
    ],
    'perjudian_ilegal': [
        "judi", "casino", "togel", "lotre", "betting", "taruhan",
        "slot", "poker", "blackjack", "roulette", "gambling"
    ],
    'pornografi_anak': [
        "cp", "loli", "shota", "pedo", "pedophile", "anak di bawah umur",
        "child porn", "underage", "minor", "preteen"
    ]
}

# Pattern untuk deteksi konten tersembunyi/injeksi
HIDDEN_CONTENT_PATTERNS = [
    r'display:\s*none',  # CSS hidden
    r'visibility:\s*hidden',  # CSS invisible
    r'opacity:\s*0',  # CSS transparent
    r'position:\s*absolute.*left:\s*-9999',  # Off-screen
    r'font-size:\s*0',  # Tiny font
    r'color:\s*#[0-9a-fA-F]{6}\s*;?\s*background:\s*#\1',  # Same color text/background
    r'<!--.*?-->',  # HTML comments
    r'<style[^>]*>.*?</style>',  # Style tags (might hide content)
    r'text-indent:\s*-9999',  # Text indent off-screen
    r'clip:\s*rect\(0,\s*0,\s*0,\s*0\)',  # Clipped content
    r'overflow:\s*hidden.*width:\s*0.*height:\s*0',  # Zero size container
]

# Pattern untuk deteksi injeksi konten
INJECTION_PATTERNS = [
    r'eval\s*\(',  # JavaScript eval
    r'document\.write\s*\(',  # Document write
    r'innerHTML\s*=',  # InnerHTML manipulation
    r'createElement\s*\(',  # Dynamic element creation
    r'setTimeout\s*\(',  # Delayed execution
    r'setInterval\s*\(',  # Repeated execution
    r'Function\s*\(',  # Function constructor
    r'atob\s*\(',  # Base64 decode
    r'String\.fromCharCode',  # Char code manipulation
    r'<iframe[^>]*src\s*=',  # Iframe injection
    r'<script[^>]*src\s*=',  # External script injection
    r'window\.location\s*=',  # Redirect manipulation
    r'location\.href\s*=',  # Location change
]

# Blacklist API Configuration
ABUSEIPDB_API_KEY = 'your_abuseipdb_api_key_here'  # Replace with actual API key or load from env
BLACKLIST_SOURCES = [
    'abuseipdb',  # Add more sources if needed, e.g., 'virustotal'
]

# Execution mode
USE_NATIVE_FLOW = True  # Set True to mimic sistem-nativ logic (Google-only + Simple validator)