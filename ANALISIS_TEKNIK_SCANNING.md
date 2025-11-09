# ANALISIS TEKNIK SCANNING SISTEM

Dokumen ini menganalisis teknik scanning yang digunakan dalam sistem deteksi konten malicious pada domain pendidikan, termasuk penggunaan dorking dan teknik-teknik lainnya.

---

## 1. APAKAH TEKNIK DORKING SUDAH SANGAT BAGUS?

### 1.1 Penggunaan Dorking dalam Sistem

**Ya, sistem menggunakan dorking, namun TIDAK HANYA mengandalkan dorking.**

**Teknik Dorking yang Digunakan:**

1. **Google Search Query dengan SerpAPI**
   - Menggunakan query seperti:
     ```
     site:{domain} ("slot gacor" OR "situs judi" OR "deposit pulsa" OR "judi online" OR "casino" OR "poker" OR "togel" OR "gambling" OR "bokep" OR "video dewasa" OR "nonton film dewasa" OR "porn" OR "hacked" OR "defaced" OR "deface")
     ```
   - Query `inurl:` untuk menemukan URL dengan keyword di path/params:
     ```
     inurl:"bokep" site:{domain}
     inurl:"gacor" site:{domain}
     inurl:"slot" site:{domain}
     ```

2. **Comprehensive Query Mode**
   - Menggunakan 1 query comprehensive vs 4 query terpisah (hemat 75% API calls)
   - Mengoptimalkan penggunaan quota SerpAPI

3. **Caching System**
   - Hasil search di-cache untuk mengurangi API calls
   - Menghemat 95% quota SerpAPI dengan intelligent caching

**Kelebihan Teknik Dorking yang Digunakan:**
- ✅ Menggunakan query yang comprehensive untuk menangkap berbagai jenis konten malicious
- ✅ Menggunakan `inurl:` untuk menemukan URL dengan keyword di path/params
- ✅ Mengoptimalkan quota API dengan caching dan comprehensive query
- ✅ Menggunakan multiple queries untuk coverage yang lebih baik

**Keterbatasan Teknik Dorking:**
- ⚠️ Hanya menemukan konten yang sudah terindex oleh Google
- ⚠️ Tidak dapat menemukan konten yang tidak terindex (orphan pages, hidden content)
- ⚠️ Terbatas oleh hasil pencarian Google (max 100 results per query)
- ⚠️ Tidak dapat menemukan konten yang tersembunyi dengan baik

---

## 2. APAKAH TEKNIK SCAN HANYA MENGANDALKAN SEBAGIAN BESAR DORKING?

### 2.1 Jawaban: TIDAK, Sistem Menggunakan KOMBINASI Berbagai Teknik

**Sistem TIDAK hanya mengandalkan dorking.** Sistem menggunakan kombinasi berbagai teknik scanning untuk coverage yang lebih komprehensif.

---

## 3. TEKNIK-TEKNIK SCANNING YANG DIGUNAKAN

### 3.1 Teknik Utama: Multi-Layer Scanning

Sistem menggunakan **multi-layer scanning approach** dengan berbagai teknik:

#### **Layer 1: Discovery (Dorking + Search)**

**1. Google Search Query (Dorking)**
- **Fungsi**: Discovery awal konten malicious yang terindex Google
- **Teknik**: 
  - Query `site:{domain}` dengan keyword malicious
  - Query `inurl:` untuk menemukan URL dengan keyword di path/params
  - Comprehensive query untuk semua konten ilegal dalam satu search
- **Kelebihan**: 
  - Cepat dan efisien
  - Menggunakan index Google yang sudah terorganisir
  - Menemukan konten yang sudah terindex
- **Keterbatasan**: 
  - Hanya menemukan konten yang terindex
  - Terbatas oleh hasil pencarian Google

**2. Multi-Source Search**
- **Google Search** (primary) - menggunakan SerpAPI
- **Bing Search** (optional) - untuk coverage tambahan
- **DuckDuckGo Search** (optional) - untuk coverage tambahan
- **Fungsi**: Meningkatkan coverage dengan menggunakan multiple search engines

#### **Layer 2: Subdomain Enumeration**

**1. DNS Lookup**
- **Fungsi**: Menemukan subdomain yang aktif
- **Teknik**: 
  - DNS lookup untuk subdomain umum (100+ entries)
  - Brute force dengan wordlist
  - Validasi DNS untuk subdomain yang ditemukan
- **Kelebihan**: 
  - Menemukan subdomain yang tidak terindex
  - Tidak tergantung pada search engine
  - Cepat dan efisien

**2. Web Search untuk Subdomain**
- **Fungsi**: Menemukan subdomain yang terindex
- **Teknik**: Query `site:{domain} -www.{domain}` untuk menemukan subdomain
- **Kelebihan**: Menemukan subdomain yang terindex Google

**3. Subdomain Content Scanning**
- **Fungsi**: Scan konten subdomain yang ditemukan
- **Teknik**: 
  - Search Google untuk subdomain dengan query malicious keywords
  - Analisis konten subdomain untuk menemukan konten malicious
  - Deep analysis untuk mendapatkan lebih banyak informasi

