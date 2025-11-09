# 🎛️ Konfigurasi Sistem - Panduan Lengkap

## Overview

Semua konfigurasi sistem sekarang dapat diubah melalui **Web UI** atau **API REST**, tanpa perlu mengubah code! Sistem akan membaca konfigurasi dari database secara dinamis.

## 📍 Cara Akses

### 1. Web UI (Recommended)
```
Login sebagai Admin → Menu "Konfigurasi" → Edit pengaturan → Simpan
```

### 2. API REST
```bash
GET /api/config/active/          # Lihat konfigurasi saat ini
PATCH /api/config/1/              # Update konfigurasi
POST /api/config/reset_to_default/  # Reset ke default
```

## ⚙️ Daftar Konfigurasi

### 1. API & Cache Settings

#### `enable_api_cache` (Boolean)
- **Default**: `true`
- **Deskripsi**: Aktifkan caching hasil search API
- **Dampak**: Hemat **95% quota SerpAPI** dengan caching
- **Rekomendasi**: Selalu enable kecuali untuk testing

#### `api_cache_ttl_days` (Integer: 1-90)
- **Default**: `7`
- **Deskripsi**: Lama penyimpanan cache dalam hari
- **Dampak**: 
  - 7 hari = balance antara fresh data dan hemat quota
  - 1 hari = data lebih fresh, tapi lebih boros quota
  - 30+ hari = sangat hemat, tapi data mungkin stale

### 2. Search Engine Settings

#### `use_comprehensive_query` (Boolean)
- **Default**: `true`
- **Deskripsi**: Gunakan 1 query comprehensive vs 4 query terpisah
- **Dampak**: Hemat **75% API calls** (4→1 query)
- **Rekomendasi**: Selalu enable untuk efisiensi

#### `max_search_results` (Integer: 10-200)
- **Default**: `100`
- **Deskripsi**: Maksimal jumlah hasil per query
- **Dampak**: 
  - 100 = optimal (balance)
  - 50 = lebih hemat, hasil kurang lengkap
  - 200 = hasil lengkap, tapi quota lebih boros

#### `enable_bing_search` (Boolean)
- **Default**: `false`
- **Deskripsi**: Aktifkan Bing search via SerpAPI
- **Dampak**: +1 API call per scan
- **Rekomendasi**: Disable untuk hemat quota

#### `enable_duckduckgo_search` (Boolean)
- **Default**: `true`
- **Deskripsi**: Aktifkan DuckDuckGo search
- **Dampak**: **GRATIS** (no API key needed), +1 source results
- **Rekomendasi**: Selalu enable

### 3. Subdomain Discovery

#### `enable_subdomain_dns_lookup` (Boolean)
- **Default**: `true`
- **Deskripsi**: DNS lookup untuk menemukan subdomain
- **Dampak**: **GRATIS**, menemukan subdomain yang punya DNS record
- **Rekomendasi**: Selalu enable

#### `enable_subdomain_search` (Boolean)
- **Default**: `false`
- **Deskripsi**: Search subdomain via Google
- **Dampak**: +1-2 API calls per scan
- **Rekomendasi**: Disable kecuali sangat diperlukan

#### `enable_subdomain_content_scan` (Boolean)
- **Default**: `false`
- **Deskripsi**: Scan konten subdomain yang ditemukan
- **Dampak**: **10+ API calls** (1 per subdomain)
- **Rekomendasi**: Disable untuk hemat quota

#### `max_subdomains_to_scan` (Integer)
- **Default**: `10`
- **Deskripsi**: Maksimal subdomain yang di-scan kontennya
- **Dampak**: Limit biaya API subdomain scan
- **Rekomendasi**: 10 cukup untuk coverage

### 4. Crawling Settings

#### `enable_deep_crawling` (Boolean)
- **Default**: `true`
- **Deskripsi**: Deep crawling untuk halaman tersembunyi
- **Dampak**: Menemukan halaman yang tidak terindex Google
- **Rekomendasi**: Enable untuk scan komprehensif

