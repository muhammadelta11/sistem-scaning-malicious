# Panduan Koneksi Django (Windows Parallels) ke Flutter App (macOS)

## Overview
Aplikasi Flutter di macOS perlu terhubung ke Django backend yang berjalan di Windows VM di Parallels Desktop.

## Langkah-langkah Setup

### 1. Dapatkan IP Address Windows VM di Parallels

#### Di Windows VM:
```powershell
# Buka PowerShell atau CMD di Windows VM
ipconfig

# Cari IPv4 Address, biasanya dalam format:
# 10.211.55.x atau 10.37.129.x
```

**Atau cara cepat:**
- Klik icon Network di system tray Windows
- Lihat IP address yang ditampilkan

#### Di macOS (Host):
```bash
# Check network interface yang terhubung ke Parallels
ifconfig | grep -A 5 "vnic"

# Atau gunakan:
ping 10.211.55.2  # Contoh IP Windows VM
```

### 2. Konfigurasi Django Server

Pastikan Django server listen di **0.0.0.0** (semua interface), bukan hanya localhost:

```python
# Di Windows VM, jalankan:
python manage.py runserver 0.0.0.0:8000
```

**Atau buat file `runserver_parallels.bat` di Windows:**
```batch
@echo off
python manage.py runserver 0.0.0.0:8000
pause
```

### 3. Update Config Flutter App

Edit file `seo_poisoning/lib/config.dart`:

```dart
class Config {
  // Untuk Parallels Desktop:
  // - IP Windows VM biasanya: 10.211.55.2 atau 10.37.129.2
  // - Ganti dengan IP Windows VM Anda yang sebenarnya
  
  // Contoh 1: Jika IP Windows VM adalah 10.211.55.2
  static const String apiBaseUrl = 'http://10.211.55.2:8000';
  
  // Contoh 2: Jika IP Windows VM adalah 10.37.129.2
  // static const String apiBaseUrl = 'http://10.37.129.2:8000';
  
  // Contoh 3: Jika menggunakan localhost (hanya untuk Android Emulator)
  // static const String apiBaseUrl = 'http://10.0.2.2:8000';
  
  // Note: Ganti IP di atas dengan IP Windows VM Anda yang sebenarnya!
}
```

### 4. Test Koneksi

#### Test dari macOS Terminal:
```bash
# Test apakah Django server bisa diakses
curl http://10.211.55.2:8000/api/

# Atau test health check
curl http://10.211.55.2:8000/api/auth/login/
```

#### Test dari Flutter App:
1. Pastikan Django server sudah running di Windows VM
2. Jalankan Flutter app
3. Coba login
4. Jika error, check console untuk error message

### 5. Troubleshooting

#### Masalah: Connection refused / Cannot connect

**Solusi 1: Check Firewall Windows**
```powershell
# Di Windows VM, buka Firewall
# Allow port 8000 untuk incoming connections
# Atau nonaktifkan firewall sementara untuk testing
```

**Solusi 2: Check Django ALLOWED_HOSTS**
Edit `sistem_deteksi_malicious/settings/base.py`:
```python
ALLOWED_HOSTS = ['*']  # Untuk development, gunakan '*'
# Atau spesifik:
# ALLOWED_HOSTS = ['10.211.55.2', 'localhost', '127.0.0.1']
```

**Solusi 3: Check Parallels Network Settings**
1. Buka Parallels Desktop > Preferences
2. Network tab
3. Pastikan "Shared Network" atau "Bridged Network" dipilih
4. Bukan "Host-Only Network" (lebih terbatas)

#### Masalah: Timeout

**Solusi:**
- Pastikan Windows VM dan macOS dalam network yang sama
- Check apakah Windows VM bisa ping ke macOS
- Pastikan port 8000 tidak blocked

#### Masalah: IP berubah setiap restart

**Solusi:**
- Set static IP di Windows VM:
  1. Network Settings > IPv4 > Manual
  2. Set IP tetap (misal: 10.211.55.100)
  3. Subnet: 255.255.255.0
  4. Gateway: 10.211.55.1

### 6. IP Address Parallels Desktop

Parallels Desktop biasanya menggunakan salah satu IP range berikut:

| Network Type | IP Range | Default Gateway |
|--------------|----------|-----------------|
| Shared Network | 10.211.55.x | 10.211.55.1 |
| Shared Network (alternatif) | 10.37.129.x | 10.37.129.1 |
| Bridged Network | IP dari router Anda | Router IP |

**Cara cek IP Windows VM:**
1. Di Windows VM: `ipconfig` → lihat IPv4 Address
2. Atau: Settings > Network & Internet > Wi‑Fi > Properties → IPv4 address

### 7. Testing Checklist

- [ ] Django server running di Windows VM dengan `0.0.0.0:8000`
- [ ] IP Windows VM sudah diketahui dan diupdate di `config.dart`
- [ ] Firewall Windows allow port 8000
- [ ] `ALLOWED_HOSTS` di Django settings sudah dikonfigurasi
- [ ] Test connection dari macOS terminal berhasil
- [ ] Flutter app bisa connect ke Django API

### 8. Quick Test Script

Buat file `test_connection.py` di Windows VM:
```python
import socket

def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Test localhost
    print("Testing localhost:8000...")
    if check_port('127.0.0.1', 8000):
        print("✓ Localhost OK")
    else:
        print("✗ Localhost FAILED")
    
    # Test all interfaces
    print("\nTesting 0.0.0.0:8000...")
    if check_port('0.0.0.0', 8000):
        print("✓ All interfaces OK")
    else:
        print("✗ All interfaces FAILED")
```

Jalankan setelah Django server started untuk verifikasi.

## Catatan Penting

⚠️ **Security Warning**: Konfigurasi di atas untuk **development only**.
- Untuk production, gunakan proper domain/IP dan security settings
- Jangan gunakan `ALLOWED_HOSTS = ['*']` di production
- Setup SSL/TLS untuk production

## Contoh Konfigurasi Lengkap

### Windows VM:
```powershell
# 1. Check IP
ipconfig
# Catat IPv4 Address, misal: 10.211.55.2

# 2. Start Django dengan 0.0.0.0
cd C:\laragon\www\sistem-deteksi-domain\sistem_deteksi_malicious
python manage.py runserver 0.0.0.0:8000
```

### macOS (Flutter):
```dart
// lib/config.dart
class Config {
  static const String apiBaseUrl = 'http://10.211.55.2:8000'; // Ganti dengan IP Windows VM
}
```

### Test:
```bash
# Di macOS terminal
curl http://10.211.55.2:8000/api/
```

Jika mendapat response JSON, berarti koneksi berhasil!

