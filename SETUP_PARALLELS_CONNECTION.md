# Panduan Koneksi Django (Windows Parallels) ke Flutter App (macOS)

## Ringkasan
Django server berjalan di Windows VM (Parallels Desktop) dan Flutter app berjalan di macOS host. Keduanya perlu terkoneksi via network.

## Langkah-langkah Setup

### 1. Dapatkan IP Address Windows VM

#### Di Windows VM, jalankan:
```powershell
ipconfig
```

**Cari IPv4 Address**, biasanya dalam format:
- `10.211.55.x` (Shared Network)
- `10.37.129.x` (Alternatif Shared Network)

**Contoh hasil:**
```
IPv4 Address. . . . . . . . . . . : 10.211.55.2
Subnet Mask . . . . . . . . . . . : 255.255.255.0
Default Gateway . . . . . . . . . : 10.211.55.1
```

**Catat IP ini!** (misal: `10.211.55.2`)

### 2. Start Django Server di Windows VM

Jalankan Django dengan bind ke **0.0.0.0** (semua interface):

```bash
# Di Windows VM
cd C:\laragon\www\sistem-deteksi-domain\sistem_deteksi_malicious
python manage.py runserver 0.0.0.0:8000
```

**Atau gunakan file batch yang sudah dibuat:**
```bash
# Double-click file: runserver_parallels.bat
```

Server akan listen di semua interface dan bisa diakses dari macOS.

### 3. Update Config Flutter App

Edit file `seo_poisoning/lib/config.dart`:

```dart
class Config {
  // Ganti dengan IP Windows VM Anda yang sebenarnya
  // Contoh: jika IP Windows VM adalah 10.211.55.2
  static const String apiBaseUrl = 'http://10.211.55.2:8000';
  
  // Atau jika IP Windows VM adalah 10.37.129.2
  // static const String apiBaseUrl = 'http://10.37.129.2:8000';
}
```

### 4. Test Koneksi

#### Test dari macOS Terminal:
```bash
# Ganti dengan IP Windows VM Anda
curl http://10.211.55.2:8000/api/

# Jika berhasil, akan mendapat response JSON
```

#### Test dari Flutter App:
1. Pastikan Django server sudah running di Windows VM
2. Build dan jalankan Flutter app
3. Coba login
4. Jika error, cek console untuk pesan error

### 5. Troubleshooting

#### ❌ Error: Connection refused

**Solusi 1: Check Firewall Windows**
- Buka Windows Firewall
- Allow port 8000 untuk incoming connections
- Atau nonaktifkan firewall sementara untuk testing

**Solusi 2: Pastikan Django running dengan 0.0.0.0**
```bash
# HARUS: python manage.py runserver 0.0.0.0:8000
# BUKAN: python manage.py runserver 8000 (hanya localhost)
# BUKAN: python manage.py runserver localhost:8000
```

#### ❌ Error: DisallowedHost / Invalid Host Header

**Solusi:**
Django settings sudah dikonfigurasi dengan `ALLOWED_HOSTS = ['*']` untuk development.
Jika masih error, pastikan file `sistem_deteksi_malicious/settings/base.py` berisi:
```python
ALLOWED_HOSTS = ['*']  # Untuk development
```

#### ❌ Error: Timeout

**Solusi:**
1. Pastikan Windows VM dan macOS dalam network yang sama
2. Test ping dari Windows VM ke macOS:
   ```powershell
   ping [MACOS_IP]
   ```
3. Test ping dari macOS ke Windows VM:
   ```bash
   ping 10.211.55.2  # Ganti dengan IP Windows VM
   ```

#### ❌ Error: CSRF token missing

**Solusi:**
API menggunakan Token Authentication, bukan session-based.
Pastikan mobile app mengirim header:
```
Authorization: Token <your-token>
```

### 6. Quick Checklist

- [ ] IP Windows VM sudah diketahui (cek dengan `ipconfig`)
- [ ] Django server running dengan `0.0.0.0:8000`
- [ ] Config Flutter app sudah diupdate dengan IP Windows VM
- [ ] Firewall Windows allow port 8000
- [ ] Test connection dari macOS terminal berhasil
- [ ] Flutter app bisa connect

### 7. Contoh Konfigurasi Lengkap

#### Windows VM:
```powershell
# 1. Check IP
ipconfig
# Result: IPv4 Address: 10.211.55.2

# 2. Start Django
cd C:\laragon\www\sistem-deteksi-domain\sistem_deteksi_malicious
python manage.py runserver 0.0.0.0:8000
```

#### macOS Flutter:
```dart
// lib/config.dart
class Config {
  static const String apiBaseUrl = 'http://10.211.55.2:8000';
}
```

#### Test:
```bash
# Di macOS terminal
curl http://10.211.55.2:8000/api/
```

Jika mendapat response JSON, koneksi berhasil! ✅

## Catatan Penting

⚠️ **Security Warning:**
- Konfigurasi `ALLOWED_HOSTS = ['*']` hanya untuk **development**
- Untuk production, gunakan IP/domain spesifik
- Setup SSL/TLS untuk production

🔧 **Tips:**
- Jika IP Windows VM berubah setiap restart, set static IP di Windows VM
- Gunakan IP yang konsisten untuk kemudahan development

