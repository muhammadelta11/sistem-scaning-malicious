# Perbaikan Penyimpanan Hasil Scan ke Database

## 📋 Masalah yang Ditemukan

Berdasarkan analisis hasil scan, ditemukan masalah berikut:

1. **Data detail tidak tersimpan terstruktur**: Data hasil scan (URL, title, description, label) hanya disimpan sebagai JSON string di field `scan_results_json`, bukan sebagai tabel terpisah yang bisa di-query dengan mudah.

2. **Hanya jumlah yang disimpan**: `DomainScanSummary` hanya menyimpan jumlah-jumlah (total_cases, hack_judol, pornografi, hacked) tanpa detail URL, title, description, label yang ditemukan.

3. **Data hanya untuk premium user**: `PermanentScanResult` hanya tersedia untuk user premium, user biasa tidak bisa menyimpan data lengkap.

4. **Tidak ada model untuk subdomain**: Subdomain hasil scan juga hanya tersimpan di JSON, tidak ada tabel terpisah untuk tracking subdomain.

## ✅ Solusi yang Diimplementasikan

### 1. Model Baru

#### a. `ScanResultItem` Model
Model untuk menyimpan setiap item hasil scan secara terstruktur:
- **URL**: URL yang ditemukan
- **Title**: Title dari halaman
- **Description**: Description/snippet dari halaman
- **Label**: Label yang terdeteksi (hack judol, pornografi, dll)
- **Category Code & Name**: Kode dan nama kategori
- **Verification Status**: Status verifikasi (LIVE, CACHE_ONLY, VERIFIED_SAFE, dll)
- **Is Live / Is Cache Only**: Flag apakah halaman masih live atau hanya cache
- **Keywords Found**: List keywords yang ditemukan
- **Confidence Score & Risk Score**: Skor confidence dan risk
- **Source**: Sumber data (Google, Bing, dll)
- **JS Analysis**: Hasil analisis JavaScript (jika tersedia)

#### b. `ScanSubdomain` Model
Model untuk menyimpan setiap subdomain yang ditemukan:
- **Subdomain**: Nama subdomain
- **IP Address**: IP address subdomain
- **Status**: Status subdomain (ACTIVE, INACTIVE, UNKNOWN)
- **Discovery Method**: Teknik yang digunakan untuk menemukan subdomain
- **Scan History**: Relasi ke scan history

### 2. Service Baru

#### `ScanResultStorageService`
Service untuk menyimpan hasil scan secara terstruktur ke database:
- `save_scan_results()`: Menyimpan semua items dan subdomains dari hasil scan
- `get_scan_items()`: Mengambil items dengan filter opsional (label, verification_status)
- `get_scan_subdomains()`: Mengambil subdomains dengan filter opsional (status)

### 3. Integrasi dengan Proses Scan

Service `ScanResultStorageService` terintegrasi di:
- `scanner/tasks.py` - Celery task untuk async scan
- `scanner/job_runner.py` - Thread pool executor untuk sync scan

**Penting**: Service ini dijalankan untuk **SEMUA USER** (bukan hanya premium), sehingga semua user bisa menyimpan data lengkap hasil scan mereka.

### 4. Admin Interface

Model baru ditambahkan ke Django Admin:
- `ScanResultItemAdmin`: Interface untuk melihat dan mengelola scan result items
- `ScanSubdomainAdmin`: Interface untuk melihat dan mengelola scan subdomains

## 🚀 Cara Menggunakan

### 1. Jalankan Migration

```bash
python manage.py migrate scanner
```

Ini akan membuat tabel `scan_resultitem` dan `scansubdomain` di database.

### 2. Scan Otomatis Menyimpan Data

Setelah migration, setiap scan yang dilakukan akan otomatis menyimpan:
- Semua URL, title, description, label ke tabel `scan_resultitem`
- Semua subdomain ke tabel `scansubdomain`

Tidak perlu perubahan di kode scan - sudah terintegrasi otomatis!

### 3. Query Data Hasil Scan

#### Mengambil semua items dari scan tertentu:
```python
from scanner.models import ScanHistory, ScanResultItem

scan_history = ScanHistory.objects.get(scan_id='...')
items = ScanResultItem.objects.filter(scan_history=scan_history)

# Filter berdasarkan label
hack_judol_items = ScanResultItem.objects.filter(
    scan_history=scan_history,
    label='hack judol'
)

# Filter berdasarkan verification status
live_items = ScanResultItem.objects.filter(
    scan_history=scan_history,
    verification_status='LIVE'
)
```

#### Mengambil semua subdomains dari scan tertentu:
```python
from scanner.models import ScanHistory, ScanSubdomain

scan_history = ScanHistory.objects.get(scan_id='...')
subdomains = ScanSubdomain.objects.filter(scan_history=scan_history)

# Filter berdasarkan status
active_subdomains = ScanSubdomain.objects.filter(
    scan_history=scan_history,
    status='ACTIVE'
)
```

### 4. Menggunakan Service

