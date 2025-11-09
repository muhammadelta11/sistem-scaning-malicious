# 🚀 Quick Start - Konfigurasi Sistem v2.0

## Pendahuluan

Sistem deteksi malicious domain sekarang memiliki **Dynamic Configuration System** yang memungkinkan Anda mengubah semua pengaturan melalui UI tanpa perlu edit code!

## ✅ Yang Sudah Diperbaiki

### 1. ✅ Preset Active Indicator
**Masalah**: Tidak bisa tahu preset mana yang aktif  
**Solusi**: 
- Badge "Preset Aktif" di bagian atas
- Highlight border pada preset aktif (border-3)
- Checkmark icon + badge "AKTIF"
- Warna berbeda untuk setiap preset

### 2. ✅ API Key Configuration
**Masalah**: Tidak ada info status SERPAPI key  
**Solusi**:
- Alert box status API key di tab Production
- Preview key: `abc123...xyz9`
- Warning alert jika belum dikonfigurasi
- Instruksi jelas untuk setup

### 3. ✅ Dashboard Information
**Masalah**: Dashboard kurang informatif  
**Solusi**:
- System Status Cards (API Key, ML Model)
- Configuration Overview Table
- Estimated API Calls per scan
- Scan Statistics (Total/Completed/Failed)
- Recent Scan History (10 terakhir)
- Link langsung ke config page

## 🎯 Cara Menggunakan

### Step 1: Migration Database

```bash
# Pastikan virtual environment aktif
cd C:\laragon\www\sistem-deteksi-domain\sistem_deteksi_malicious

# Run migration
python manage.py migrate

# Seharusnya akan membuat tabel SistemConfig
```

### Step 2: Akses Halaman Konfigurasi

```
1. Jalankan server: python manage.py runserver
2. Login sebagai admin
3. Buka: http://localhost:8000/config/
```

### Step 3: Konfigurasi Via UI

#### Opsi A: Load Quick Preset (Recommended)

1. Scroll ke bagian **Quick Presets**
2. Lihat preset aktif saat ini (badge hijau/biru/merah)
3. Pilih preset yang diinginkan:
   - **Hemat Maksimal** (~2-4 API calls) - Recommended untuk free tier
   - **Balanced** (~5-10 API calls) - Balanced performance
   - **Scan Lengkap** (~20-30 API calls) - Full features
4. Klik preset → Fields akan terisi otomatis
5. Scroll ke atas → Klik **"Simpan Semua Konfigurasi"**
6. Done! ✅

#### Opsi B: Manual Configuration

1. Klik tab sesuai kategori:
   - **Production Settings**: API cache, verification
   - **Optimization**: Search engines, subdomain, crawling
   - **Features**: Illegal detection, backlink
   - **Legacy**: Keywords, old mode
2. Edit pengaturan sesuai kebutuhan
3. Scroll ke bawah → Klik **"Simpan Semua Konfigurasi"**
4. Done! ✅

### Step 4: Cek Dashboard

```
Buka: http://localhost:8000/dashboard/
```

Lihat:
- ✅ Status API Key (Hijau/Merah)
- ✅ Model ML Status
- ✅ Konfigurasi aktif
- ✅ Estimated API calls per scan
- ✅ Statistik scan
- ✅ History terbaru

## 📊 Preset Configurations

### 🔋 Hemat Maksimal (Default - Recommended)

**Use Case**: Free tier SerpAPI (250/month), cost-efficient

**Settings**:
- ✅ API Cache: 14 hari
- ✅ Comprehensive Query: ON
- ✅ Max Results: 100
- ❌ Bing: OFF
- ✅ DuckDuckGo: ON
- ✅ DNS Lookup: ON
- ❌ Subdomain Search: OFF
- ❌ Content Scan: OFF
- ✅ Deep Crawling: ON
- ❌ Graph Analysis: OFF
- Max Crawl: 30 pages
- ❌ Unindexed Discovery: OFF
- ❌ Backlink: OFF

**Estimated**: ~2-4 API calls per scan  
**Savings**: 80-90% quota usage

### ⚖️ Balanced

**Use Case**: Standard production, balance speed vs accuracy

**Settings**:
- ✅ API Cache: 7 hari
- ✅ Comprehensive Query: ON
- ✅ Max Results: 100
- ✅ Deep Crawling: ON
- ✅ Graph Analysis: ON
- ✅ Unindexed Discovery: ON
- Max Crawl: 50 pages

**Estimated**: ~5-10 API calls per scan  
**Performance**: Optimal balance

### 🚀 Scan Lengkap

**Use Case**: Maximum accuracy, detailed analysis

**Settings**:
- ✅ All features enabled
- ✅ Bing: ON
- ✅ Subdomain Search: ON
- ✅ Content Scan: ON (20 subdomains)
- ✅ Graph Analysis: ON
- ✅ Unindexed Discovery: ON
- ✅ Backlink: ON
- Max Results: 200
- Max Crawl: 100 pages

**Estimated**: ~20-30 API calls per scan  
**Accuracy**: Maximum detection

## 🔍 Monitoring Usage

### Check API Usage
```
1. Login to SerpAPI dashboard
2. Check "API Usage" section
3. Monitor daily/monthly quota
4. Adjust config if needed
```

### Check Cache Hit Rate
```
1. Login as admin
2. Go to Dashboard
3. See "Configuration Overview"
4. Check "API Cache: Aktif/Non-Aktif"
```

### View Recent Scans
```
Dashboard → Recent Scan History
→ See last 10 scans
→ Check success/failure rate
```

## ⚠️ Troubleshooting

### Preset tidak aktif setelah save
**Penyebab**: Form tidak submit semua fields  
**Solusi**: Scroll ke bawah, pastikan klik "Simpan Semua Konfigurasi"

### Dashboard tidak menampilkan info
**Penyebab**: Belum ada scan history atau config  
**Solusi**: 
1. Run migration: `python manage.py migrate`
2. Create config: Akses `/config/`, klik save
3. Do a test scan

### API Key tidak terdeteksi
**Penyebab**: File .env tidak ada atau key salah  
**Solusi**:
1. Cek file `.env` di root project
2. Pastikan line: `SERPAPI_API_KEY=your_key_here`
3. Restart server

## 🎯 Best Practices

### Untuk Development
- Gunakan preset "Hemat Maksimal"
- Monitor cache hit rate
- Test di staging dulu
- Document changes in notes

### Untuk Production
- Start with "Hemat Maksimal"
- Monitor API usage daily
- Adjust based on quota
- Set cache TTL to 7-14 days
- Enable all detection features
- Use tiered verification

### Untuk Mobile App
- Use `/api/config/active/` endpoint
- Display config to users
- Adjust UI based on features
- Cache config locally
- Poll for updates

## 📚 Related Documentation

- **[KONFIGURASI_SISTEM.md](KONFIGURASI_SISTEM.md)** - Complete config guide
- **[README_API.md](README_API.md)** - API documentation
- **[DEPLOYMENT_PRODUCTION.md](DEPLOYMENT_PRODUCTION.md)** - Production setup
- **[SUMMARY_v2.md](SUMMARY_v2.md)** - Feature summary

## 🎉 Quick Comparison

### Before v2.0
```
Edit code → Change config → Test → Deploy → Restart server
⏱️ Time: ~15-30 minutes
❌ Risk: Code errors, downtime
```

### After v2.0
```
Open UI → Load preset → Save → Done
⏱️ Time: ~30 seconds
✅ Risk: Minimal, real-time effect
```

**Performance**: 30x faster! 🚀

---

**Questions?** Check documentation or contact admin.

