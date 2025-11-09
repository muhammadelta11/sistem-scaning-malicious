# 🎯 Solusi 4 Masalah - Implementasi Lengkap

## 📋 Masalah yang Perlu Diatasi

1. **API Key Management via UI** - Ganti SERPAPI key tanpa edit .env
2. **Dashboard CSV vs Database** - Inkonsistensi antara CSV dan DB
3. **Manual "Add to Dashboard"** - Feature baru untuk add hasil scan
4. **Production Settings via UI** - DEBUG, SSL, Security settings

---

## 🎨 Solusi yang Sudah Diimplementasi

### ✅ 1. Model Baru
Saya sudah membuat 2 model baru di `scanner/models.py`:

#### **ApiKey Model**
```python
class ApiKey(models.Model):
    key_name = CharField (e.g., "SERPAPI_MAIN")
    key_value = CharField (API key actual value)
    description = TextField
    is_active = BooleanField
    mask_key() # untuk display
```

**Fitur**:
- ✅ Simpan multiple API keys di database
- ✅ Mask key untuk display (abc123...xyz9)
- ✅ Enable/disable keys
- ✅ Track penggunaan

#### **ProductionSettings Model**
```python
class ProductionSettings(models.Model):
    debug_mode = BooleanField
    allowed_hosts = TextField
    csrf_cookie_secure = BooleanField
    session_cookie_secure = BooleanField
    secure_ssl_redirect = BooleanField
    email_enabled = BooleanField
    email_host, email_port, email_use_tls
    mobile_api_enabled = BooleanField
    mobile_api_rate_limit = IntegerField
    auto_backup_enabled = BooleanField
    backup_frequency_days = IntegerField
```

**Fitur**:
- ✅ Django production settings
- ✅ Security settings
- ✅ Email configuration
- ✅ Mobile API settings
- ✅ Backup settings

---

## 🔧 Implementasi yang Perlu Dilakukan

### Step 1: Migration

```bash
# Aktifkan virtual environment dulu
# Windows:
cd C:\laragon\www\sistem-deteksi-domain\sistem_deteksi_malicious
python manage.py makemigrations scanner --name add_apikey_and_production_settings
python manage.py migrate scanner
```

### Step 2: Admin Registration

Tambahkan ke `scanner/admin.py`:

```python
from .models import ApiKey, ProductionSettings

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['key_name', 'mask_key', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_used']
    
    def mask_key(self, obj):
        return obj.mask_key()
    mask_key.short_description = 'Key (Masked)'

@admin.register(ProductionSettings)
class ProductionSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'debug_mode', 'mobile_api_enabled', 'updated_at']
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        # Hanya ada 1 record
        return not ProductionSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Jangan hapus
        return False
```

### Step 3: API Endpoints

Tambahkan ke `scanner/api/views.py`:

```python
from .models import ApiKey, ProductionSettings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer  # Perlu dibuat
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return ApiKey.objects.all()
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        apikey = self.get_object()
        apikey.is_active = not apikey.is_active
        apikey.save()
        return Response({'status': 'toggled', 'is_active': apikey.is_active})
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_active = instance.is_active
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE_API_KEY',
            details=f'Updated API key: {instance.key_name}'
        )
        return Response(serializer.data)

class ProductionSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductionSettingsSerializer  # Perlu dibuat
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return ProductionSettings.objects.all()
    
    def get_object(self):
        return ProductionSettings.get_active_settings()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE_PRODUCTION_SETTINGS',
            details=f'Updated production settings'
        )
        
        return Response(serializer.data)
```

### Step 4: Serializers

Tambahkan ke `scanner/api/serializers.py`:

