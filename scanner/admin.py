from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, ScanHistory, ActivityLog, MaliciousKeyword, 
    DomainScanSummary, SistemConfig, ApiKey, ProductionSettings,
    PermanentScanResult, UserScanQuota, Feedback, Partnership,
    ScanResultItem, ScanSubdomain
)

# Register your models here.
# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'organization_name', 'user_api_key', 'is_staff', 'is_active')
#     list_filter = ('is_staff', 'is_active', 'organization_name')
#     search_fields = ('username', 'email', 'organization_name')
#     ordering = ('username',)

# @admin.register(ActivityLog)
# class ActivityLogAdmin(admin.ModelAdmin):
#     list_display = ('timestamp', 'user', 'organization_name', 'action', 'details')
#     list_filter = ('action', 'timestamp', 'organization_name')
#     search_fields = ('user__username', 'organization_name', 'action', 'details')
#     ordering = ('-timestamp',)
#     readonly_fields = ('timestamp',)

# Kustomisasi tampilan CustomUser di admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Tambahkan field kustom ke tampilan list dan form
    list_display = ('username', 'email', 'organization_name', 'is_premium', 'is_staff', 'user_api_key')
    list_filter = ('is_premium', 'is_staff', 'is_active', 'organization_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('organization_name', 'user_api_key', 'role', 'is_premium')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('organization_name', 'user_api_key', 'role', 'is_premium')}),
    )

# Kustomisasi tampilan ScanHistory
class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('scan_id', 'user', 'domain', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'domain', 'user__organization_name') # Filter berdasarkan status, domain, instansi
    search_fields = ('scan_id', 'domain', 'user__username') # Tambah fitur search
    readonly_fields = ('start_time', 'end_time', 'scan_results_json', 'error_message') # Jangan biarkan hasil diedit manual

# Kustomisasi tampilan ActivityLog
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'organization_name', 'action')
    list_filter = ('action', 'organization_name', 'user__username')
    search_fields = ('username', 'details', 'action')
    readonly_fields = ('timestamp',)

# Kustomisasi tampilan MaliciousKeyword
class MaliciousKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'category', 'is_active', 'created_at', 'created_by')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('keyword', 'category')
    ordering = ('-created_at',)

# Kustomisasi tampilan DomainScanSummary
class DomainScanSummaryAdmin(admin.ModelAdmin):
    list_display = ('domain', 'total_cases', 'hack_judol', 'pornografi', 'hacked', 'last_scan')
    list_filter = ('last_scan',)
    search_fields = ('domain',)
    readonly_fields = ('last_scan', 'created_at', 'updated_at')

# Kustomisasi tampilan SistemConfig
class SistemConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('API & Cache Settings', {
            'fields': ('enable_api_cache', 'api_cache_ttl_days')
        }),
        ('Search Engine Settings', {
            'fields': ('use_comprehensive_query', 'max_search_results', 
                      'enable_bing_search', 'enable_duckduckgo_search')
        }),
        ('Subdomain Discovery', {
            'fields': ('enable_subdomain_dns_lookup', 'enable_subdomain_search',
                      'enable_subdomain_content_scan', 'max_subdomains_to_scan')
        }),
        ('Crawling Settings', {
            'fields': ('enable_deep_crawling', 'enable_sitemap_analysis',
                      'enable_path_discovery', 'enable_graph_analysis', 'max_crawl_pages')
        }),
        ('Verification Settings', {
            'fields': ('enable_realtime_verification', 'use_tiered_verification')
        }),
        ('Illegal Content Detection', {
            'fields': ('enable_illegal_content_detection', 'enable_hidden_content_detection',
                      'enable_injection_detection', 'enable_unindexed_discovery')
        }),
        ('Backlink Analysis', {
            'fields': ('enable_backlink_analysis',)
        }),
        ('Metadata', {
            'fields': ('updated_by', 'updated_at', 'notes')
        }),
    )
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Only allow one config record
        return not SistemConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ScanHistory, ScanHistoryAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(MaliciousKeyword, MaliciousKeywordAdmin)
admin.site.register(DomainScanSummary, DomainScanSummaryAdmin)
admin.site.register(SistemConfig, SistemConfigAdmin)


