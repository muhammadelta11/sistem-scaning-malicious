# BAB III METODOLOGI PENELITIAN

Bab ini membahas metodologi yang digunakan dalam penelitian ini, meliputi metodologi pengembangan sistem, analisis kebutuhan, perancangan sistem, perancangan model machine learning, implementasi, dan pengujian sistem.

---

## 3.1 Metodologi Pengembangan Sistem

### 3.1.1 Model Pengembangan (Waterfall/SDLC)

Penelitian ini menggunakan pendekatan metodologi pengembangan sistem Waterfall atau Software Development Life Cycle (SDLC) yang merupakan model pengembangan sistem klasik dengan tahapan yang berurutan dan sistematis. Model Waterfall dipilih karena cocok untuk proyek penelitian yang memiliki requirement yang jelas, tahapan yang terdefinisi dengan baik, dan memerlukan dokumentasi yang lengkap untuk keperluan akademik.

Model Waterfall terdiri dari beberapa tahapan utama:

1. **Analisis Kebutuhan (Requirements Analysis)**
   - Identifikasi masalah dan kebutuhan sistem
   - Analisis fungsional dan non-fungsional
   - Analisis stakeholder dan user requirements

2. **Perancangan Sistem (System Design)**
   - Perancangan arsitektur sistem
   - Perancangan database
   - Perancangan API endpoints
   - Perancangan user interface

3. **Perancangan Model Machine Learning**
   - Persiapan dataset
   - Feature extraction
   - Model selection dan training
   - Model evaluation

4. **Implementasi (Implementation)**
   - Development backend API
   - Integrasi model machine learning
   - Development aplikasi mobile
   - Integrasi komponen-komponen

5. **Pengujian (Testing)**
   - Unit testing
   - Integration testing
   - System testing
   - User acceptance testing

6. **Deployment dan Dokumentasi**
   - Deployment sistem
   - Dokumentasi lengkap
   - Maintenance plan

### 3.1.2 Tahapan Pengembangan

Tahapan pengembangan sistem dilakukan secara bertahap dengan alur sebagai berikut:

**Tahap 1: Analisis dan Perancangan (Minggu 1-4)**
- Analisis kebutuhan fungsional dan non-fungsional
- Studi literatur dan penelitian terkait
- Perancangan arsitektur sistem
- Perancangan database dan ERD
- Perancangan API endpoints
- Perancangan model machine learning

**Tahap 2: Persiapan Dataset dan Training Model (Minggu 5-8)**
- Pengumpulan dataset domain pendidikan
- Preprocessing data (cleaning, normalization)
- Feature extraction menggunakan TF-IDF
- Training model dengan algoritma SVM, Naive Bayes, dan Random Forest
- Evaluasi dan pemilihan model terbaik

**Tahap 3: Implementasi Backend API (Minggu 9-12)**
- Setup Django project dan REST Framework
- Implementasi authentication system
- Implementasi scan service dengan integrasi ML
- Implementasi API endpoints
- Implementasi caching system
- Testing backend API

**Tahap 4: Implementasi Mobile Application (Minggu 13-16)**
- Setup Flutter project
- Implementasi UI/UX
- Implementasi state management
- Implementasi API integration
- Testing aplikasi mobile

**Tahap 5: Integrasi dan Pengujian (Minggu 17-20)**
- Integrasi backend dan mobile app
- Integration testing
- System testing
- User acceptance testing
- Dokumentasi

**Tahap 6: Evaluasi dan Penulisan (Minggu 21-24)**
- Evaluasi performa sistem
- Analisis hasil pengujian
- Penulisan skripsi
- Revisi dan finalisasi

---

## 3.2 Analisis Kebutuhan

### 3.2.1 Analisis Fungsional

Analisis kebutuhan fungsional mengidentifikasi fitur-fitur yang harus ada dalam sistem. Berikut adalah kebutuhan fungsional utama:

**1. Manajemen User dan Authentication**
- Sistem harus dapat melakukan registrasi user baru
- Sistem harus dapat melakukan login dan logout
- Sistem harus dapat mengelola profil user
- Sistem harus dapat mengelola role dan permission (admin, staff, client)
- Sistem harus dapat mengelola kuota scan per user

