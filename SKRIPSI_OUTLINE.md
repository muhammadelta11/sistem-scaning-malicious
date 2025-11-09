# OUTLINE SKRIPSI

**Judul:**
**Sistem Deteksi Konten Malicious pada Domain Pendidikan Berbasis Machine Learning dengan Arsitektur REST API untuk Klien Multi-Platform**

---

## ABSTRAK

Konten malicious pada domain pendidikan merupakan ancaman cyber security yang semakin meningkat di Indonesia. Berdasarkan data dari berbagai sumber, sebagian besar serangan konten malicious terjadi pada domain pendidikan (.ac.id), dimana domain-domain kampus sering menjadi target karena memiliki otoritas tinggi dan aksesibilitas yang luas. Banyak domain pendidikan yang terindikasi memiliki konten ilegal seperti judi online, pornografi, narkoba, dan phishing yang dapat muncul dalam hasil pencarian mesin pencari dan merugikan pengguna. Penelitian ini mengembangkan sebuah sistem deteksi konten malicious pada domain pendidikan berbasis machine learning dengan arsitektur REST API untuk klien multi-platform. Sistem ini terdiri dari tiga komponen utama: (1) Backend API menggunakan Django REST Framework yang menyediakan endpoint untuk deteksi, (2) Model machine learning yang menggunakan algoritma klasifikasi (SVM, Naive Bayes, dan Random Forest) untuk mengidentifikasi konten malicious, dan (3) Aplikasi mobile client menggunakan Flutter untuk Android yang memungkinkan pengguna melakukan scanning domain secara real-time.

Metodologi pengembangan sistem menggunakan pendekatan waterfall dengan tahapan analisis kebutuhan, perancangan sistem, implementasi, dan pengujian. Model machine learning dilatih menggunakan dataset yang terdiri dari domain pendidikan aman dan domain pendidikan yang terindikasi konten malicious dengan fitur ekstraksi menggunakan TF-IDF dan stemming bahasa Indonesia. Evaluasi model menunjukkan Random Forest mencapai akurasi terbaik sebesar [X]% dengan F1-Score [Y]%.

Sistem yang dikembangkan telah berhasil mengintegrasikan fitur-fitur deteksi komprehensif termasuk real-time verification, graph analysis untuk menemukan orphan pages, deep content detection untuk konten tersembunyi, dan subdomain enumeration. Meskipun fokus penelitian pada domain pendidikan (.ac.id), sistem tetap dapat melakukan scanning pada domain lain untuk keperluan perbandingan dan validasi. Pengujian fungsional menunjukkan semua fitur berjalan dengan baik dan aplikasi mobile dapat terhubung dengan backend API melalui protokol HTTPS. Hasil pengujian menunjukkan sistem mampu mendeteksi konten malicious pada domain pendidikan dengan akurasi yang memadai dan dapat digunakan sebagai tools untuk membantu mengidentifikasi domain-domain pendidikan yang terindikasi konten malicious.

**Kata Kunci:** Konten Malicious, Domain Pendidikan, Machine Learning, REST API, Django, Flutter, Multi-Platform, Cyber Security, Domain Scanning

---

## DAFTAR ISI

### BAB I PENDAHULUAN
1.1. Latar Belakang Masalah
1.2. Rumusan Masalah
1.3. Batasan Masalah
1.4. Tujuan Penelitian
1.5. Manfaat Penelitian
1.6. Sistematika Penulisan

### BAB II TINJAUAN PUSTAKA
2.1. Konten Malicious pada Domain Pendidikan
    2.1.1. Pengertian Konten Malicious
    2.1.2. Fenomena Konten Malicious pada Domain Pendidikan di Indonesia
    2.1.3. Jenis-Jenis Konten Malicious (Judi Online, Pornografi, Narkoba, Phishing)
    2.1.4. Dampak Konten Malicious pada Domain Pendidikan
    2.1.5. Metode Deteksi Konten Malicious pada Domain Pendidikan
2.2. Machine Learning untuk Klasifikasi Teks
    2.2.1. Support Vector Machine (SVM)
    2.2.2. Naive Bayes
    2.2.3. Random Forest
    2.2.4. TF-IDF (Term Frequency-Inverse Document Frequency)
    2.2.5. Stemming dan Preprocessing