#### **Layer 3: Deep Content Analysis**

**1. Domain Crawler (untuk Scan Komprehensif)**
- **Fungsi**: Crawling halaman website untuk menemukan konten malicious
- **Teknik**: 
  - Selenium untuk crawling halaman website
  - Follow links untuk menemukan halaman yang tidak terindex
  - Graph analysis untuk menemukan orphan pages
- **Kelebihan**: 
  - Menemukan konten yang tidak terindex
  - Menemukan orphan pages dan isolated clusters
  - Comprehensive coverage
- **Keterbatasan**: 
  - Lebih lambat dibanding dorking
  - Memerlukan lebih banyak resource

**2. Path Discovery**
- **Fungsi**: Mencoba berbagai path yang mencurigakan
- **Teknik**: 
  - Mencoba path seperti `/slot`, `/judi`, `/bokep`, `/drugs`, dll
  - Scan path yang ditemukan untuk konten malicious
- **Kelebihan**: 
  - Menemukan konten yang tidak terindex
  - Menemukan konten yang tersembunyi
- **Keterbatasan**: 
  - Terbatas oleh wordlist path
  - Memerlukan banyak HTTP requests

**3. Deep Content Detection**
- **Fungsi**: Analisis mendalam konten HTML untuk menemukan konten malicious
- **Teknik**: 
  - Keyword matching
  - Hidden content detection (CSS hidden, invisible, opacity 0, dll)
  - Injection detection (JavaScript eval, document.write, dll)
  - Comment detection (HTML comments)
  - Meta tags detection
  - Hidden attributes detection
- **Kelebihan**: 
  - Menemukan konten yang tersembunyi dengan baik
  - Comprehensive analysis
  - Deteksi berbagai teknik penyembunyian konten

#### **Layer 4: Real-Time Verification**

**1. Quick Verification**
- **Fungsi**: Verifikasi cepat konten dengan multiple user agents
- **Teknik**: 
  - Fetch URL dengan multiple user agents
  - Check apakah konten malicious masih ada
  - Deteksi apakah konten berbeda untuk user agents yang berbeda
- **Kelebihan**: 
  - Cepat dan efisien
  - Menemukan konten yang berbeda untuk user agents yang berbeda
- **Keterbatasan**: 
  - Tidak dapat menemukan konten yang hanya muncul dengan JavaScript

**2. Selenium Verification (Real-Time)**
- **Fungsi**: Verifikasi konten dengan Selenium untuk menangani JavaScript
- **Teknik**: 
  - Menggunakan Selenium untuk render halaman dengan JavaScript
  - Verifikasi konten yang terlihat oleh pengguna
  - Deteksi konten yang hanya muncul dengan JavaScript
- **Kelebihan**: 
  - Menemukan konten yang hanya muncul dengan JavaScript
  - Verifikasi konten yang terlihat oleh pengguna
  - Comprehensive verification
- **Keterbatasan**: 
  - Lebih lambat dibanding quick verification
  - Memerlukan lebih banyak resource

#### **Layer 5: Machine Learning Classification**

**1. ML Model Prediction**
- **Fungsi**: Klasifikasi konten menggunakan machine learning
- **Teknik**: 
  - SVM, Naive Bayes, atau Random Forest untuk klasifikasi
  - TF-IDF untuk feature extraction
  - Stemming bahasa Indonesia untuk preprocessing
- **Kelebihan**: 
  - Deteksi konten malicious yang tidak terdeteksi keyword matching
  - Dapat mengenali pola-pola konten malicious
  - Akurasi tinggi dengan model yang baik

**2. Keyword Fallback**
- **Fungsi**: Fallback jika ML model tidak tersedia atau gagal
- **Teknik**: Keyword matching untuk kategori tertentu (pornografi, hacked, judi)
- **Kelebihan**: 
  - Tetap dapat mendeteksi konten malicious meskipun ML model tidak tersedia
  - Simple dan cepat

---

## 4. DISTRIBUSI PENGGUNAAN TEKNIK

### 4.1 Perbandingan Teknik

**Scan Cepat (Google Only):**
- **Dorking**: ~70% (discovery awal)
- **Subdomain Enumeration**: ~20% (DNS lookup)
- **Real-Time Verification**: ~10% (verifikasi konten)

**Scan Komprehensif (Google + Crawling):**
- **Dorking**: ~40% (discovery awal)
- **Domain Crawler**: ~30% (deep crawling)
- **Subdomain Enumeration**: ~15% (DNS lookup + search)
- **Deep Content Detection**: ~10% (hidden content)
- **Real-Time Verification**: ~5% (verifikasi konten)

**Kesimpulan:**
- **Scan Cepat**: Lebih mengandalkan dorking (70%)
- **Scan Komprehensif**: Menggunakan kombinasi berbagai teknik, dorking hanya 40%

---

## 5. KELEBIHAN DAN KETERBATASAN

### 5.1 Kelebihan Sistem Multi-Layer Scanning