**2. Domain Scanning**
- Sistem harus dapat melakukan scanning domain secara real-time
- Sistem harus dapat mendeteksi konten malicious menggunakan machine learning
- Sistem harus dapat melakukan verifikasi konten secara real-time
- Sistem harus dapat melakukan enumerasi subdomain
- Sistem harus dapat melakukan graph analysis untuk menemukan orphan pages
- Sistem harus dapat melakukan deep content detection
- Sistem harus dapat menampilkan progress scanning secara real-time

**3. Manajemen Hasil Scan**
- Sistem harus dapat menyimpan hasil scan
- Sistem harus dapat menampilkan history scan
- Sistem harus dapat menampilkan detail hasil scan
- Sistem harus dapat melakukan export hasil scan
- Sistem harus dapat menyimpan hasil scan permanen untuk premium user

**4. Manajemen Keywords**
- Sistem harus dapat menambah, mengubah, dan menghapus keywords malicious
- Sistem harus dapat mengelola kategori keywords
- Sistem harus dapat melakukan pencarian keywords

**5. Dashboard dan Reporting**
- Sistem harus dapat menampilkan dashboard dengan statistik scan
- Sistem harus dapat menampilkan ringkasan domain yang di-scan
- Sistem harus dapat menampilkan aktivitas user

**6. API untuk Mobile Application**
- Sistem harus menyediakan REST API untuk aplikasi mobile
- Sistem harus dapat melakukan authentication via token
- Sistem harus dapat menyediakan endpoint untuk scanning
- Sistem harus dapat menyediakan endpoint untuk history scan
- Sistem harus dapat menyediakan endpoint untuk user profile

### 3.2.2 Analisis Non-Fungsional

Analisis kebutuhan non-fungsional mengidentifikasi karakteristik kualitas sistem yang harus dipenuhi:

**1. Performance**
- Sistem harus dapat menangani minimal 10 request bersamaan
- Response time API harus kurang dari 2 detik untuk operasi normal
- Sistem harus dapat melakukan scanning dalam waktu maksimal 20 menit per domain
- Sistem harus dapat mengoptimalkan penggunaan API quota search engine

**2. Security**
- Sistem harus menggunakan protokol HTTPS untuk komunikasi
- Sistem harus menggunakan token-based authentication
- Sistem harus dapat melakukan rate limiting untuk mencegah abuse
- Sistem harus dapat melakukan logging aktivitas user
- Sistem harus dapat melakukan validasi input untuk mencegah injection

**3. Scalability**
- Sistem harus dapat di-scale dengan mudah
- Sistem harus dapat menangani peningkatan jumlah user
- Sistem harus menggunakan caching untuk meningkatkan performa
- Sistem harus dapat menggunakan load balancing jika diperlukan

**4. Reliability**
- Sistem harus memiliki uptime minimal 95%
- Sistem harus dapat menangani error dengan baik
- Sistem harus dapat melakukan backup data secara berkala
- Sistem harus memiliki logging yang komprehensif

**5. Usability**
- Sistem harus memiliki user interface yang intuitif
- Sistem harus dapat digunakan oleh user dengan berbagai tingkat keahlian
- Sistem harus menyediakan feedback yang jelas kepada user
- Sistem harus memiliki dokumentasi yang lengkap

**6. Maintainability**
- Sistem harus memiliki kode yang mudah dipahami dan di-maintain
- Sistem harus memiliki dokumentasi yang lengkap
- Sistem harus menggunakan best practices dalam pengembangan
- Sistem harus memiliki struktur yang modular

### 3.2.3 Analisis Stakeholder

Analisis stakeholder mengidentifikasi pihak-pihak yang terlibat dalam sistem:

**1. Admin**
- Mengelola user dan permission
- Mengelola keywords dan kategori
- Mengelola konfigurasi sistem
- Melihat dashboard dan statistik
- Mengelola API keys

**2. Staff**
- Melakukan scanning domain
- Melihat hasil scan
- Mengelola keywords (jika diberi permission)
- Melihat dashboard

**3. Client/User**
- Melakukan scanning domain
- Melihat hasil scan sendiri
- Melihat history scan sendiri
- Mengelola profil sendiri

**4. Mobile App User**
- Melakukan scanning domain melalui aplikasi mobile
- Melihat hasil scan melalui aplikasi mobile
- Melihat history scan melalui aplikasi mobile
- Login dan logout melalui aplikasi mobile

