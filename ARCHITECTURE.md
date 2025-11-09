# Architecture Overview

Dokumen ini menjelaskan arsitektur sistem yang telah direstrukturisasi.

## 🏗️ Struktur Baru

### Service Layer
Semua business logic dipindahkan ke service layer untuk memisahkan concerns:

- **ScanService**: Menangani operasi scanning domain
- **DomainService**: Menangani operasi domain (intelligence, subdomain enumeration)
- **KeywordService**: Menangani CRUD operations untuk keywords
- **UserService**: Menangani operasi user management

### API Layer
API endpoints menggunakan Django REST Framework:

- **ViewSets**: Untuk operasi CRUD standard
- **Custom Actions**: Untuk operasi khusus seperti progress tracking
- **Serializers**: Untuk validasi dan serialization data

### Middleware
Custom middleware untuk:

- **Rate Limiting**: Proteksi dari abuse (100 requests per 60 detik)
- **Request Logging**: Tracking semua request dan response

### Exception Handling
Custom exceptions untuk error handling yang lebih baik:

- `DomainValidationError`: Domain tidak valid
- `APIKeyError`: API key error
- `ScanProcessingError`: Error saat processing scan
- `RateLimitExceeded`: Rate limit terlampaui
- `ResourceNotFound`: Resource tidak ditemukan
- `PermissionDenied`: Permission ditolak

### Settings Modular
Settings dipisah berdasarkan environment:

- **base.py**: Settings yang umum untuk semua environment
- **development.py**: Settings khusus development
- **production.py**: Settings khusus production dengan security features

## 📊 Flow Diagram

```
User Request
    ↓
URL Routing (urls.py)
    ↓
View (views.py / api/views.py)
    ↓
Service Layer (services/*.py)
    ↓
Core Logic (core_scanner.py)
    ↓
Database / External APIs
```

## 🔄 API Request Flow

```
1. Client → API Endpoint
2. Authentication Check (IsAuthenticated)
3. Permission Check (IsAdminUser if needed)
4. Rate Limiting Check
5. Request Logging
6. Service Layer Processing
7. Response Serialization
8. Return JSON Response
```

## 🔐 Security Features

1. **Rate Limiting**: 100 requests per 60 detik per user
2. **Session Authentication**: Django session-based auth
3. **CSRF Protection**: Built-in Django CSRF protection
4. **Permission Checks**: Role-based access control
5. **Secure Cookies**: Untuk production environment
6. **SSL Redirect**: Untuk production environment

## 📝 Best Practices

1. **Separation of Concerns**: Business logic di service layer, bukan di views
2. **Error Handling**: Gunakan custom exceptions untuk error handling yang lebih baik
3. **Logging**: Semua operasi penting di-log
4. **Validation**: Validasi input di serializer/form dan service layer
5. **Caching**: Gunakan Redis untuk caching
6. **Documentation**: API documentation dengan drf-spectacular

## 🚀 Deployment

Untuk production:

1. Set environment variable: `DJANGO_ENVIRONMENT=production`
2. Update `ALLOWED_HOSTS` di `.env`
3. Setup SSL certificates
4. Configure email backend
5. Setup proper logging
6. Run migrations
7. Collect static files: `python manage.py collectstatic`
8. Setup Celery workers (optional)