1. **Comprehensive Coverage**
   - Menggunakan berbagai teknik untuk coverage yang lebih baik
   - Tidak hanya mengandalkan satu teknik
   - Menemukan konten yang tidak terindex dan tersembunyi

2. **Layered Defense**
   - Setiap layer menangani aspek yang berbeda
   - Layer 1: Discovery (dorking)
   - Layer 2: Subdomain enumeration
   - Layer 3: Deep content analysis
   - Layer 4: Real-time verification
   - Layer 5: ML classification

3. **Flexible dan Adaptable**
   - Dapat disesuaikan dengan kebutuhan (cepat vs komprehensif)
   - Dapat mengaktifkan/nonaktifkan teknik tertentu
   - Dapat menambahkan teknik baru jika diperlukan

### 5.2 Keterbatasan Sistem

1. **Resource Intensive**
   - Scan komprehensif memerlukan lebih banyak resource (CPU, memory, network)
   - Crawling memerlukan waktu yang lebih lama
   - Selenium verification memerlukan lebih banyak resource

2. **API Quota**
   - Meskipun sudah dioptimalkan dengan caching, masih memerlukan API quota untuk SerpAPI
   - Terbatas oleh quota API yang tersedia

3. **False Positives/Negatives**
   - Dorking dapat menghasilkan false positives (konten yang tidak malicious)
   - ML model dapat menghasilkan false negatives (konten malicious yang tidak terdeteksi)

---

## 6. REKOMENDASI PERBAIKAN

### 6.1 Perbaikan Teknik Dorking

1. **Query Optimization**
   - ✅ Sudah menggunakan comprehensive query (hemat 75% API calls)
   - ✅ Sudah menggunakan caching (hemat 95% quota)
   - 💡 Bisa ditambahkan: Query yang lebih spesifik untuk mengurangi false positives

2. **Multiple Search Engines**
   - ✅ Sudah menggunakan Google, Bing, DuckDuckGo (optional)
   - 💡 Bisa ditambahkan: Yandex, Baidu untuk coverage internasional

3. **Query Variations**
   - ✅ Sudah menggunakan berbagai query variations
   - 💡 Bisa ditambahkan: Query yang lebih banyak untuk coverage yang lebih baik

### 6.2 Penambahan Teknik Baru

1. **Web Archive (Wayback Machine)**
   - 💡 Bisa ditambahkan: Scan versi historis website untuk menemukan konten malicious yang sudah dihapus

2. **Certificate Transparency Logs**
   - 💡 Bisa ditambahkan: Scan certificate transparency logs untuk menemukan subdomain baru

3. **DNS Records Analysis**
   - 💡 Bisa ditambahkan: Analisis DNS records untuk menemukan subdomain dan server

4. **Social Media Monitoring**
   - 💡 Bisa ditambahkan: Monitor social media untuk menemukan link ke konten malicious

---

## 7. KESIMPULAN

### 7.1 Apakah Teknik Dorking Sudah Sangat Bagus?

**Ya, teknik dorking yang digunakan sudah cukup baik**, dengan:
- ✅ Query yang comprehensive
- ✅ Optimasi quota API dengan caching
- ✅ Multiple query variations
- ✅ Query `inurl:` untuk menemukan URL dengan keyword di path/params

**Namun, masih ada ruang untuk perbaikan:**
- 💡 Query yang lebih spesifik untuk mengurangi false positives
- 💡 Multiple search engines untuk coverage yang lebih baik
- 💡 Query variations yang lebih banyak

### 7.2 Apakah Teknik Scan Hanya Mengandalkan Sebagian Besar Dorking?

**TIDAK, sistem TIDAK hanya mengandalkan dorking.**

**Distribusi Teknik:**
- **Scan Cepat**: Dorking ~70%, teknik lain ~30%
- **Scan Komprehensif**: Dorking ~40%, teknik lain ~60%

**Sistem menggunakan multi-layer scanning approach dengan:**
1. **Dorking** (discovery awal) - 40-70%
2. **Subdomain Enumeration** (DNS lookup + search) - 15-20%
3. **Domain Crawler** (deep crawling) - 30% (hanya komprehensif)
4. **Deep Content Detection** (hidden content) - 10% (hanya komprehensif)
5. **Real-Time Verification** (Selenium) - 5-10%
6. **ML Classification** (klasifikasi konten) - integrated

**Kesimpulan:**
- Sistem menggunakan **kombinasi berbagai teknik** untuk coverage yang lebih komprehensif
- Dorking digunakan sebagai **discovery awal**, kemudian dilengkapi dengan teknik lain untuk validasi dan deep analysis
- Untuk scan komprehensif, dorking hanya ~40%, sedangkan teknik lain ~60%

---

**Catatan:**
- Distribusi persentase dapat bervariasi tergantung pada konfigurasi dan jenis scan
- Teknik yang digunakan dapat disesuaikan dengan kebutuhan (cepat vs komprehensif)
- Sistem dapat dikembangkan dengan menambahkan teknik baru jika diperlukan