---

## 3.3 Perancangan Sistem

### 3.3.1 Arsitektur Sistem

Sistem dirancang dengan arsitektur three-tier yang terdiri dari:

**1. Presentation Layer**
- **Web Application**: Django template untuk admin panel dan dashboard
- **Mobile Application**: Flutter application untuk Android/iOS
- **REST API**: Django REST Framework untuk menyediakan API endpoints

**2. Application Layer**
- **Service Layer**: Business logic untuk scan, user management, keyword management
- **Machine Learning Model**: Model klasifikasi untuk deteksi konten malicious
- **Authentication System**: Token-based authentication
- **Caching System**: Redis untuk caching hasil scan dan API responses

**3. Data Layer**
- **Database**: MySQL/PostgreSQL untuk menyimpan data
- **File Storage**: Untuk menyimpan model machine learning dan file lainnya
- **External APIs**: SerpAPI untuk search engine, AbuseIPDB untuk IP intelligence

**Arsitektur Sistem:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
├─────────────────────┬───────────────────┬────────────────────┤
│  Web Application   │  Mobile App      │   REST API         │
│  (Django Template) │  (Flutter)       │   (DRF)            │
└─────────────────────┴───────────────────┴────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
├───────────────────┬───────────────┬─────────────────────────┤
│  Service Layer    │  ML Model     │   Authentication        │
│  - ScanService    │  - SVM        │   - Token Auth          │
│  - UserService    │  - NB         │   - Permission          │
│  - KeywordService │  - RF         │   - Rate Limiting      │
│  - DomainService  │               │                         │
└───────────────────┴───────────────┴─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
├───────────────────┬───────────────┬─────────────────────────┤
│  Database         │  File Storage │   External APIs         │
│  - MySQL/Postgres  │  - ML Models  │   - SerpAPI            │
│  - Redis Cache    │  - Logs       │   - AbuseIPDB          │
└───────────────────┴───────────────┴─────────────────────────┘
```

### 3.3.2 Use Case Diagram

Use Case Diagram menggambarkan interaksi antara aktor (user) dengan sistem. Aktor utama dalam sistem ini adalah:

- **Admin**: Mengelola sistem secara keseluruhan
- **Staff**: Menggunakan sistem untuk scanning
- **Client/User**: Menggunakan sistem untuk scanning domain
- **System**: Sistem eksternal yang terintegrasi

**Use Case Utama:**

1. **Authentication Use Cases**
   - Login
   - Logout
   - Register
   - Manage Profile

2. **Scanning Use Cases**
   - Scan Domain
   - View Scan Progress
   - View Scan Results
   - View Scan History
   - Export Scan Results

3. **Admin Use Cases**
   - Manage Users
   - Manage Keywords
   - Manage Configuration
   - View Dashboard
   - Manage API Keys

4. **Mobile App Use Cases**
   - Scan Domain via Mobile
   - View Scan Results via Mobile
   - View History via Mobile
   - Login via Mobile

### 3.3.3 Sequence Diagram

Sequence Diagram menggambarkan alur interaksi antar komponen sistem untuk proses scanning domain:

**Alur Scanning Domain:**

```
User → Mobile App → REST API → ScanService → CoreScanner
                                      ↓
                              ML Model (Prediction)
                                      ↓
                              External APIs (SerpAPI)
                                      ↓
                              Database (Save Results)
                                      ↓
                              Cache (Store Progress)
                                      ↓
                              Mobile App (Display Results)
