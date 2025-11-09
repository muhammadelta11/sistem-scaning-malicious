# Sistem Deteksi Domain Malicious

Sistem profesional untuk mendeteksi domain yang terindikasi malicious content menggunakan Django dan teknologi modern.

## 🎉 Major Updates v2.0

### ✅ Dynamic Configuration System
**Semua konfigurasi sekarang bisa diubah dari UI tanpa edit code!**

- ⚙️ Web-based configuration management
- 🔌 REST API untuk mobile apps  
- 💾 Config tersimpan di database (dinamis)
- 📊 20+ konfigurasi yang fleksibel
- 🔄 Real-time effect (no restart)

**File Baru:**
- `KONFIGURASI_SISTEM.md` - Panduan lengkap konfigurasi
- `README_API.md` - API documentation untuk mobile

**Model Baru:**
- `SistemConfig` - Singleton model untuk semua konfigurasi

## 🚀 Fitur Utama

- **Scanning Domain Multi-Source**: Google Search (dengan caching), Bing (optional), DuckDuckGo
- **Deteksi Konten Ilegal Komprehensif**: Narkoba, penipuan, phishing, terorisme, pemalsuan, dll
- **Verifikasi Real-Time**: Validasi konten langsung dari website target
- **Graph Analysis**: Analisis struktur website untuk menemukan orphan pages dan isolated clusters
- **Subdomain Enumeration**: Deteksi subdomain yang terindikasi (DNS-based, gratis)
- **Deep Content Detection**: Deteksi konten tersembunyi, injeksi, dan halaman tidak terindex
- **API Cache System**: Hemat 95% quota SerpAPI dengan intelligent caching
- **API RESTful**: Endpoint lengkap dengan dokumentasi Swagger
- **Rate Limiting**: Proteksi dari abuse dengan rate limiting
- **Logging & Monitoring**: Tracking aktivitas dan audit log
- **Multi-User Support**: Role-based access control

## 📋 Requirements

- Python 3.9+
- MySQL 8.0+
- Redis (untuk cache dan Celery)
- Chrome/Chromium (untuk Selenium)

## 🔧 Instalasi

1. **Clone repository**
```bash
git clone <repository-url>
cd sistem_deteksi_malicious
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
Buat file `.env` di root project:
```env
SECRET_KEY=your-secret-key-here
SERPAPI_API_KEY=your-serpapi-key
DB_NAME=sistem_deteksi
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
DJANGO_ENVIRONMENT=development
```

4. **Setup database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Run development server**
```bash
python manage.py runserver
```

## 🏗️ Struktur Project

```
sistem_deteksi_malicious/
├── scanner/
│   ├── api/              # REST API endpoints
│   ├── services/        # Business logic layer
│   ├── utils/           # Utility functions
│   ├── middleware/      # Custom middleware
│   ├── models.py        # Database models
│   ├── views.py         # Template views
│   └── forms.py         # Django forms
├── sistem_deteksi_malicious/
│   ├── settings/        # Modular settings
│   │   ├── base.py      # Base settings
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py          # URL routing
└── requirements.txt
```

## 🆕 Quick Start - Konfigurasi Sistem

### Untuk Admin
1. Login sebagai admin
2. Buka menu **Konfigurasi**
3. Edit pengaturan sesuai kebutuhan
4. Simpan perubahan

### Via API
```bash
# Lihat config saat ini
curl -X GET http://localhost:8000/api/config/active/ \
  -H "Authorization: Token YOUR_TOKEN"

# Update config
curl -X PATCH http://localhost:8000/api/config/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"max_search_results": 150}'
```

### Preset Recommended
- **Hemat Maksimal**: ~2-4 API calls per scan (default)
- **Scan Lengkap**: ~20-30 API calls per scan  
- **Scan Cepat**: ~1-2 API calls per scan

📖 Lihat **[KONFIGURASI_SISTEM.md](KONFIGURASI_SISTEM.md)** untuk detail lengkap

## 📖 API Documentation

Setelah server berjalan, akses dokumentasi API:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/
- **📱 Mobile API Guide**: [README_API.md](README_API.md)

## 🔌 API Endpoints

### Authentication Required

- `POST /api/scans/` - Buat scan baru
- `GET /api/scans/` - Daftar semua scan milik user
- `GET /api/scans/{id}/` - Detail scan
- `GET /api/scans/{id}/results/` - Hasil scan
- `GET /api/scans/{id}/progress/` - Progress scan

### Admin Only

- `GET /api/config/active/` - Konfigurasi sistem
- `PATCH /api/config/{id}/` - Update konfigurasi
- `POST /api/config/reset_to_default/` - Reset ke default
- `GET /api/keywords/` - Daftar keywords
- `POST /api/keywords/` - Buat keyword baru
- `PUT /api/keywords/{id}/` - Update keyword
- `DELETE /api/keywords/{id}/` - Hapus keyword
- `POST /api/keywords/{id}/toggle/` - Toggle status keyword

## 🎯 Penggunaan

### Melakukan Scan Domain

1. Login ke sistem
2. Masuk ke halaman Scan
3. Masukkan domain target
4. Pilih tipe scan (Cepat atau Komprehensif)
5. Klik "Scan Domain"

### Via API

```bash
curl -X POST http://localhost:8000/api/scans/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your-session-id" \
  -d '{
    "domain": "example.com",
    "scan_type": "Komprehensif (Google + Crawling)",
    "enable_verification": true,
    "show_all_results": false
  }'
```

## 🔐 Security

- Session-based authentication
- CSRF protection
- Rate limiting (100 requests per 60 detik per user)
- Role-based access control
- Secure cookies untuk production

## 🧪 Testing

```bash
python manage.py test scanner
```

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Name Here]

---

**Note**: Sistem ini dirancang untuk penggunaan komersial dengan struktur yang scalable dan maintainable.

