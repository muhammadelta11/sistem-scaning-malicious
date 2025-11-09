# 🔑 API Key Integration - Penjelasan Lengkap

## ⚠️ SITUASI SAAT INI

**Yang Sudah**:
- ✅ Model `ApiKey` di database
- ✅ UI untuk manage API keys
- ✅ API endpoints untuk CRUD
- ✅ Admin interface

**Yang Belum**:
- ⚠️ Integrasi ke `core_scanner.py`
- ⚠️ Logic untuk pick key dari database

---

## 📊 FLOW SAAT INI

### Current Flow (Sejak Awal)
```
1. User request scan
   ↓
2. ScanService.create_scan() 
   ↓
3. Get API key dari:
   primary_key = user.user_api_key OR settings.ADMIN_SERPAPI_KEY
   ↓
4. Pass ke core_scanner.search_google()
   ↓
5. Use key untuk SerpAPI request
```

**Tidak ada integrasi ke model ApiKey database!**

---

## 🎯 YANG PERLU DILAKUKAN

### Integrasikan ApiKey Model ke Core Scanner

**Location**: `scanner/services/scan_service.py` line 54

**Current Code**:
```python
primary_key = user.user_api_key or settings.ADMIN_SERPAPI_KEY
fallback_key = settings.ADMIN_SERPAPI_KEY
```

**Needs To Become**:
```python
# Try get active API key from database first
primary_key = None
try:
    from .models import ApiKey
    active_key = ApiKey.objects.filter(is_active=True).first()
    if active_key:
        primary_key = active_key.key_value
        # Update last_used timestamp
        active_key.last_used = timezone.now()
        active_key.save(update_fields=['last_used'])
except:
    pass

# Fallback to user key or env
if not primary_key:
    primary_key = user.user_api_key or settings.ADMIN_SERPAPI_KEY

fallback_key = settings.ADMIN_SERPAPI_KEY
```

---

## 🔄 PRIORITAS API KEY

### Urutan Priority (Dari yang Diinginkan)

**Option 1: Database First** ⭐ (Recommended)
```
1. Active API key dari database (ApiKey model)
2. User's personal API key (user.user_api_key)
3. Admin key dari .env (settings.ADMIN_SERPAPI_KEY)
```

**Option 2: User First** (Current behavior with DB)
```
1. User's personal API key (user.user_api_key)
2. Active API key dari database (ApiKey model)
3. Admin key dari .env (settings.ADMIN_SERPAPI_KEY)
```

**Option 3: .env Always Wins** (Current behavior)
```
1. User's personal API key (user.user_api_key)
2. Admin key dari .env (settings.ADMIN_SERPAPI_KEY)
3. Never use database keys
```

---

## 💡 JAWABAN PERTANYAAN ANDA

### "Yang dipake yang di .env atau yang di konfigurasi UI?"

**Saat Ini**: ✅ **.env (.ADMIN_SERPAPI_KEY)**  
**Ke Depan**: ⭐ **Yang di konfigurasi UI (Database)**

**Penjelasan**:
- `.env` → Untuk backward compatibility & fallback
- `UI/Database` → Untuk flexibility & multiple keys
- Keduanya bisa digunakan bersamaan (priority)

---

## 🔧 IMPLEMENTASI INTEGRASI

### Step 1: Update ScanService
**File**: `scanner/services/scan_service.py`

```python
# Add import
from .models import ApiKey

# Update get API keys logic
@staticmethod
def get_api_key_for_scan(user):
    """
    Get API key untuk scan dengan priority:
    1. Active key dari database
    2. User's personal key
    3. Admin key dari .env
    """
    # Try database first
    try:
        active_key = ApiKey.objects.filter(is_active=True).first()
        if active_key:
            # Update last_used
            ApiKey.objects.filter(id=active_key.id).update(
                last_used=timezone.now()
            )
            return active_key.key_value, active_key.key_name
    except Exception as e:
        logger.warning(f"Could not get API key from DB: {e}")
    
    # Fallback to user key
    if user.user_api_key:
        return user.user_api_key, "user_personal"
    
    # Fallback to env
    admin_key = getattr(settings, 'ADMIN_SERPAPI_KEY', None)
    if admin_key:
        return admin_key, "admin_env"
    
    raise ScanProcessingError("No API key available")

# In create_scan():
primary_key, key_source = ScanService.get_api_key_for_scan(user)
```

### Step 2: Update Scan History
Track which key was used.

```python
scan_obj = ScanHistory.objects.create(
    # ... other fields ...
    api_key_source=key_source  # "database", "user_personal", "admin_env"
)
```

---

## 🎨 UI SHOW WHICH KEY IS USED

### In Dashboard
```html
<div class="alert alert-info">
    <i class="fas fa-key"></i>
    <strong>API Key Status:</strong>
    {% if last_key_used == 'database' %}
        ✅ Using database key ({{ key_name }})
    {% elif last_key_used == 'user_personal' %}
        ℹ️ Using your personal key
    {% else %}
        ⚠️ Using admin key from .env
    {% endif %}
</div>
```

---

## ✅ KONFIGURASI YANG DIINGINKAN

### For Maximum Flexibility
**Best Practice**:
```
1. Setup multiple API keys di database
2. Set 1 key sebagai active
3. Rotate keys kapan saja dari UI
4. .env sebagai emergency fallback
```

### Benefits
- ✅ No server restart needed
- ✅ Easy key rotation
- ✅ Multiple keys support
- ✅ Usage tracking
- ✅ Centralized management

---

## 🚀 QUICK IMPLEMENTATION

Ingin saya implementasikan sekarang?

**Akan update**:
1. `scanner/services/scan_service.py` - Add get_api_key_for_scan()
2. `scanner/models.py` - Add api_key_source field (optional)
3. Dashboard - Display key status

**Benefits**:
- ✅ Priority system clear
- ✅ Backward compatible
- ✅ UI-manageable keys
- ✅ Automatic fallback

---

## 📝 SUMMARY

**Current**: .env only  
**After Integration**: Database → User → .env (priority)

**UI Config**: Manage multiple keys  
**.env**: Emergency fallback

**Semua akan work together!** ✅

---

**Mau saya implementasikan integrasinya sekarang?** 🚀

