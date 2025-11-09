"""
Serializers untuk Django REST Framework.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from scanner.models import (
    ScanHistory, MaliciousKeyword, ActivityLog, DomainScanSummary, 
    SistemConfig, ApiKey, ProductionSettings
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer untuk User."""
    
    is_premium = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'organization_name', 'role', 'is_active', 'is_premium', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class MaliciousKeywordSerializer(serializers.ModelSerializer):
    """Serializer untuk MaliciousKeyword."""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = MaliciousKeyword
        fields = ['id', 'keyword', 'category', 'is_active', 'created_at', 
                 'updated_at', 'created_by', 'created_by_username']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScanHistorySerializer(serializers.ModelSerializer):
    """Serializer untuk ScanHistory."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ScanHistory
        fields = ['id', 'scan_id', 'user', 'user_username', 'domain', 'status', 
                 'status_display', 'scan_type', 'ran_with_verification', 
                 'showed_all_results', 'scan_date', 'start_time', 'end_time',
                 'error_message']
        read_only_fields = ['id', 'scan_id', 'scan_date', 'start_time', 'end_time']


class ScanResultSerializer(serializers.Serializer):
    """Serializer untuk hasil scan."""
    
    categories = serializers.DictField()
    domain_info = serializers.DictField()
    total_pages = serializers.IntegerField()
    verified_scan = serializers.BooleanField()
    final_conclusion = serializers.DictField()


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer untuk ActivityLog."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_username', 'timestamp', 'organization_name', 
                 'action', 'details']
        read_only_fields = ['id', 'timestamp']


class DomainScanSummarySerializer(serializers.ModelSerializer):
    """Serializer untuk DomainScanSummary."""
    
    class Meta:
        model = DomainScanSummary
        fields = ['id', 'domain', 'total_cases', 'hack_judol', 'pornografi', 
                 'hacked', 'last_scan', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_scan']


class ScanCreateSerializer(serializers.Serializer):
    """Serializer untuk membuat scan baru."""
    
    domain = serializers.CharField(max_length=255, required=True)
    scan_type = serializers.ChoiceField(
        choices=['Cepat (Google Only)', 'Komprehensif (Google + Crawling)'],
        required=True
    )
    enable_verification = serializers.BooleanField(default=True)
    show_all_results = serializers.BooleanField(default=False)
    
    def validate_domain(self, value):
        """Validasi domain."""
        from scanner.utils.validators import validate_domain
        if not validate_domain(value):
            raise serializers.ValidationError("Format domain tidak valid.")
        return value


class ProgressSerializer(serializers.Serializer):
    """Serializer untuk progress scan."""
    
    status = serializers.CharField()
    phase = serializers.CharField(required=False, allow_null=True)
    current = serializers.IntegerField(required=False, allow_null=True)
    total = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)


class SistemConfigSerializer(serializers.ModelSerializer):
    """Serializer untuk System Configuration."""
    
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = SistemConfig
        fields = [
            'id',
            # API & Cache
            'enable_api_cache', 'api_cache_ttl_days',
            # Search Engine
            'use_comprehensive_query', 'max_search_results', 
            'enable_bing_search', 'enable_duckduckgo_search',
            # Subdomain
            'enable_subdomain_dns_lookup', 'enable_subdomain_search',
            'enable_subdomain_content_scan', 'max_subdomains_to_scan',
            # Crawling
            'enable_deep_crawling', 'enable_sitemap_analysis',
            'enable_path_discovery', 'enable_graph_analysis', 'max_crawl_pages',
            # Verification
            'enable_realtime_verification', 'use_tiered_verification',
            # Illegal Content Detection
            'enable_illegal_content_detection', 'enable_hidden_content_detection',
            'enable_injection_detection', 'enable_unindexed_discovery',
            # Backlink
            'enable_backlink_analysis',
            # Metadata
            'updated_by', 'updated_by_username', 'updated_at', 'notes'
        ]
        read_only_fields = ['id', 'updated_at']
    
    def validate(self, data):
        """Validasi custom."""
        # Pastikan TTL cache masuk akal
        if 'api_cache_ttl_days' in data:
            if data['api_cache_ttl_days'] < 1 or data['api_cache_ttl_days'] > 90:
                raise serializers.ValidationError({
                    'api_cache_ttl_days': 'TTL harus antara 1-90 hari'
                })
        
        # Pastikan max results masuk akal
        if 'max_search_results' in data:
            if data['max_search_results'] < 10 or data['max_search_results'] > 200:
                raise serializers.ValidationError({
                    'max_search_results': 'Max results harus antara 10-200'
                })
        
        return data


class ApiKeySerializer(serializers.ModelSerializer):
    """Serializer untuk API Key Management."""
    
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
            'key_value': {'write_only': True}  # Hide key_value in responses
        }
    
    def validate_key_value(self, value):
        """Validate key value."""
        if not value or len(value) < 10:
            raise serializers.ValidationError('API key terlalu pendek atau kosong')
        return value
    
    def validate_key_name(self, value):
        """Validate key name."""
        if not value or not value.strip():
            raise serializers.ValidationError('Nama key tidak boleh kosong')
        return value.strip().upper()
    
    def create(self, validated_data):
        """Create new API key."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProductionSettingsSerializer(serializers.ModelSerializer):
    """Serializer untuk Production Settings."""
    
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = ProductionSettings
        fields = [
            'id',
            # Django Settings
            'debug_mode', 'allowed_hosts',
            # Security Settings
            'csrf_cookie_secure', 'session_cookie_secure', 'secure_ssl_redirect',
            # Email Settings
            'email_enabled', 'email_host', 'email_port', 'email_use_tls',
            # Mobile API Settings
            'mobile_api_enabled', 'mobile_api_rate_limit',
            # Backup Settings
            'auto_backup_enabled', 'backup_frequency_days',
            # Metadata
            'updated_by_username', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
    
    def validate_allowed_hosts(self, value):
        """Validate allowed hosts."""
        if not value or value.strip() == '':
            raise serializers.ValidationError('Allowed hosts tidak boleh kosong di production')
        # Validate format
        hosts = [h.strip() for h in value.split(',') if h.strip()]
        if not hosts:
            raise serializers.ValidationError('Allowed hosts harus berisi minimal 1 host')
        return value
    
    def validate_mobile_api_rate_limit(self, value):
        """Validate rate limit."""
        if value < 1 or value > 10000:
            raise serializers.ValidationError('Rate limit harus antara 1-10000 requests per jam')
        return value
    
    def validate_backup_frequency_days(self, value):
        """Validate backup frequency."""
        if value < 1 or value > 365:
            raise serializers.ValidationError('Backup frequency harus antara 1-365 hari')
        return value
    
    def validate_email_port(self, value):
        """Validate email port."""
        if value < 1 or value > 65535:
            raise serializers.ValidationError('Email port harus valid (1-65535)')
        return value


class QuotaStatusSerializer(serializers.Serializer):
    """Serializer untuk quota status user."""
    
    quota_limit = serializers.IntegerField()
    used_quota = serializers.IntegerField()
    remaining_quota = serializers.IntegerField()
    is_unlimited = serializers.BooleanField()
    can_scan = serializers.BooleanField()
    reset_period = serializers.CharField()
    next_reset = serializers.DateTimeField(allow_null=True)
    last_reset = serializers.DateTimeField()


class UserProfileSerializer(serializers.Serializer):
    """Serializer untuk user profile dengan quota dan premium status."""
    
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    organization_name = serializers.CharField(read_only=True, required=False)
    role = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)
    quota_status = QuotaStatusSerializer(read_only=True, allow_null=True)
    date_joined = serializers.DateTimeField(read_only=True)