```python
from scanner.services.scan_result_storage_service import ScanResultStorageService
from scanner.models import ScanHistory

scan_history = ScanHistory.objects.get(scan_id='...')

# Ambil items dengan filter
items = ScanResultStorageService.get_scan_items(
    scan_history,
    label='hack judol',
    verification_status='LIVE'
)

# Ambil subdomains dengan filter
subdomains = ScanResultStorageService.get_scan_subdomains(
    scan_history,
    status='ACTIVE'
)
```

## 📊 Struktur Database

### Tabel `scan_resultitem`
- `id` (PK)
- `scan_history_id` (FK ke `scanhistory`)
- `url` (URLField)
- `title` (TextField)
- `description` (TextField)
- `label` (CharField)
- `category_code` (CharField)
- `category_name` (CharField)
- `verification_status` (CharField)
- `is_live` (BooleanField)
- `is_cache_only` (BooleanField)
- `keywords_found` (JSONField)
- `confidence_score` (FloatField)
- `risk_score` (IntegerField)
- `source` (CharField)
- `discovered_at` (DateTimeField)
- `js_analysis` (JSONField)

**Indexes**:
- `(scan_history, label)`
- `(scan_history, verification_status)`
- `(url)`
- `(is_live, label)`

### Tabel `scansubdomain`
- `id` (PK)
- `scan_history_id` (FK ke `scanhistory`)
- `subdomain` (CharField)
- `ip_address` (GenericIPAddressField)
- `status` (CharField)
- `discovery_method` (CharField)
- `discovered_at` (DateTimeField)

**Unique Constraint**: `(scan_history, subdomain)`

**Indexes**:
- `(scan_history, status)`
- `(subdomain)`

## 🔍 Contoh Hasil

Setelah scan selesai, data akan tersimpan seperti ini:

### ScanResultItem
```
URL: https://example.com/slot-gacor
Title: Slot Thailand # Bandar Link Slot Gacor Terbaik
Description: Slot Thailand merupakan bandar link slot gacor...
Label: hack judol
Category Code: 1
Category Name: Hack Judol
Verification Status: LIVE
Is Live: True
Is Cache Only: False
Keywords Found: ['slot', 'gacor', 'deposit pulsa']
Risk Score: 85
```

### ScanSubdomain
```
Subdomain: pmb.unwahas.ac.id
IP Address: 103.178.172.40
Status: ACTIVE
Discovery Method: dns_lookup
```

## ⚠️ Catatan Penting

1. **Backward Compatibility**: Data lama yang sudah tersimpan di `scan_results_json` tetap bisa diakses. Model baru hanya menambahkan penyimpanan terstruktur untuk scan baru.

2. **Performance**: Penggunaan `bulk_create` untuk efisiensi saat menyimpan banyak items sekaligus.

3. **Error Handling**: Jika penyimpanan terstruktur gagal, scan tetap dianggap berhasil (hanya log error). Data tetap tersimpan di `scan_results_json`.

4. **Data Duplikasi**: Data tersimpan di dua tempat:
   - `scan_results_json` (JSON string) - untuk backward compatibility
   - `ScanResultItem` & `ScanSubdomain` (tabel terpisah) - untuk query dan analisis yang lebih mudah

## 📝 File yang Diubah/Ditambahkan

1. **Model**: `scanner/models.py`
   - Ditambahkan `ScanResultItem` model
   - Ditambahkan `ScanSubdomain` model

2. **Service**: `scanner/services/scan_result_storage_service.py` (baru)
   - Service untuk menyimpan dan mengambil data hasil scan

3. **Tasks**: `scanner/tasks.py`
   - Ditambahkan call ke `ScanResultStorageService.save_scan_results()`

4. **Job Runner**: `scanner/job_runner.py`
   - Ditambahkan call ke `ScanResultStorageService.save_scan_results()`

5. **Admin**: `scanner/admin.py`
   - Ditambahkan `ScanResultItemAdmin`
   - Ditambahkan `ScanSubdomainAdmin`

6. **Migration**: `scanner/migrations/0018_scanresultitem_scansubdomain.py` (baru)
   - Migration untuk membuat tabel baru

## 🎯 Keuntungan

1. **Query yang Lebih Mudah**: Bisa query langsung berdasarkan URL, label, verification status, dll tanpa harus parse JSON.

2. **Analisis yang Lebih Baik**: Bisa melakukan analisis statistik, filtering, dan reporting yang lebih mudah.

3. **Akses untuk Semua User**: Semua user (bukan hanya premium) bisa menyimpan data lengkap hasil scan mereka.

4. **Tracking Subdomain**: Bisa tracking subdomain yang ditemukan secara terpisah dan mudah.

5. **Performance**: Query ke tabel terstruktur lebih cepat daripada query ke JSON field.

## 🔄 Langkah Selanjutnya

1. **Jalankan Migration**: `python manage.py migrate scanner`
2. **Test Scan**: Lakukan scan baru dan verifikasi data tersimpan di tabel baru
3. **Update Views**: Update views untuk menampilkan data dari model baru (opsional)
4. **Backfill Data**: Jika perlu, buat script untuk backfill data lama dari JSON ke tabel baru (opsional)

