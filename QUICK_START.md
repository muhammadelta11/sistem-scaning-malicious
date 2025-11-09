# Quick Start Guide

## Setup dan Running

### 1. Aktifkan Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies (jika belum)

```bash
pip install -r requirements.txt
```

### 3. Setup Database

```bash
python manage.py migrate
```

### 4. Create Superuser (jika belum ada)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

### 6. Akses Aplikasi

- Web UI: http://localhost:8000/scanner/
- API Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Troubleshooting

### Error: No module named 'django'
**Solusi:** Pastikan virtual environment sudah diaktifkan

### Error: No module named 'debug_toolbar'
**Solusi:** Ini normal, debug_toolbar sudah di-disable (tidak diperlukan)

### Error: ModuleNotFoundError: No module named 'eventlet'
**Solusi:** Sudah diperbaiki, eventlet sudah dihapus dari manage.py

### Error Database Connection
**Solusi:** Pastikan MySQL running dan konfigurasi di `.env` benar

## Environment Variables

Buat file `.env` di root project dengan konfigurasi:

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