# Kustomisasi tampilan ApiKey
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('key_name', 'mask_key', 'is_active', 'created_at', 'last_used')
    list_filter = ('is_active', 'created_at')
    search_fields = ('key_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'last_used')
    fieldsets = (
        ('Key Information', {
            'fields': ('key_name', 'key_value', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )
    
    def mask_key(self, obj):
        """Display masked key in list."""
        return obj.mask_key()
    mask_key.short_description = 'Key (Masked)'


# Kustomisasi tampilan ProductionSettings
class ProductionSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Django Settings', {
            'fields': ('debug_mode', 'allowed_hosts')
        }),
        ('Security Settings', {
            'fields': ('csrf_cookie_secure', 'session_cookie_secure', 'secure_ssl_redirect')
        }),
        ('Email Settings', {
            'fields': ('email_enabled', 'email_host', 'email_port', 'email_use_tls')
        }),
        ('Mobile API Settings', {
            'fields': ('mobile_api_enabled', 'mobile_api_rate_limit')
        }),
        ('Backup Settings', {
            'fields': ('auto_backup_enabled', 'backup_frequency_days')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'updated_at')
        }),
    )
    readonly_fields = ('updated_at',)
    list_display = ('__str__', 'debug_mode', 'mobile_api_enabled', 'updated_at')
    
    def has_add_permission(self, request):
        """Hanya ada 1 record."""
        return not ProductionSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Jangan hapus."""
        return False

# Kustomisasi tampilan PermanentScanResult
class PermanentScanResultAdmin(admin.ModelAdmin):
    list_display = ('scan_history', 'total_items', 'total_subdomains', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('scan_history__domain', 'scan_history__scan_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Scan Information', {
            'fields': ('scan_history',)
        }),
        ('Results Summary', {
            'fields': ('total_items', 'total_subdomains', 'categories_detected')
        }),
        ('Full Results', {
            'fields': ('full_results_json',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Kustomisasi tampilan UserScanQuota
class UserScanQuotaAdmin(admin.ModelAdmin):
    list_display = ('user', 'quota_limit', 'used_quota', 'remaining_quota_display', 'reset_period', 'next_reset')
    list_filter = ('reset_period', 'quota_limit')
    search_fields = ('user__username', 'user__email', 'user__organization_name')
    readonly_fields = ('created_at', 'updated_at', 'last_reset')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Quota Settings', {
            'fields': ('quota_limit', 'used_quota', 'reset_period')
        }),
        ('Reset Information', {
            'fields': ('last_reset', 'next_reset')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def remaining_quota_display(self, obj):
        """Display remaining quota."""
        if obj.is_unlimited:
            return "Unlimited"
        remaining = obj.remaining_quota
        return f"{remaining} (of {obj.quota_limit})"
    remaining_quota_display.short_description = 'Remaining Quota'

# Kustomisasi tampilan Feedback
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'is_resolved', 'created_at', 'replied_by', 'replied_at')
    list_filter = ('is_resolved', 'created_at', 'replied_at')
    search_fields = ('user__username', 'message', 'reply')
    readonly_fields = ('created_at', 'replied_at')
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'message', 'created_at')
        }),
        ('Reply Information', {
            'fields': ('is_resolved', 'reply', 'replied_by', 'replied_at')
        }),
    )
    
    def message_preview(self, obj):
        """Display first 50 characters of message."""
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_preview.short_description = 'Message Preview'

# Kustomisasi tampilan Partnership
class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'partnership_type', 'is_active', 'display_order', 'website_url', 'created_at')
    list_filter = ('partnership_type', 'is_active', 'created_at')
    search_fields = ('name', 'website_url')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Partnership Information', {
            'fields': ('name', 'partnership_type', 'logo', 'website_url')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Kustomisasi tampilan ScanResultItem
class ScanResultItemAdmin(admin.ModelAdmin):
    list_display = ('url_preview', 'title_preview', 'label', 'verification_status', 'is_live', 'discovered_at')
    list_filter = ('label', 'verification_status', 'is_live', 'is_cache_only', 'scan_history__domain')
    search_fields = ('url', 'title', 'description', 'label', 'scan_history__domain')
    readonly_fields = ('discovered_at',)
    fieldsets = (
        ('Scan Information', {
            'fields': ('scan_history',)
        }),
        ('Item Information', {
            'fields': ('url', 'title', 'description')
        }),
        ('Label & Category', {
            'fields': ('label', 'category_code', 'category_name')
        }),
        ('Verification', {
            'fields': ('verification_status', 'is_live', 'is_cache_only')
        }),
        ('Analysis', {
            'fields': ('keywords_found', 'confidence_score', 'risk_score', 'js_analysis')
        }),
        ('Metadata', {
            'fields': ('source', 'discovered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def url_preview(self, obj):
        """Display first 50 characters of URL."""
        if len(obj.url) > 50:
            return obj.url[:50] + '...'
        return obj.url
    url_preview.short_description = 'URL'
    
    def title_preview(self, obj):
        """Display first 50 characters of title."""
        if obj.title and len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title or 'No Title'
    title_preview.short_description = 'Title'

# Kustomisasi tampilan ScanSubdomain
class ScanSubdomainAdmin(admin.ModelAdmin):
    list_display = ('subdomain', 'ip_address', 'status', 'discovery_method', 'scan_history', 'discovered_at')
    list_filter = ('status', 'discovery_method', 'scan_history__domain')
    search_fields = ('subdomain', 'ip_address', 'scan_history__domain')
    readonly_fields = ('discovered_at',)
    fieldsets = (
        ('Scan Information', {
            'fields': ('scan_history',)
        }),
        ('Subdomain Information', {
            'fields': ('subdomain', 'ip_address', 'status')
        }),
        ('Discovery', {
            'fields': ('discovery_method',)
        }),
        ('Metadata', {
            'fields': ('discovered_at',),
            'classes': ('collapse',)
        }),
    )

admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.register(ProductionSettings, ProductionSettingsAdmin)
admin.site.register(PermanentScanResult, PermanentScanResultAdmin)
admin.site.register(UserScanQuota, UserScanQuotaAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Partnership, PartnershipAdmin)
admin.site.register(ScanResultItem, ScanResultItemAdmin)
admin.site.register(ScanSubdomain, ScanSubdomainAdmin)