2.3. Arsitektur REST API
    2.3.1. Konsep REST (Representational State Transfer)
    2.3.2. Django REST Framework
    2.3.3. Token Authentication
    2.3.4. API Documentation dengan Swagger
2.4. Mobile Application Development
    2.4.1. Flutter Framework
    2.4.2. State Management dengan Provider
    2.4.3. HTTP Client untuk API Integration
2.5. Penelitian Terkait
    2.5.1. Sistem Deteksi Konten Malicious pada Domain Pendidikan
    2.5.2. Aplikasi Mobile untuk Cyber Security di Institusi Pendidikan
    2.5.3. Machine Learning untuk Klasifikasi Web Content
2.6. Kerangka Teori

### BAB III METODOLOGI PENELITIAN
3.1. Metodologi Pengembangan Sistem
    3.1.1. Model Pengembangan (Waterfall/SDLC)
    3.1.2. Tahapan Pengembangan
3.2. Analisis Kebutuhan
    3.2.1. Analisis Fungsional
    3.2.2. Analisis Non-Fungsional
    3.2.3. Analisis Stakeholder
3.3. Perancangan Sistem
    3.3.1. Arsitektur Sistem
    3.3.2. Use Case Diagram
    3.3.3. Sequence Diagram
    3.3.4. Entity Relationship Diagram (ERD)
    3.3.5. Database Design
3.4. Perancangan Machine Learning Model
    3.4.1. Dataset Preparation
    3.4.2. Feature Extraction
    3.4.3. Model Selection dan Training
    3.4.4. Model Evaluation
3.5. Implementasi
    3.5.1. Environment Setup
    3.5.2. Backend Development (Django REST API)
    3.5.3. Model Machine Learning Integration
    3.5.4. Mobile Application Development (Flutter)
3.6. Pengujian Sistem
    3.6.1. Pengujian Unit Testing
    3.6.2. Pengujian Integration Testing
    3.6.3. Pengujian Model Machine Learning
    3.6.4. Pengujian User Acceptance Testing (UAT)

### BAB IV HASIL DAN PEMBAHASAN
4.1. Hasil Analisis Kebutuhan
    4.1.1. Identifikasi Masalah
    4.1.2. Requirement Analysis
4.2. Hasil Perancangan Sistem
    4.2.1. Arsitektur Sistem yang Diterapkan
    4.2.2. Desain Database
    4.2.3. Desain API Endpoints
    4.2.4. Desain User Interface Mobile App
4.3. Hasil Implementasi Backend API
    4.3.1. Setup Django Project dan REST Framework
    4.3.2. Implementasi Authentication System
    4.3.3. Implementasi Scan Service
    4.3.4. Implementasi API Endpoints
    4.3.5. Implementasi Machine Learning Integration
    4.3.6. Implementasi Caching System
4.4. Hasil Training dan Evaluasi Model Machine Learning
    4.4.1. Dataset yang Digunakan
    4.4.2. Hasil Preprocessing Data
    4.4.3. Perbandingan Performa Model (SVM, Naive Bayes, Random Forest)
    4.4.4. Hasil Evaluasi Model Terpilih
    4.4.5. Classification Report
4.5. Hasil Implementasi Mobile Application
    4.5.1. Setup Flutter Project
    4.5.2. Implementasi UI/UX
    4.5.3. Implementasi State Management
    4.5.4. Implementasi API Integration
    4.5.5. Implementasi Fitur-Fitur Utama
4.6. Hasil Pengujian Sistem
    4.6.1. Pengujian Fungsional Backend API
    4.6.2. Pengujian Fungsional Mobile Application
    4.6.3. Pengujian Integrasi Backend dan Mobile
    4.6.4. Pengujian Performa Model Machine Learning
    4.6.5. Pengujian User Acceptance Testing
4.7. Pembahasan Hasil
    4.7.1. Analisis Hasil Pengujian
    4.7.2. Kelebihan Sistem
    4.7.3. Keterbatasan Sistem
    4.7.4. Perbandingan dengan Sistem Sejenis