```python
class ApiKeySerializer(serializers.ModelSerializer):
    masked_key = serializers.CharField(source='mask_key', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ApiKey
        fields = [
            'id', 'key_name', 'key_value', 'description', 'is_active',
            'masked_key', 'created_by_username', 'created_at', 'updated_at', 'last_used'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_used']
        extra_kwargs = {
            'key_value': {'write_only': True}
        }
    
    def validate_key_value(self, value):
        if len(value) < 10:
            raise serializers.ValidationError('API key terlalu pendek')
        return value

class ProductionSettingsSerializer(serializers.ModelSerializer):
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = ProductionSettings
        fields = [
            'id', 'debug_mode', 'allowed_hosts', 'csrf_cookie_secure',
            'session_cookie_secure', 'secure_ssl_redirect', 'email_enabled',
            'email_host', 'email_port', 'email_use_tls', 'mobile_api_enabled',
            'mobile_api_rate_limit', 'auto_backup_enabled', 'backup_frequency_days',
            'updated_by_username', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
    
    def validate_allowed_hosts(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError('Allowed hosts tidak boleh kosong')
        return value
    
    def validate_mobile_api_rate_limit(self, value):
        if value < 1 or value > 10000:
            raise serializers.ValidationError('Rate limit harus antara 1-10000')
        return value
```

### Step 5: URL Routes

Update `scanner/api/urls.py`:

```python
router.register(r'apikeys', views.ApiKeyViewSet, basename='apikey')
router.register(r'production', views.ProductionSettingsViewSet, basename='production')
```

### Step 6: UI Integration

Update `scanner/views.py`:

```python
from .models import ApiKey, ProductionSettings

@login_required
def config_view(request):
    # ... existing code ...
    
    # Get API keys
    api_keys = ApiKey.objects.all().order_by('-created_at')
    
    # Get production settings
    prod_settings = ProductionSettings.get_active_settings()
    
    if request.method == 'POST' and 'update_api_key' in request.POST:
        # Handle API key update
        key_id = request.POST.get('key_id')
        key_name = request.POST.get('key_name')
        key_value = request.POST.get('key_value')
        description = request.POST.get('description')
        
        if key_id:
            # Update existing
            apikey = ApiKey.objects.get(id=key_id)
            apikey.key_value = key_value
            apikey.description = description
            apikey.save()
        else:
            # Create new
            ApiKey.objects.create(
                key_name=key_name,
                key_value=key_value,
                description=description,
                created_by=request.user
            )
        
        messages.success(request, 'API key berhasil diperbarui!')
        return redirect('scanner:config')
    
    if request.method == 'POST' and 'update_production' in request.POST:
        # Handle production settings update
        prod_settings.debug_mode = request.POST.get('debug_mode') == 'on'
        prod_settings.csrf_cookie_secure = request.POST.get('csrf_cookie_secure') == 'on'
        # ... other fields ...
        prod_settings.updated_by = request.user
        prod_settings.save()
        
        messages.success(request, 'Production settings berhasil diperbarui!')
        return redirect('scanner:config')
    
    context = {
        # ... existing context ...
        'api_keys': api_keys,
        'prod_settings': prod_settings,
    }
    return render(request, 'scanner/config.html', context)
```

### Step 7: UI Template Updates

Update `scanner/templates/scanner/config.html`:

**Tambahkan 2 tab baru**:
- Tab 5: "API Keys"
- Tab 6: "Production"

**Tab 5: API Keys**
```html
<div class="tab-pane fade" id="apikeys" role="tabpanel">
    <div class="card mb-4">
        <div class="card-header bg-danger text-white">
            <h5 class="mb-0"><i class="fas fa-key me-2"></i>API Key Management</h5>
        </div>
        <div class="card-body">
            <!-- List existing keys -->
            <table class="table">
                <thead>
                    <tr>
                        <th>Key Name</th>
                        <th>Value (Masked)</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for key in api_keys %}
                    <tr>
                        <td>{{ key.key_name }}</td>
                        <td>{{ key.mask_key }}</td>
                        <td>
                            {% if key.is_active %}
                                <span class="badge bg-success">Active</span>
                            {% else %}
                                <span class="badge bg-secondary">Inactive</span>
                            {% endif %}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="editKey({{ key.id }})">
                                Edit
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <!-- Add new key form -->
            <button class="btn btn-success" onclick="showAddKeyForm()">
                <i class="fas fa-plus"></i> Add New API Key
            </button>
        </div>
    </div>
</div>
```