```

**Sequence Diagram Detail:**

1. User meminta scan domain melalui mobile app
2. Mobile app mengirim request ke REST API
3. REST API memvalidasi request dan authentication
4. ScanService membuat scan history dan memulai proses scanning
5. CoreScanner melakukan enumerasi subdomain
6. CoreScanner melakukan search menggunakan SerpAPI
7. CoreScanner melakukan verifikasi konten
8. ML Model melakukan prediksi konten malicious
9. CoreScanner melakukan graph analysis
10. CoreScanner menyimpan hasil ke database
11. CoreScanner menyimpan progress ke cache
12. REST API mengembalikan response ke mobile app
13. Mobile app menampilkan hasil kepada user

### 3.3.4 Entity Relationship Diagram (ERD)

ERD menggambarkan struktur database dan relasi antar entitas. Entitas utama dalam sistem:

**1. User (CustomUser)**
- id (Primary Key)
- username
- email
- password
- role (admin, staff, user)
- is_premium
- is_active
- date_joined

**2. ScanHistory**
- id (Primary Key)
- scan_id (Unique)
- user_id (Foreign Key → User)
- domain
- scan_type
- status
- start_time
- end_time
- scan_results_json
- error_message

**3. PermanentScanResult**
- id (Primary Key)
- scan_history_id (Foreign Key → ScanHistory, OneToOne)
- full_results_json
- total_items
- total_subdomains
- categories_detected
- created_at
- updated_at

**4. UserScanQuota**
- id (Primary Key)
- user_id (Foreign Key → User, OneToOne)
- quota_limit
- used_quota
- reset_period
- last_reset
- next_reset

**5. MaliciousKeyword**
- id (Primary Key)
- keyword
- category
- is_active
- created_at
- updated_at

**6. DomainScanSummary**
- id (Primary Key)
- domain
- total_scans
- last_scan_date
- risk_score
- malicious_pages_count

**7. ActivityLog**
- id (Primary Key)
- user_id (Foreign Key → User)
- action
- details
- timestamp

**8. ApiKey**
- id (Primary Key)
- key_name
- key_value
- is_active
- last_used
- created_at

**Relasi:**
- User 1:N ScanHistory
- User 1:1 UserScanQuota
- User 1:N ActivityLog
- ScanHistory 1:1 PermanentScanResult (untuk premium user)
- DomainScanSummary memiliki relasi implicit dengan ScanHistory melalui domain

### 3.3.5 Database Design

**Tabel-tabel utama:**

**1. Tabel users (CustomUser)**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_premium BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**2. Tabel scan_history**
```sql
CREATE TABLE scan_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scan_id VARCHAR(36) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    scan_results_json LONGTEXT,
    error_message TEXT,
    ran_with_verification BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_scan_id (scan_id),
    INDEX idx_user_id (user_id),
    INDEX idx_domain (domain),
    INDEX idx_status (status)
);
```

**3. Tabel permanent_scan_result**
```sql
CREATE TABLE permanent_scan_result (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scan_history_id INT UNIQUE NOT NULL,
    full_results_json JSON NOT NULL,
    total_items INT DEFAULT 0,
    total_subdomains INT DEFAULT 0,
    categories_detected JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_history_id) REFERENCES scan_history(id) ON DELETE CASCADE,
    INDEX idx_scan_history_id (scan_history_id)
);
```

**4. Tabel user_scan_quota**
```sql
CREATE TABLE user_scan_quota (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    quota_limit INT DEFAULT 0,
    used_quota INT DEFAULT 0,
    reset_period VARCHAR(20) DEFAULT 'monthly',
    last_reset DATETIME,
    next_reset DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);