### BAB V KESIMPULAN DAN SARAN
5.1. Kesimpulan
    5.1.1. Pencapaian Tujuan Penelitian
    5.1.2. Kontribusi Penelitian
    5.1.3. Hasil Akhir Sistem
5.2. Saran
    5.2.1. Pengembangan Selanjutnya
    5.2.2. Peningkatan Model Machine Learning
    5.2.3. Fitur Tambahan yang Dapat Dikembangkan
    5.2.4. Optimasi Performa Sistem

---

## RINGKASAN PER BAB

### BAB I: PENDAHULUAN
**Isi:**
- Menjelaskan latar belakang masalah konten malicious pada domain dan pentingnya deteksi
- Mengidentifikasi gap dalam penelitian sebelumnya
- Merumuskan masalah yang akan diselesaikan
- Menetapkan batasan penelitian (scope dan teknologi yang digunakan)
- Menyatakan tujuan dan manfaat penelitian
- Menjelaskan struktur penulisan skripsi

**Poin Penting:**
- Konten malicious pada domain sebagai ancaman cyber security
- Perlunya tools deteksi yang mudah digunakan
- Kombinasi ML + REST API + Mobile app sebagai solusi

---

### BAB II: TINJAUAN PUSTAKA
**Isi:**
1. **Teori Konten Malicious pada Domain** - Definisi, jenis-jenis konten malicious (judi, pornografi, narkoba, phishing), dampak, metode deteksi
2. **Machine Learning** - Algoritma klasifikasi (SVM, NB, RF), TF-IDF, preprocessing
3. **REST API** - Konsep REST, Django REST Framework, authentication
4. **Mobile Development** - Flutter framework, state management, API integration
5. **Penelitian Terkait** - Review paper/jurnal tentang deteksi konten malicious pada domain
6. **Kerangka Teori** - Integrasi semua teori untuk mendukung penelitian

**Poin Penting:**
- Landasan teori untuk setiap teknologi yang digunakan
- Justifikasi pemilihan teknologi
- Referensi penelitian sebelumnya

---

### BAB III: METODOLOGI PENELITIAN
**Isi:**
1. **Metodologi Pengembangan** - Waterfall/SDLC dengan tahapan jelas
2. **Analisis Kebutuhan** - Functional requirements, non-functional requirements
3. **Perancangan Sistem** - Arsitektur, diagram UML (Use Case, Sequence, ERD)
4. **Perancangan ML Model** - Dataset, feature extraction, training strategy
5. **Implementasi** - Langkah-langkah development
6. **Pengujian** - Strategi testing (unit, integration, UAT)

**Diagram yang Diperlukan:**
- Use Case Diagram
- Sequence Diagram
- ERD (Entity Relationship Diagram)
- Architecture Diagram
- Flowchart untuk proses scanning

---

### BAB IV: HASIL DAN PEMBAHASAN
**Isi:**

**4.1-4.2: Analisis dan Perancangan**
- Hasil analisis kebutuhan
- Desain arsitektur sistem
- Desain database dengan ERD
- Desain API endpoints

**4.3: Implementasi Backend**
- Detail implementasi Django REST API
- Authentication system
- Scan service dengan integrasi ML
- Caching mechanism
- Screenshot/ilustrasi kode penting

**4.4: Machine Learning**
- Dataset description (jumlah, distribusi)
- Preprocessing steps
- **Perbandingan 3 model:**
  - SVM Accuracy: X%, F1-Score: Y%
  - Naive Bayes Accuracy: X%, F1-Score: Y%
  - Random Forest Accuracy: X%, F1-Score: Y%
- **Classification Report** (Precision, Recall, F1 per class)
- **Confusion Matrix**
- Pemilihan model terbaik (Random Forest)

**4.5: Implementasi Mobile App**
- UI/UX design
- Fitur-fitur utama:
  - Login/Register
  - Dashboard
  - Domain Scanning
  - Scan History
  - Results View
- State management dengan Provider
- API integration

**4.6: Pengujian**
- **Tabel Hasil Pengujian Fungsional:**
  | No | Test Case | Expected Result | Actual Result | Status |
  |----|-----------|----------------|---------------|--------|
  | 1  | Login dengan kredensial valid | Berhasil login | Berhasil login | ✅ Pass |
  
