# 🔑 Saran API Key Management

## 📊 Analisis Sistem Saat Ini

### Priority System Saat Ini:
```
1. Database Key (ApiKey model, is_active=True) ← Prioritas Tertinggi
2. User Personal Key (user.user_api_key) ← Jika user punya
3. Admin .env Key (ADMIN_SERPAPI_KEY) ← Fallback
```

### Masalah:
- ❌ User key tidak pernah dipakai karena database key selalu diprioritaskan
- ❌ Tidak adil: user yang punya key sendiri tidak bisa pakai key mereka
- ❌ Tidak efisien: semua user pakai satu key, bisa habis quota
- ❌ Tidak ada isolasi: jika satu key habis, semua user terpengaruh

---

## 💡 Rekomendasi: User Key First

### Priority System Baru (Disarankan):
```
1. User Personal Key (user.user_api_key) ← Jika user punya
2. Database Key (ApiKey model, is_active=True) ← Shared key
3. Admin .env Key (ADMIN_SERPAPI_KEY) ← Fallback
```

### Keuntungan:
- ✅ **Adil**: User yang punya key pakai key sendiri
- ✅ **Efisien**: Load terdistribusi ke multiple keys
- ✅ **Isolasi**: Jika satu key habis, hanya user tertentu yang terpengaruh
- ✅ **Fleksibel**: Database key jadi fallback untuk user tanpa key

---

## 🎯 Skenario dengan User Key First

### Kondisi:
- Admin: `ADMIN_SERPAPI_KEY` di .env = "KEY_ADMIN"
- Admin: Database API Key (active) = "KEY_DB"
- Client1: `user_api_key` = "KEY_CLIENT1"
- Client2: `user_api_key` = "KEY_CLIENT2"

### Hasil:
- ✅ Client1 scan → pakai **KEY_CLIENT1** (user key sendiri)
- ✅ Client2 scan → pakai **KEY_CLIENT2** (user key sendiri)
- ✅ User tanpa key → pakai **KEY_DB** (database key)
- ✅ Jika database key habis → pakai **KEY_ADMIN** (env fallback)

---

## 🔧 Implementasi

### File: `scanner/services/scan_service.py`

**Ubah method `get_api_key_for_scan()`:**

```python
@staticmethod
def get_api_key_for_scan(user):
    """
    Get API key untuk scan dengan priority:
    1. User's personal key (user.user_api_key) ← BARU: Priority 1
    2. Active key dari database (ApiKey model)
    3. Admin key dari .env (settings.ADMIN_SERPAPI_KEY)
    """
    # Priority 1: User's personal key (BARU: dipindah ke priority 1)
    if user.user_api_key:
        logger.info(f"Using user's personal API key for {user.username}")
        return user.user_api_key, "user_personal"
    
    # Priority 2: Try get active API key from database
    primary_key = None
    key_source = None
    try:
        from scanner.models import ApiKey
        active_key = ApiKey.objects.filter(is_active=True).first()
        if active_key:
            primary_key = active_key.key_value
            key_source = "database"
            # Update last_used timestamp
            active_key.last_used = timezone.now()
            active_key.save(update_fields=['last_used'])
            logger.info(f"Using active API key from database: {active_key.key_name}")
    except Exception as e:
        logger.warning(f"Could not get API key from database: {e}")
    
    # Priority 3: Fallback to env key
    if not primary_key:
        admin_key = getattr(settings, 'ADMIN_SERPAPI_KEY', None)
        if admin_key:
            primary_key = admin_key
            key_source = "admin_env"
            logger.info("Using admin API key from .env")
    
    if not primary_key:
        raise ScanProcessingError(
            "No API key available. Please configure API key in database or .env file."
        )
    
    return primary_key, key_source
```

---

## 📈 Monitoring & Tracking

### Tambahkan Tracking di ScanHistory:
- Field `api_key_source` untuk tracking key mana yang dipakai
- Field `api_key_name` untuk identifikasi key
- Logging untuk monitoring usage per key

### Dashboard Monitoring:
- Usage per key (user key vs database key)
- Quota status per key
- Alert jika key mendekati limit

---

## 🎨 UI Enhancement

### Di Halaman Profile:
- Tampilkan status API key user
- Indikator apakah menggunakan key sendiri atau shared key
- Link untuk set/update user key

### Di Halaman Scan:
- Badge menunjukkan source key yang dipakai
- Info jika menggunakan shared key (database/env)

---

## ✅ Checklist Implementasi

- [ ] Ubah priority di `get_api_key_for_scan()`
- [ ] Test dengan user yang punya key
- [ ] Test dengan user tanpa key
- [ ] Test fallback ke database key
- [ ] Test fallback ke env key
- [ ] Update logging untuk tracking
- [ ] Update UI untuk menampilkan key source
- [ ] Dokumentasi perubahan

---

## 🔄 Migration Strategy

1. **Backup**: Backup current implementation
2. **Test**: Test di development environment
3. **Deploy**: Deploy ke production
4. **Monitor**: Monitor usage dan error
5. **Rollback**: Siapkan rollback plan jika ada masalah

---

## 📝 Catatan

- User key harus valid dan aktif
- Admin harus set database key untuk user tanpa key
- Env key tetap sebagai fallback terakhir
- Consider rate limiting per key
- Consider quota monitoring per key