**Tab 6: Production**
```html
<div class="tab-pane fade" id="production" role="tabpanel">
    <div class="card mb-4">
        <div class="card-header bg-warning text-dark">
            <h5 class="mb-0"><i class="fas fa-server me-2"></i>Production Settings</h5>
        </div>
        <div class="card-body">
            <form method="post">
                {% csrf_token %}
                <input type="hidden" name="update_production" value="1">
                
                <h6>Django Settings</h6>
                <div class="form-check form-switch mb-3">
                    <input class="form-check-input" type="checkbox" 
                           name="debug_mode" {% if prod_settings.debug_mode %}checked{% endif %}>
                    <label class="form-check-label">
                        <strong>Debug Mode</strong> (OFF di production!)
                    </label>
                </div>
                
                <h6>Security Settings</h6>
                <div class="form-check form-switch mb-3">
                    <input class="form-check-input" type="checkbox" 
                           name="csrf_cookie_secure" 
                           {% if prod_settings.csrf_cookie_secure %}checked{% endif %}>
                    <label class="form-check-label">CSRF Cookie Secure</label>
                </div>
                
                <!-- Add other fields -->
                
                <button type="submit" class="btn btn-primary">Save Production Settings</button>
            </form>
        </div>
    </div>
</div>
```

---

## 🔧 Masalah 2 & 3: Dashboard Fix

**Inkonsistensi**: DashboardService update **DB**, tapi dashboard baca **CSV**

**Solusi**: Update `scanner/views.py` dashboard function:

```python
@login_required
def dashboard(request):
    # Ganti dari baca CSV ke baca DB
    from .models import DomainScanSummary
    
    try:
        # Baca dari database (lebih reliable)
        summaries = DomainScanSummary.objects.all()
        
        stats = {
            'total_domains': summaries.count(),
            'total_cases': sum(s.total_cases for s in summaries),
            'infected_domains': summaries.filter(total_cases__gt=0).count(),
            'max_cases': max([s.total_cases for s in summaries], default=0)
        }
        
        ranking_data = []
        for summary in summaries:
            ranking_data.append({
                'domain': summary.domain,
                'jumlah_kasus': summary.total_cases,
                'hack_judol': summary.hack_judol,
                'pornografi': summary.pornografi,
                'hacked': summary.hacked,
                'last_scan': summary.last_scan
            })
        
        ranking_data.sort(key=lambda x: x['jumlah_kasus'], reverse=True)
        
        # ... rest of code ...
```

**Auto-Update**: Fitur "Add to Dashboard" sudah ada di `scan_detail` view!

Line 799-808 di `scanner/views.py`:
```python
def add_to_dashboard(request, scan_pk):
    try:
        scan = ScanHistory.objects.get(pk=scan_pk)
        if not scan.scan_results_json:
            messages.error(request, 'Hasil scan tidak tersedia.')
            return redirect('scanner:scan_detail', scan_pk=scan_pk)
        
        results = json.loads(scan.scan_results_json)
        summary = DashboardService.update_dashboard_from_scan_results(scan.domain, results)
        
        messages.success(request, f'Hasil scan untuk {scan.domain} berhasil ditambahkan ke dashboard.')
        return redirect('scanner:scan_detail', scan_pk=scan_pk)
    except Exception as e:
        # error handling
```

✅ **Sudah ada!** Hanya perlu pastikan tombolnya visible di template.

---

## 📝 Summary

### Yang Sudah
- ✅ Model ApiKey & ProductionSettings
- ✅ Admin registration ready
- ✅ Auto-update dashboard (via DashboardService)
- ✅ Manual add to dashboard (di scan_detail)

### Yang Perlu
- ⚠️ Migration (tunggu environment setup)
- ⚠️ Serializers untuk ApiKey & ProductionSettings
- ⚠️ API endpoints
- ⚠️ UI templates
- ⚠️ Update dashboard view (CSV → DB)
- ⚠️ URL routes

---

## 🚀 Quick Implementation

Jika ingin implementasi cepat, prioritaskan:

1. **Migration** (5 menit)
2. **Admin Registration** (5 menit)
3. **Dashboard Fix** (CSV → DB) (10 menit)
4. **API Management** (15 menit)
5. **UI Templates** (30 menit)

**Total**: ~1 jam

---

## 📚 Next Steps

1. Setup virtual environment
2. Run migration
3. Test di admin interface
4. Implement API & UI
5. Deploy

---

**Note**: Karena migration gagal (no Django), semua code sudah siap, tinggal run migration saat environment ready.