- Pengujian API endpoints
- Pengujian mobile app features
- Pengujian integrasi
- Pengujian model ML dengan test data
- UAT hasil (jika ada)

**4.7: Pembahasan**
- Analisis hasil pengujian
- Kelebihan sistem
- Keterbatasan
- Perbandingan dengan sistem sejenis

**Tabel/Tabel Penting:**
1. Tabel perbandingan model ML
2. Classification report
3. Tabel hasil pengujian fungsional
4. Tabel performa API endpoints

---

### BAB V: KESIMPULAN DAN SARAN
**Isi:**

**Kesimpulan:**
- Sistem berhasil dikembangkan dengan teknologi yang dipilih
- Model ML mencapai akurasi [X]%
- Mobile app dapat terhubung dengan backend
- Semua fitur berfungsi sesuai kebutuhan
- Kontribusi untuk penelitian dan praktik

**Saran:**
1. **Pengembangan Model:**
   - Eksperimen dengan algoritma lain (Deep Learning)
   - Penambahan dataset untuk training
   - Feature engineering lebih lanjut

2. **Fitur Tambahan:**
   - iOS version
   - Web dashboard
   - Real-time notifications
   - Report generation (PDF)

3. **Optimasi:**
   - Caching mechanism yang lebih advanced
   - Load balancing untuk production
   - Monitoring dan logging yang lebih baik

---

## DAFTAR PUSTAKA

### Referensi Teori:
1. Paper tentang Deteksi Konten Malicious pada Domain
2. Jurnal tentang Machine Learning untuk klasifikasi teks
3. Dokumentasi Django REST Framework
4. Dokumentasi Flutter
5. Paper tentang REST API architecture
6. Jurnal tentang cyber security detection

### Format:
- APA Style atau sesuai format kampus
- Minimal 20-30 referensi
- Kombinasi paper/jurnal, buku, dan dokumentasi resmi

---

## LAMPIRAN

1. **Source Code** (bisa di GitHub atau CD)
2. **Screenshot Aplikasi** - UI/UX mobile app
3. **Screenshot Backend** - Admin panel, API documentation
4. **Dataset** - Sample dataset yang digunakan (jika diizinkan)
5. **Hasil Pengujian Lengkap** - Test cases dan hasil
6. **Installation Guide** - Panduan instalasi dan setup
7. **User Manual** - Panduan penggunaan aplikasi

---

## TEKNOLOGI YANG DIGUNAKAN

### Backend:
- Python 3.9+
- Django 5.2.7
- Django REST Framework 3.14+
- MySQL/PostgreSQL
- Redis (caching)
- Celery (optional)
- Gunicorn (production server)

### Machine Learning:
- scikit-learn
- pandas
- joblib
- TF-IDF vectorization
- Sastrawi (Indonesian stemming)

### Mobile App:
- Flutter SDK
- Dart
- Provider (state management)
- http (API client)
- shared_preferences

### Tools Development:
- Postman (API testing)
- Android Studio / VS Code
- Git (version control)

---

## METRIK EVALUASI

### Machine Learning:
- **Accuracy** - Akurasi keseluruhan
- **Precision** - Per class dan macro average
- **Recall** - Per class dan macro average
- **F1-Score** - Per class dan macro average
- **Confusion Matrix** - Visualisasi hasil klasifikasi

### Sistem:
- **Response Time** - API response time
- **Throughput** - Request per second
- **Error Rate** - Persentase error
- **User Satisfaction** - Dari UAT

---

## CATATAN PENTING

1. **Isi Angka di [X] dan [Y]%** dengan hasil aktual dari pengujian model Anda
2. **Screenshot** harus jelas dan relevan
3. **Diagram** harus konsisten dan mengikuti standar UML
4. **Kode** yang ditampilkan harus dijelaskan dengan komentar
5. **Referensi** harus up-to-date dan relevan
6. **Plagiarism** - Pastikan semua konten original atau cited dengan benar

---

**Selamat menulis skripsi! 🎓📝**