#### `enable_sitemap_analysis` (Boolean)
- **Default**: `true`
- **Deskripsi**: Analisis sitemap.xml
- **Dampak**: **GRATIS**, menemukan semua URL dari sitemap
- **Rekomendasi**: Selalu enable

#### `enable_path_discovery` (Boolean)
- **Default**: `true`
- **Deskripsi**: Path brute force discovery
- **Dampak**: **GRATIS**, menemukan path tersembunyi (admin, login, dll)
- **Rekomendasi**: Enable untuk security scanning

#### `enable_graph_analysis` (Boolean)
- **Default**: `true`
- **Deskripsi**: Graph analysis untuk orphan pages
- **Dampak**: Menemukan halaman yang tidak terlink
- **Rekomendasi**: Enable untuk completeness

#### `max_crawl_pages` (Integer)
- **Default**: `50`
- **Deskripsi**: Maksimal halaman yang di-crawl
- **Dampak**:
  - 50 = balance antara completeness dan speed
  - 100 = lebih lengkap, tapi lebih lambat
  - 20 = lebih cepat, tapi coverage kurang

### 5. Verification Settings

#### `enable_realtime_verification` (Boolean)
- **Default**: `true`
- **Deskripsi**: Verifikasi real-time dengan Selenium
- **Dampak**: Akurasi tinggi, tapi lebih lambat
- **Rekomendasi**: Enable untuk production

#### `use_tiered_verification` (Boolean)
- **Default**: `true`
- **Deskripsi**: Requests first, lalu Selenium jika perlu
- **Dampak**: Lebih cepat, hemat resource Selenium
- **Rekomendasi**: Selalu enable

### 6. Illegal Content Detection

#### `enable_illegal_content_detection` (Boolean)
- **Default**: `true`
- **Deskripsi**: Deteksi konten ilegal komprehensif
- **Dampak**: Deteksi narkoba, penipuan, terorisme, dll
- **Rekomendasi**: Enable

#### `enable_hidden_content_detection` (Boolean)
- **Default**: `true`
- **Deskripsi**: Deteksi konten CSS hidden
- **Dampak**: Menemukan cloaking
- **Rekomendasi**: Enable

#### `enable_injection_detection` (Boolean)
- **Default**: `true`
- **Deskripsi**: Deteksi JavaScript/iframe injection
- **Dampak**: Menemukan content injection
- **Rekomendasi**: Enable

#### `enable_unindexed_discovery` (Boolean)
- **Default**: `true`
- **Deskripsi**: Discovery halaman tidak terindex Google
- **Dampak**: Menemukan konten ilegal tersembunyi
- **Rekomendasi**: Enable

### 7. Backlink Analysis

#### `enable_backlink_analysis` (Boolean)
- **Default**: `false`
- **Deskripsi**: Analisis backlink (menggunakan API)
- **Dampak**: +1 API call per scan
- **Rekomendasi**: Disable kecuali untuk research

## 📊 Preset Konfigurasi

### 🚀 Mode "Hemat Maksimal" (Recommended untuk Free Tier)

```json
{
  "enable_api_cache": true,
  "api_cache_ttl_days": 14,
  "use_comprehensive_query": true,
  "max_search_results": 100,
  "enable_bing_search": false,
  "enable_duckduckgo_search": true,
  "enable_subdomain_dns_lookup": true,
  "enable_subdomain_search": false,
  "enable_subdomain_content_scan": false,
  "max_subdomains_to_scan": 10,
  "enable_deep_crawling": true,
  "enable_sitemap_analysis": true,
  "enable_path_discovery": true,
  "enable_graph_analysis": false,
  "max_crawl_pages": 30,
  "enable_realtime_verification": true,
  "use_tiered_verification": true,
  "enable_illegal_content_detection": true,
  "enable_hidden_content_detection": true,
  "enable_injection_detection": true,
  "enable_unindexed_discovery": false,
  "enable_backlink_analysis": false
}
```

**Estimated Usage**: ~2-4 API calls per scan

### 🔍 Mode "Scan Lengkap"

