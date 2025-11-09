# Panduan Deployment Production

Panduan lengkap untuk meng-host Django backend dan mengupload Android app ke Play Store.

## 📋 Daftar Isi

1. [Persiapan Django Backend untuk Production](#1-persiapan-django-backend-untuk-production)
2. [Konfigurasi Flutter App untuk Production](#2-konfigurasi-flutter-app-untuk-production)
3. [Build Release APK/AAB](#3-build-release-apk-aab)
4. [Upload ke Google Play Store](#4-upload-ke-google-play-store)
5. [Konfigurasi CORS di Django](#5-konfigurasi-cors-di-django)
6. [SSL/HTTPS Setup](#6-sslhttps-setup)

---

## 1. Persiapan Django Backend untuk Production

### 1.1 Update Settings.py

Edit file `settings.py` Django Anda:

```python
# settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Set ke False untuk production

ALLOWED_HOSTS = [
    'your-domain.com',
    'www.your-domain.com',
    'api.your-domain.com',  # Jika menggunakan subdomain
    # Tambahkan IP server Anda juga jika perlu
]

# Database (gunakan PostgreSQL untuk production, bukan SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files (untuk production)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings untuk production
SECURE_SSL_REDIRECT = True  # Redirect HTTP ke HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    # Tambahkan origin lain jika perlu
]

# Atau jika ingin mengizinkan semua origin (kurang aman, tapi untuk testing OK)
# CORS_ALLOW_ALL_ORIGINS = True  # HATI-HATI: Gunakan ini hanya untuk development!

# Untuk mobile app, kita perlu mengizinkan semua origin karena tidak ada specific origin
CORS_ALLOW_ALL_ORIGINS = True  # Mobile apps tidak punya origin seperti browser
CORS_ALLOW_CREDENTIALS = True

# CORS Headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CORS Methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

### 1.2 Install Dependencies untuk Production

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Install gunicorn untuk production server
pip install gunicorn

# Install whitenoise untuk static files
pip install whitenoise

# Update requirements.txt
pip freeze > requirements.txt
```

### 1.3 Setup Gunicorn

Buat file `gunicorn_config.py`:

```python
# gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

Jalankan dengan:
```bash
gunicorn --config gunicorn_config.py your_project.wsgi:application
```

### 1.4 Setup Nginx sebagai Reverse Proxy (Opsional tapi Disarankan)

File konfigurasi Nginx (`/etc/nginx/sites-available/your-project`):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
```

---

## 2. Konfigurasi Flutter App untuk Production

### 2.1 Update config.dart

Edit file `seo_poisoning/lib/config.dart`:

```dart
class Config {
  // DEVELOPMENT
  static const String devApiBaseUrl = 'http://10.211.55.2:8000';
  
  // PRODUCTION - Ganti dengan URL production Django Anda
  static const String prodApiBaseUrl = 'https://your-domain.com';
  
  // PENTING: Set ke false untuk production build!
  static const bool isDevelopment = false; // <-- UBAH KE FALSE
  
  static String get apiBaseUrl {
    return isDevelopment ? devApiBaseUrl : prodApiBaseUrl;
  }
}
```

**⚠️ PENTING**: Pastikan `isDevelopment = false` sebelum build release APK/AAB!

### 2.2 Update Android Network Security Config

Edit file `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest ...>
    <application
        android:networkSecurityConfig="@xml/network_security_config"
        ...>
        ...
    </application>
</manifest>
```

Buat file `android/app/src/main/res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Untuk production, hanya izinkan HTTPS -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    
    <!-- Untuk development, izinkan HTTP juga -->
    <!-- 
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    -->
    
    <!-- Jika perlu izinkan domain tertentu untuk HTTP (development only) -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.211.55.2</domain>
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>
    </domain-config>
</network-security-config>
```

---

## 3. Build Release APK/AAB

### 3.1 Update Version

Edit `pubspec.yaml`:

```yaml
version: 1.0.0+1  # Format: version+build_number
```

### 3.2 Build App Bundle (AAB) untuk Play Store

```bash
# Masuk ke folder Flutter project
cd seo_poisoning

# Build release app bundle
flutter build appbundle --release

# File akan ada di: build/app/outputs/bundle/release/app-release.aab
```

### 3.3 Build APK (Opsional - untuk distribusi langsung)

```bash
flutter build apk --release

# Atau split APK per ABI (ukuran lebih kecil)
flutter build apk --split-per-abi --release
```

### 3.4 Sign APK/AAB

Jika belum dikonfigurasi, buat file `android/key.properties`:

```properties
storePassword=your_keystore_password
keyPassword=your_key_password
keyAlias=your_key_alias
storeFile=path/to/your/keystore.jks
```

Buat keystore:
```bash
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

Edit `android/app/build.gradle.kts`:

```kotlin
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    ...
    
    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties['keyAlias']
            keyPassword = keystoreProperties['keyPassword']
            storeFile = keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword = keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

---

## 4. Upload ke Google Play Store

1. **Buka Google Play Console**: https://play.google.com/console
2. **Buat aplikasi baru** atau pilih aplikasi yang sudah ada
3. **Upload AAB**:
   - Pilih "Production" atau "Internal testing"
   - Upload file `app-release.aab`
4. **Isi informasi aplikasi**:
   - Nama aplikasi
   - Deskripsi pendek dan panjang
   - Screenshots
   - Icon aplikasi
   - Privacy policy URL (wajib untuk beberapa tipe aplikasi)
5. **Content rating**: Isi kuesioner rating konten
6. **Pricing & distribution**: Pilih gratis atau berbayar, negara distribusi
7. **Review**: Google akan mereview aplikasi Anda (biasanya 1-7 hari)

---

## 5. Konfigurasi CORS di Django

Untuk production dengan mobile app, kita perlu mengizinkan semua origin karena mobile app tidak punya origin seperti browser web.

File `settings.py`:

```python
# CORS untuk mobile app
CORS_ALLOW_ALL_ORIGINS = True  # OK untuk mobile app
CORS_ALLOW_CREDENTIALS = True

# Atau lebih aman, izinkan hanya untuk domain tertentu
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
]
```

---

## 6. SSL/HTTPS Setup

### 6.1 Gunakan Let's Encrypt (Gratis)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (akan otomatis di-setup)
sudo certbot renew --dry-run
```

### 6.2 Atau Gunakan Cloudflare (Lebih Mudah)

1. Daftar di Cloudflare
2. Tambahkan domain Anda
3. Update nameserver domain ke Cloudflare
4. Aktifkan SSL/TLS (Full atau Full Strict)
5. Cloudflare akan menangani SSL secara otomatis

---

## ✅ Checklist Sebelum Release

- [ ] Django `DEBUG = False`
- [ ] `ALLOWED_HOSTS` sudah dikonfigurasi
- [ ] Database production (PostgreSQL) sudah setup
- [ ] Static files sudah dikumpulkan (`python manage.py collectstatic`)
- [ ] SSL/HTTPS sudah aktif
- [ ] CORS sudah dikonfigurasi
- [ ] Flutter `isDevelopment = false`
- [ ] Network security config Android sudah benar
- [ ] Aplikasi sudah ditest di production environment
- [ ] Version dan build number sudah diupdate
- [ ] APK/AAB sudah di-sign
- [ ] Testing release build di device fisik

---

## 🔧 Troubleshooting

### Issue: App tidak bisa connect ke API

1. **Cek URL production** di `config.dart`
2. **Cek SSL certificate** - pastikan valid
3. **Cek CORS** - pastikan mengizinkan semua origin
4. **Cek firewall** - pastikan port 443 (HTTPS) terbuka

### Issue: SSL Certificate Error di Android

1. **Pastikan menggunakan HTTPS** (bukan HTTP)
2. **Pastikan certificate valid** dan tidak expired
3. **Untuk development**, izinkan HTTP di `network_security_config.xml`

### Issue: CORS Error

1. **Pastikan `CORS_ALLOW_ALL_ORIGINS = True`** untuk mobile app
2. **Atau tambahkan origin** ke `CORS_ALLOWED_ORIGINS`

---

## 📞 Support

Jika ada masalah, cek:
1. Django logs: `tail -f /var/log/gunicorn/error.log`
2. Nginx logs: `tail -f /var/log/nginx/error.log`
3. Flutter logs: `flutter logs`

---

**Selamat deploy! 🚀**

