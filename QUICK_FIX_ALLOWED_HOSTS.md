# Quick Fix: DisallowedHost Error

## Masalah
```
Header HTTP_HOST tidak valid: '10.211.55.3:8000'. 
Anda mungkin perlu menambahkan '10.211.55.3' ke ALLOWED_HOSTS.
```

## Solusi

### ✅ Sudah Diperbaiki:
File `sistem_deteksi_malicious/settings/development.py` sudah diupdate:
```python
ALLOWED_HOSTS = ['*']  # Untuk development dengan Parallels Desktop
```

### 🔄 Langkah-langkah:

1. **Restart Django Server** (PENTING!)
   ```bash
   # Stop Django server (Ctrl+C)
   # Kemudian start lagi:
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Verifikasi Settings**
   Pastikan Django menggunakan settings yang benar. Check dengan:
   ```bash
   python manage.py shell
   ```
   Lalu di shell:
   ```python
   from django.conf import settings
   print(settings.ALLOWED_HOSTS)
   ```
   Harus output: `['*']`

3. **Test Koneksi**
   ```bash
   # Dari macOS terminal:
   curl http://10.211.55.3:8000/api/
   ```

## Jika Masih Error:

### Check Settings yang Aktif
```bash
# Di Windows VM
python manage.py shell
```

```python
from django.conf import settings
import django
print(f"Django settings module: {settings.SETTINGS_MODULE}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"DEBUG: {settings.DEBUG}")
```

### Atau Set Langsung di Environment Variable
```bash
# Di Windows VM, sebelum start Django:
set DJANGO_SETTINGS_MODULE=sistem_deteksi_malicious.settings.development
python manage.py runserver 0.0.0.0:8000
```

### Atau Edit `.env` File
Buat/edit file `.env` di root project:
```
DEBUG=True
ALLOWED_HOSTS=*
```

## Catatan:
- **Restart Django server** setelah mengubah settings!
- Settings di `development.py` akan meng-override `base.py`
- `ALLOWED_HOSTS = ['*']` hanya untuk development, jangan digunakan di production