```json
{
  "enable_api_cache": true,
  "api_cache_ttl_days": 7,
  "use_comprehensive_query": true,
  "max_search_results": 200,
  "enable_bing_search": true,
  "enable_duckduckgo_search": true,
  "enable_subdomain_dns_lookup": true,
  "enable_subdomain_search": true,
  "enable_subdomain_content_scan": true,
  "max_subdomains_to_scan": 20,
  "enable_deep_crawling": true,
  "enable_sitemap_analysis": true,
  "enable_path_discovery": true,
  "enable_graph_analysis": true,
  "max_crawl_pages": 100,
  "enable_realtime_verification": true,
  "use_tiered_verification": true,
  "enable_illegal_content_detection": true,
  "enable_hidden_content_detection": true,
  "enable_injection_detection": true,
  "enable_unindexed_discovery": true,
  "enable_backlink_analysis": true
}
```

**Estimated Usage**: ~20-30 API calls per scan

### ⚡ Mode "Scan Cepat"

```json
{
  "enable_api_cache": true,
  "api_cache_ttl_days": 3,
  "use_comprehensive_query": true,
  "max_search_results": 50,
  "enable_bing_search": false,
  "enable_duckduckgo_search": false,
  "enable_subdomain_dns_lookup": false,
  "enable_subdomain_search": false,
  "enable_subdomain_content_scan": false,
  "max_subdomains_to_scan": 5,
  "enable_deep_crawling": false,
  "enable_sitemap_analysis": false,
  "enable_path_discovery": false,
  "enable_graph_analysis": false,
  "max_crawl_pages": 10,
  "enable_realtime_verification": false,
  "use_tiered_verification": false,
  "enable_illegal_content_detection": true,
  "enable_hidden_content_detection": true,
  "enable_injection_detection": true,
  "enable_unindexed_discovery": false,
  "enable_backlink_analysis": false
}
```

**Estimated Usage**: ~1-2 API calls per scan

## 🎯 Quick Actions

### Reset ke Default
```bash
# Via API
POST /api/config/reset_to_default/

# Via Django Admin
# Login → Scanner → System Configurations → Select config → Delete
```

### Load Preset
```bash
# Via API
PATCH /api/config/1/
Body: {...preset config...}

# Via Web UI
# Copy preset JSON → Edit config → Paste → Save
```

## 📈 Monitoring Usage

### Check API Calls
1. Login ke SerpAPI dashboard
2. Lihat usage reports
3. Adjust configuration jika perlu

### Cache Hit Rate
- Check cache usage di Redis
- Cache miss = query baru ke API
- Cache hit = gratis!

## ⚠️ Important Notes

1. **Config adalah Singleton**: Hanya ada 1 config record
2. **Admin Only**: Hanya admin yang bisa edit config
3. **Audit Trail**: Semua perubahan di-log di activity logs
4. **Backward Compatible**: Default values akan digunakan jika config tidak ada
5. **Real-time Effect**: Perubahan langsung apply (no restart needed)

## 🔧 Troubleshooting

### Config tidak ter-apply
- Pastikan `SistemConfig.get_active_config()` dipanggil
- Check database punya 1 config record
- Check user punya permission admin

### Performance drop
- Disable features yang tidak perlu
- Kurangi `max_crawl_pages`
- Increase `api_cache_ttl_days`

### Quota habis cepat
- Enable `enable_api_cache`
- Disable `enable_subdomain_content_scan`
- Disable `enable_bing_search`
- Gunakan `use_comprehensive_query`

## 📚 Related Documentation

- [README.md](README.md) - Overview system
- [README_API.md](README_API.md) - API documentation
- [OPTIMISASI_QUOTA.md](OPTIMISASI_QUOTA.md) - Quota optimization guide

## 💡 Best Practices

1. **Start Conservative**: Gunakan preset "Hemat Maksimal" dulu
2. **Monitor Usage**: Check SerpAPI dashboard regularly
3. **Adjust as Needed**: Tweak setting berdasarkan kebutuhan
4. **Use Cache**: Selalu enable API cache
5. **Test Changes**: Test di staging sebelum production
6. **Document Changes**: Tambahkan notes saat update config
7. **Audit Regularly**: Review activity logs

---

**Dibuat**: 2024-01-15  
**Versi**: 2.0 - Dynamic Configuration System