```

**5. Tabel malicious_keyword**
```sql
CREATE TABLE malicious_keyword (
    id INT PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
);
```

---

## 3.4 Perancangan Machine Learning Model

### 3.4.1 Dataset Preparation

**Sumber Dataset:**
- Domain pendidikan (.ac.id) yang aman (dari universitas terpercaya)
- Domain pendidikan yang terindikasi konten malicious (dari observasi dan penelitian)
- Domain umum (.com, .org) sebagai pembanding

**Preprocessing Dataset:**
1. **Data Cleaning**
   - Menghapus duplikasi
   - Menghapus data yang tidak valid
   - Normalisasi format data

2. **Data Labeling**
   - Label 0: Aman
   - Label 1: Hack Judol (Judi Online)
   - Label 2: Pornografi
   - Label 3: Hacked (Domain yang diretas)
   - Label 4: Narkoba (jika ada dalam dataset)

3. **Data Splitting**
   - Training Set: 70%
   - Validation Set: 15%
   - Test Set: 15%

### 3.4.2 Feature Extraction

**1. TF-IDF Vectorization**
- Menggunakan TF-IDF untuk mengekstrak fitur dari teks konten
- Menggunakan Sastrawi untuk stemming bahasa Indonesia
- Menggunakan stop words removal untuk bahasa Indonesia
- Max features: 5000-10000

**2. Preprocessing Text**
- Lowercasing
- Removing special characters
- Removing stop words
- Stemming menggunakan Sastrawi
- Tokenization

**3. Feature Engineering**
- Ekstraksi keyword malicious
- Ekstraksi domain characteristics
- Ekstraksi URL patterns
- Ekstraksi meta tags

### 3.4.3 Model Selection dan Training

**Algoritma yang Digunakan:**

**1. Support Vector Machine (SVM)**
- Kernel: RBF (Radial Basis Function)
- C parameter: 1.0
- Gamma: 'scale'
- Hyperparameter tuning menggunakan GridSearchCV

**2. Naive Bayes**
- Variant: Multinomial Naive Bayes
- Alpha: 1.0 (Laplace smoothing)
- Fit prior: True

**3. Random Forest**
- Number of estimators: 100-200
- Max depth: None
- Min samples split: 2
- Min samples leaf: 1
- Hyperparameter tuning menggunakan RandomSearchCV

**Training Process:**
1. Load dan preprocessing dataset
2. Feature extraction menggunakan TF-IDF
3. Split data menjadi training, validation, dan test set
4. Train masing-masing model
5. Hyperparameter tuning untuk model terbaik
6. Evaluasi menggunakan validation set
7. Final evaluation menggunakan test set

### 3.4.4 Model Evaluation

**Metrik Evaluasi:**
- **Accuracy**: Proporsi prediksi yang benar
- **Precision**: Proporsi prediksi positif yang benar
- **Recall**: Proporsi positif aktual yang terdeteksi
- **F1-Score**: Harmonic mean dari precision dan recall
- **Confusion Matrix**: Matrix untuk melihat distribusi prediksi

**Classification Report:**
- Per class metrics (Precision, Recall, F1-Score)
- Macro average
- Weighted average

**Model Selection:**
- Model dengan akurasi tertinggi dipilih
- Model dengan F1-Score tertinggi dipilih
- Model dengan balance terbaik antara precision dan recall dipilih

**Model Persistence:**
- Model terpilih disimpan menggunakan joblib
- TF-IDF vectorizer disimpan terpisah
- Label mapping disimpan untuk interpretasi hasil

---

## 3.5 Implementasi

### 3.5.1 Environment Setup

**Backend Environment:**
- Python 3.9+
- Django 5.2.7
- Django REST Framework 3.14+
- MySQL/PostgreSQL 8.0+
- Redis (untuk caching)
- Virtual environment (venv)

**Machine Learning Environment:**
- scikit-learn 1.3+
- pandas 2.0+
- numpy 1.24+
- joblib (untuk model persistence)
- Sastrawi (untuk stemming Indonesia)

**Mobile Environment:**
- Flutter SDK 3.0+
- Dart 3.0+
- Android Studio / VS Code
- Android SDK (untuk Android development)

### 3.5.2 Backend Development (Django REST API)

**1. Project Structure**
```
sistem_deteksi_malicious/
├── scanner/
│   ├── models.py          # Database models
│   ├── views.py           # Web views
│   ├── services/          # Business logic
│   │   ├── scan_service.py
│   │   ├── quota_service.py
│   │   └── permanent_storage_service.py
│   ├── api/               # REST API
│   │   ├── views.py       # API viewsets
│   │   ├── serializers.py # Data serialization
│   │   └── urls.py        # API routing
│   ├── core_scanner.py    # Core scanning logic
│   └── utils/             # Utilities
├── manage.py
└── requirements.txt
```

**2. Implementasi Authentication**
- Token-based authentication menggunakan Django REST Framework
- Custom user model dengan role dan premium status
- Permission classes untuk role-based access control

**3. Implementasi Scan Service**
- Service layer untuk business logic scanning
- Integrasi dengan core_scanner.py
- Integrasi dengan machine learning model
- Progress tracking menggunakan cache
- Error handling dan logging

**4. Implementasi API Endpoints**
- `/api/scans/` - CRUD scan history
- `/api/scans/{id}/results/` - Get scan results
- `/api/scans/{id}/progress/` - Get scan progress
- `/api/scans/my_scans/` - Get user's scans
- `/api/users/profile/` - Get user profile
- `/api/users/quota_status/` - Get quota status
- `/api/auth/login/` - Authentication

**5. Implementasi Caching System**
- Redis untuk caching hasil scan
- Cache untuk progress tracking
- Cache untuk API responses
- Cache untuk domain intelligence

### 3.5.3 Model Machine Learning Integration

**1. Model Loading**
- Load model menggunakan joblib
- Load TF-IDF vectorizer
- Load label mapping

**2. Prediction Service**
- Service untuk melakukan prediksi konten
- Input: konten teks dari website
- Output: label dan confidence score
- Batch prediction untuk efisiensi

**3. Integration dengan Scan Service**
- Prediksi dilakukan saat scanning
- Hasil prediksi disimpan dalam scan results
- Confidence score digunakan untuk ranking

### 3.5.4 Mobile Application Development (Flutter)

**1. Project Structure**
```
lib/
├── models/
│   ├── scan_result.dart
│   └── user.dart
├── services/
│   └── api_service.dart
├── providers/
│   ├── scan_provider.dart
│   └── auth_provider.dart
├── screens/
│   ├── login_screen.dart
│   ├── scan_screen.dart
│   ├── history_screen.dart
│   └── results_screen.dart
└── main.dart
```

**2. State Management**
- Menggunakan Provider untuk state management
- Providers untuk scan, authentication, dan user data

**3. API Integration**
- HTTP client untuk komunikasi dengan REST API
- Token management untuk authentication
- Error handling dan retry logic

**4. UI/UX Implementation**
- Material Design untuk konsistensi
- Responsive design untuk berbagai ukuran layar
- Loading states dan error handling
- Real-time progress updates

---

## 3.6 Pengujian Sistem

### 3.6.1 Pengujian Unit Testing

**Backend Unit Testing:**
- Testing service layer functions
- Testing model methods
- Testing utility functions
- Testing API serializers

**Mobile Unit Testing:**
- Testing model classes
- Testing service functions
- Testing provider logic

### 3.6.2 Pengujian Integration Testing

**Backend Integration Testing:**
- Testing API endpoints
- Testing database operations
- Testing cache operations
- Testing ML model integration

**Mobile Integration Testing:**
- Testing API integration
- Testing state management
- Testing navigation flow

### 3.6.3 Pengujian Model Machine Learning

**Testing Model Performance:**
- Testing dengan test dataset
- Testing dengan data baru (domain yang belum pernah di-scan)
- Testing dengan berbagai jenis konten malicious
- Testing dengan domain aman

**Metrics Testing:**
- Accuracy testing
- Precision dan Recall testing
- F1-Score testing
- Confusion matrix analysis

### 3.6.4 Pengujian User Acceptance Testing (UAT)

**Scenario Testing:**
- User melakukan scanning domain pendidikan
- User melihat hasil scan
- User melihat history scan
- Admin mengelola keywords
- Admin mengelola users

**Usability Testing:**
- Kemudahan penggunaan aplikasi mobile
- Kejelasan tampilan hasil scan
- Kecepatan loading
- Error handling yang user-friendly

**Performance Testing:**
- Response time API
- Time to complete scan
- Memory usage
- Battery consumption (mobile app)

**Security Testing:**
- Authentication testing
- Authorization testing
- Input validation testing
- SQL injection testing
- XSS testing

---

## 3.7 Tools dan Teknologi yang Digunakan

### 3.7.1 Development Tools
- **IDE**: PyCharm, VS Code, Android Studio
- **Version Control**: Git
- **API Testing**: Postman
- **Database Management**: MySQL Workbench, pgAdmin
- **Documentation**: Markdown, Swagger

### 3.7.2 Testing Tools
- **Unit Testing**: Django TestCase, Flutter Test
- **API Testing**: Postman, REST Client
- **Performance Testing**: Apache JMeter (optional)
- **Code Quality**: Pylint, Flutter Analyzer

### 3.7.3 Deployment Tools
- **Web Server**: Gunicorn, Nginx
- **Database**: MySQL/PostgreSQL
- **Cache**: Redis
- **Monitoring**: Django logging, custom monitoring

---

Bab ini menjelaskan metodologi yang digunakan dalam penelitian ini, mulai dari metodologi pengembangan sistem hingga pengujian. Metodologi yang digunakan dirancang untuk memastikan sistem dapat dikembangkan dengan baik, diuji secara menyeluruh, dan dapat memenuhi kebutuhan pengguna.

