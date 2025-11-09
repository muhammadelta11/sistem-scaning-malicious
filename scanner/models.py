# scanner/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings # <-- Import settings

# Model CustomUser dengan role fleksibel
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
        ('superuser', 'Superuser'),
    ]

    organization_name = models.CharField(max_length=100, blank=True, null=True)
    user_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="SerpApi key milik user/instansi (jika ada)")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='Role pengguna untuk kontrol akses'
    )
    is_premium = models.BooleanField(
        default=False,
        help_text='Apakah user memiliki akses premium (permanent storage)'
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role in ['admin', 'superuser'] or self.is_superuser

    @property
    def is_moderator(self):
        return self.role in ['moderator', 'admin', 'superuser'] or self.is_staff or self.is_superuser

# --- Perubahan di Model ActivityLog ---
class ActivityLog(models.Model):
    # GANTI 'CustomUser' DENGAN 'settings.AUTH_USER_MODEL'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # <-- GANTI DI SINI
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    organization_name = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {user_str} - {self.action}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Activity Logs" # Ubah nama jika perlu

# Model untuk MaliciousKeyword
class MaliciousKeyword(models.Model):
    CATEGORY_CHOICES = [
        ('judi', 'Judi Online'),
        ('pornografi', 'Pornografi'),
        ('hacking', 'Hacking/Malware'),
        ('phishing', 'Phishing'),
        ('narkoba', 'Narkoba/Obat Terlarang'),
        ('penipuan', 'Penipuan/Scam'),
        ('terorisme', 'Terorisme'),
        ('pemalsuan', 'Pemalsuan'),
        ('perdagangan_manusia', 'Perdagangan Manusia'),
        ('konten_kekerasan', 'Konten Kekerasan'),
        ('prostitusi', 'Prostitusi'),
        ('perjudian_ilegal', 'Perjudian Ilegal'),
        ('pornografi_anak', 'Pornografi Anak'),
        ('other', 'Lainnya'),
    ]

    keyword = models.CharField(
        max_length=100,
        unique=True,
        help_text='Kata kunci untuk deteksi malicious content'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text='Kategori keyword'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Apakah keyword aktif digunakan'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_keywords',
        help_text='User yang membuat keyword'
    )

    def __str__(self):
        return f"{self.keyword} ({self.get_category_display()})"

    class Meta:
        verbose_name = 'Malicious Keyword'
        verbose_name_plural = 'Malicious Keywords'
        ordering = ['-created_at']

# Model untuk menyimpan riwayat scan
class ScanHistory(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    scan_id = models.CharField(max_length=100, unique=True, help_text='Unique scan identifier')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scan_histories'
    )
    domain = models.CharField(max_length=255, help_text='Target domain yang di-scan')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    scan_type = models.CharField(
        max_length=50,
        default='Cepat (Google Only)',
        help_text='Tipe scan yang dilakukan (Cepat/Komprehensif)'
    )
    ran_with_verification = models.BooleanField(
        default=True,
        help_text='Apakah scan dijalankan dengan verifikasi real-time'
    )
    showed_all_results = models.BooleanField(
        default=False,
        help_text='Apakah scan menampilkan semua hasil terindikasi (tanpa filter verifikasi)'
    )
    # --- BATAS PENAMBAHAN ---
    scan_date = models.DateTimeField(auto_now_add=True, help_text='Tanggal scan dilakukan')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    scan_results_json = models.TextField(null=True, blank=True, help_text='Hasil scan dalam format JSON')
    error_message = models.TextField(null=True, blank=True, help_text='Pesan error jika scan gagal')

    def __str__(self):
        return f"Scan {self.scan_id} - {self.domain} ({self.status})"

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Scan History'
        verbose_name_plural = 'Scan Histories'

# Model untuk menyimpan summary hasil scan per domain untuk dashboard
class DomainScanSummary(models.Model):
    domain = models.CharField(max_length=255, unique=True, help_text='Domain yang di-scan')
    total_cases = models.IntegerField(default=0, help_text='Total kasus malicious ditemukan')
    hack_judol = models.IntegerField(default=0, help_text='Jumlah kasus hack/judol')
    pornografi = models.IntegerField(default=0, help_text='Jumlah kasus pornografi')
    hacked = models.IntegerField(default=0, help_text='Jumlah kasus hacked/defaced')
    last_scan = models.DateTimeField(auto_now=True, help_text='Waktu scan terakhir')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.domain} - {self.total_cases} cases"

    class Meta:
        ordering = ['-last_scan']
        verbose_name = 'Domain Scan Summary'
        verbose_name_plural = 'Domain Scan Summaries'


# Model untuk konfigurasi sistem yang dapat diubah dari UI
class SistemConfig(models.Model):
    """
    Model untuk menyimpan semua konfigurasi sistem yang dapat diubah dari UI.
    Hanya admin yang dapat mengubah konfigurasi.
    """
    
    # Konfigurasi Optimisasi Quota SerpAPI
    enable_api_cache = models.BooleanField(
        default=True,
        help_text='Aktifkan caching hasil search (hemat 95% quota API)'
    )
    api_cache_ttl_days = models.IntegerField(
        default=7,
        help_text='Lama penyimpanan cache dalam hari (default: 7 hari)'
    )
    
    # Konfigurasi Search Engine
    use_comprehensive_query = models.BooleanField(
        default=True,
        help_text='Gunakan query comprehensive (1 query vs 4 queries)'
    )
    max_search_results = models.IntegerField(
        default=100,
        help_text='Maksimal jumlah hasil search per query (default: 100)'
    )
    enable_bing_search = models.BooleanField(
        default=False,
        help_text='Aktifkan Bing search (menggunakan API key)'
    )
    enable_duckduckgo_search = models.BooleanField(
        default=True,
        help_text='Aktifkan DuckDuckGo search (GRATIS, no API key)'
    )
    
    # Konfigurasi Subdomain Discovery
    enable_subdomain_dns_lookup = models.BooleanField(
        default=True,
        help_text='Aktifkan DNS lookup untuk subdomain (GRATIS)'
    )
    enable_subdomain_search = models.BooleanField(
        default=False,
        help_text='Aktifkan search subdomain via Google (menggunakan API)'
    )
    enable_subdomain_content_scan = models.BooleanField(
        default=False,
        help_text='Aktifkan scan konten subdomain (10+ API calls jika enable)'
    )
    max_subdomains_to_scan = models.IntegerField(
        default=10,
        help_text='Maksimal subdomain yang di-scan (default: 10)'
    )
    
    # Konfigurasi Crawling
    enable_deep_crawling = models.BooleanField(
        default=True,
        help_text='Aktifkan deep crawling untuk menemukan halaman tersembunyi'
    )
    enable_sitemap_analysis = models.BooleanField(
        default=True,
        help_text='Aktifkan analisis sitemap.xml (GRATIS)'
    )
    enable_path_discovery = models.BooleanField(
        default=True,
        help_text='Aktifkan path brute force discovery (GRATIS)'
    )
    enable_graph_analysis = models.BooleanField(
        default=True,
        help_text='Aktifkan graph analysis untuk orphan pages'
    )
    max_crawl_pages = models.IntegerField(
        default=50,
        help_text='Maksimal halaman yang di-crawl (default: 50)'
    )
    
    # Konfigurasi Verifikasi
    enable_realtime_verification = models.BooleanField(
        default=True,
        help_text='Aktifkan verifikasi real-time dengan Selenium'
    )
    use_tiered_verification = models.BooleanField(
        default=True,
        help_text='Gunakan tiered verification (requests first, then Selenium)'
    )
    
    # Konfigurasi Deteksi Konten Ilegal
    enable_illegal_content_detection = models.BooleanField(
        default=True,
        help_text='Aktifkan deteksi konten ilegal komprehensif'
    )
    enable_hidden_content_detection = models.BooleanField(
        default=True,
        help_text='Aktifkan deteksi konten tersembunyi (CSS hidden, dll)'
    )
    enable_injection_detection = models.BooleanField(
        default=True,
        help_text='Aktifkan deteksi injeksi konten (JavaScript, iframe)'
    )
    enable_unindexed_discovery = models.BooleanField(
        default=True,
        help_text='Aktifkan discovery halaman tidak terindex Google'
    )
    
    # Konfigurasi Backlink Analysis
    enable_backlink_analysis = models.BooleanField(
        default=False,
        help_text='Aktifkan analisis backlink (menggunakan API)'
    )
    
    # Metadata
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_configs',
        help_text='User terakhir yang mengupdate konfigurasi'
    )
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Catatan admin tentang konfigurasi'
    )
    
    def __str__(self):
        return f"System Configuration (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')})"
    
    class Meta:
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
        
    @classmethod
    def get_active_config(cls):
        """
        Mendapatkan konfigurasi aktif. Hanya ada satu record.
        """
        config = cls.objects.first()
        if not config:
            # Create default config jika belum ada
            config = cls.objects.create()
        return config
    
    def save(self, *args, **kwargs):
        # Pastikan hanya ada satu record konfigurasi
        if self.pk is None:
            # Check if config already exists
            existing = SistemConfig.objects.first()
            if existing:
                self.pk = existing.pk
        super().save(*args, **kwargs)


# Model untuk menyimpan API Keys (untuk UI management)
class ApiKey(models.Model):
    """
    Model untuk menyimpan API keys yang dapat diubah dari UI.
    """
    key_name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nama key (e.g., SERPAPI_MAIN, SERPAPI_FALLBACK)'
    )
    key_value = models.CharField(
        max_length=500,
        help_text='Nilai API key (akan di-encrypt di production)'
    )
    description = models.TextField(
        blank=True,
        help_text='Deskripsi penggunaan key ini'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Apakah key ini aktif digunakan'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_api_keys'
    )
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.key_name} ({'Active' if self.is_active else 'Inactive'})"
    
    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        
    def mask_key(self):
        """Return masked key for display."""
        if not self.key_value or len(self.key_value) < 10:
            return "***"
        return f"{self.key_value[:6]}...{self.key_value[-4:]}"


# Model untuk Production Settings
class ProductionSettings(models.Model):
    """
    Model untuk settings khusus production (DEBUG, SSL, Security, dll).
    """
    # Django Settings
    debug_mode = models.BooleanField(
        default=False,
        help_text='Debug mode (OFF di production!)'
    )
    allowed_hosts = models.TextField(
        default='localhost,127.0.0.1',
        help_text='Comma-separated list of allowed hosts'
    )
    
    # Security Settings
    csrf_cookie_secure = models.BooleanField(
        default=True,
        help_text='CSRF cookie secure flag'
    )
    session_cookie_secure = models.BooleanField(
        default=True,
        help_text='Session cookie secure flag'
    )
    secure_ssl_redirect = models.BooleanField(
        default=True,
        help_text='Force HTTPS redirect'
    )
    
    # Email Settings (untuk notifications)
    email_enabled = models.BooleanField(
        default=False,
        help_text='Enable email notifications'
    )
    email_host = models.CharField(
        max_length=255,
        blank=True,
        help_text='SMTP server'
    )
    email_port = models.IntegerField(
        default=587,
        help_text='SMTP port'
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text='Use TLS for email'
    )
    
    # Mobile API Settings
    mobile_api_enabled = models.BooleanField(
        default=True,
        help_text='Enable mobile API access'
    )
    mobile_api_rate_limit = models.IntegerField(
        default=100,
        help_text='API requests per hour per user'
    )
    
    # Backup Settings
    auto_backup_enabled = models.BooleanField(
        default=True,
        help_text='Enable automatic backups'
    )
    backup_frequency_days = models.IntegerField(
        default=1,
        help_text='How often to backup (in days)'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_production_settings'
    )
    
    def __str__(self):
        return f"Production Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')})"
    
    class Meta:
        verbose_name = 'Production Settings'
        verbose_name_plural = 'Production Settings'
        
    @classmethod
    def get_active_settings(cls):
        """Get active production settings (singleton)."""
        settings_obj = cls.objects.first()
        if not settings_obj:
            settings_obj = cls.objects.create()
        return settings_obj
    
    def save(self, *args, **kwargs):
        # Ensure only one record
        if self.pk is None:
            existing = ProductionSettings.objects.first()
            if existing:
                self.pk = existing.pk
        super().save(*args, **kwargs)


# Model untuk menyimpan hasil scan permanen (Premium Feature)
class PermanentScanResult(models.Model):
    """
    Menyimpan hasil scan secara permanen untuk user premium.
    Memungkinkan user untuk meninjau kembali URL/link yang pernah ditemukan.
    """
    scan_history = models.OneToOneField(
        ScanHistory,
        on_delete=models.CASCADE,
        related_name='permanent_result',
        help_text='Scan history yang terkait'
    )
    
    # Simpan full results sebagai JSON
    full_results_json = models.JSONField(
        help_text='Hasil scan lengkap dalam format JSON'
    )
    
    # Metadata
    total_items = models.IntegerField(default=0, help_text='Total item yang ditemukan')
    total_subdomains = models.IntegerField(default=0, help_text='Total subdomain yang ditemukan')
    categories_detected = models.JSONField(default=dict, help_text='Kategori yang terdeteksi')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Permanent Result: {self.scan_history.domain} ({self.scan_history.scan_id})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Permanent Scan Result'
        verbose_name_plural = 'Permanent Scan Results'


# Model untuk menyimpan setiap item hasil scan secara terstruktur
class ScanResultItem(models.Model):
    """
    Menyimpan setiap URL, title, description, label yang ditemukan dalam scan.
    Memungkinkan query dan filtering yang lebih mudah daripada hanya menyimpan JSON.
    """
    VERIFICATION_STATUS_CHOICES = [
        ('LIVE', 'Live Malicious'),
        ('CACHE_ONLY', 'Cache Only'),
        ('VERIFIED_SAFE', 'Verified Safe'),
        ('UNVERIFIED', 'Unverified'),
        ('ERROR', 'Error'),
    ]
    
    scan_history = models.ForeignKey(
        ScanHistory,
        on_delete=models.CASCADE,
        related_name='result_items',
        help_text='Scan history yang terkait'
    )
    
    # Data utama
    url = models.URLField(max_length=2048, help_text='URL yang ditemukan')
    title = models.TextField(blank=True, null=True, help_text='Title dari halaman')
    description = models.TextField(blank=True, null=True, help_text='Description/snippet dari halaman')
    
    # Label dan kategori
    label = models.CharField(max_length=100, help_text='Label yang terdeteksi (hack judol, pornografi, dll)')
    category_code = models.CharField(max_length=10, blank=True, null=True, help_text='Kode kategori (0=aman, 1=hack judol, 2=pornografi, 3=hacked)')
    category_name = models.CharField(max_length=100, blank=True, null=True, help_text='Nama kategori')
    
    # Verifikasi
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='UNVERIFIED',
        help_text='Status verifikasi halaman'
    )
    is_live = models.BooleanField(default=False, help_text='Apakah halaman masih live/aktif')
    is_cache_only = models.BooleanField(default=False, help_text='Apakah hanya ditemukan di cache')
    
    # Keywords yang ditemukan
    keywords_found = models.JSONField(
        default=list,
        blank=True,
        help_text='List keywords yang ditemukan di halaman'
    )
    
    # Analisis tambahan
    confidence_score = models.FloatField(null=True, blank=True, help_text='Confidence score dari model')
    risk_score = models.IntegerField(null=True, blank=True, help_text='Risk score (0-100)')
    
    # Metadata
    source = models.CharField(max_length=100, blank=True, null=True, help_text='Sumber data (Google, Bing, dll)')
    discovered_at = models.DateTimeField(auto_now_add=True, help_text='Waktu item ditemukan')
    
    # Analisis JavaScript (opsional)
    js_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text='Hasil analisis JavaScript jika tersedia'
    )
    
    class Meta:
        ordering = ['-discovered_at', '-risk_score']
        verbose_name = 'Scan Result Item'
        verbose_name_plural = 'Scan Result Items'
        indexes = [
            models.Index(fields=['scan_history', 'label']),
            models.Index(fields=['scan_history', 'verification_status']),
            models.Index(fields=['url']),
            models.Index(fields=['is_live', 'label']),
        ]
    
    def __str__(self):
        return f"{self.url[:50]}... - {self.label} ({self.verification_status})"


# Model untuk menyimpan setiap subdomain yang ditemukan
class ScanSubdomain(models.Model):
    """
    Menyimpan setiap subdomain yang ditemukan dalam scan.
    Memungkinkan query dan tracking yang lebih mudah.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Aktif'),
        ('INACTIVE', 'Tidak Aktif'),
        ('UNKNOWN', 'Tidak Diketahui'),
    ]
    
    scan_history = models.ForeignKey(
        ScanHistory,
        on_delete=models.CASCADE,
        related_name='subdomains',
        help_text='Scan history yang terkait'
    )
    
    # Data subdomain
    subdomain = models.CharField(max_length=255, help_text='Nama subdomain (contoh: www.example.com)')
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text='IP address subdomain')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UNKNOWN',
        help_text='Status subdomain'
    )
    
    # Teknik discovery
    discovery_method = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Teknik yang digunakan untuk menemukan subdomain (dns_lookup, web_search, certificate_transparency)'
    )
    
    # Metadata
    discovered_at = models.DateTimeField(auto_now_add=True, help_text='Waktu subdomain ditemukan')
    
    class Meta:
        ordering = ['subdomain']
        verbose_name = 'Scan Subdomain'
        verbose_name_plural = 'Scan Subdomains'
        unique_together = ['scan_history', 'subdomain']  # Satu subdomain per scan
        indexes = [
            models.Index(fields=['scan_history', 'status']),
            models.Index(fields=['subdomain']),
        ]
    
    def __str__(self):
        return f"{self.subdomain} - {self.status} ({self.scan_history.domain})"


# Model untuk mengelola kuota scan per user
class UserScanQuota(models.Model):
    """
    Mengelola kuota scan untuk setiap user/client.
    Admin dapat mengatur berapa kali setiap user dapat melakukan scan.
    """
    RESET_PERIOD_CHOICES = [
        ('daily', 'Harian'),
        ('weekly', 'Mingguan'),
        ('monthly', 'Bulanan'),
        ('yearly', 'Tahunan'),
        ('never', 'Tidak pernah reset'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scan_quota',
        help_text='User yang memiliki kuota ini'
    )
    
    # Kuota settings
    quota_limit = models.IntegerField(
        default=10,
        help_text='Total kuota scan yang tersedia (0 = unlimited)'
    )
    used_quota = models.IntegerField(
        default=0,
        help_text='Kuota yang sudah digunakan'
    )
    
    # Reset settings
    reset_period = models.CharField(
        max_length=20,
        choices=RESET_PERIOD_CHOICES,
        default='monthly',
        help_text='Periode reset kuota'
    )
    last_reset = models.DateTimeField(
        auto_now_add=True,
        help_text='Waktu reset terakhir'
    )
    next_reset = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Waktu reset berikutnya'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.quota_limit == 0:
            return f"{self.user.username}: Unlimited"
        remaining = self.quota_limit - self.used_quota
        return f"{self.user.username}: {self.used_quota}/{self.quota_limit} (Sisa: {remaining})"
    
    @property
    def remaining_quota(self):
        """Hitung sisa kuota."""
        if self.quota_limit == 0:
            return -1  # Unlimited
        return max(0, self.quota_limit - self.used_quota)
    
    @property
    def is_unlimited(self):
        """Cek apakah kuota unlimited."""
        return self.quota_limit == 0
    
    @property
    def is_exceeded(self):
        """Cek apakah kuota sudah habis."""
        if self.is_unlimited:
            return False
        return self.used_quota >= self.quota_limit
    
    def can_scan(self):
        """Cek apakah user masih bisa melakukan scan."""
        # Check if quota needs reset
        self._check_and_reset()
        return not self.is_exceeded
    
    def use_quota(self, count=1):
        """Gunakan kuota scan."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.is_unlimited:
            # Refresh from DB to ensure we have latest value
            old_used = self.used_quota
            self.refresh_from_db(fields=['used_quota'])
            logger.info(f"Using quota: User {self.user.username}, Before: {old_used}/{self.quota_limit}, Refreshed: {self.used_quota}/{self.quota_limit}")
            self.used_quota += count
            self.save(update_fields=['used_quota', 'updated_at'])
            logger.info(f"Quota updated: User {self.user.username}, After save: {self.used_quota}/{self.quota_limit}")
        else:
            logger.info(f"Skipping quota usage for {self.user.username} (unlimited quota)")
    
    def _calculate_next_reset(self):
        """Hitung waktu reset berikutnya."""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.reset_period == 'daily':
            self.next_reset = timezone.now() + timedelta(days=1)
        elif self.reset_period == 'weekly':
            self.next_reset = timezone.now() + timedelta(weeks=1)
        elif self.reset_period == 'monthly':
            self.next_reset = timezone.now() + timedelta(days=30)
        elif self.reset_period == 'yearly':
            self.next_reset = timezone.now() + timedelta(days=365)
        else:
            self.next_reset = None
    
    def _check_and_reset(self):
        """Cek dan reset kuota jika perlu."""
        from django.utils import timezone
        
        if self.next_reset and timezone.now() >= self.next_reset:
            # Reset quota
            self.used_quota = 0
            self.last_reset = timezone.now()
            self._calculate_next_reset()
            self.save(update_fields=['used_quota', 'last_reset', 'next_reset', 'updated_at'])
    
    class Meta:
        verbose_name = 'User Scan Quota'
        verbose_name_plural = 'User Scan Quotas'
        ordering = ['user__username']


# Model untuk Feedback dari User
class Feedback(models.Model):
    """
    Model untuk menyimpan feedback dari user client/staff ke admin.
    Admin dapat membalas feedback ini.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text='User yang memberikan feedback'
    )
    message = models.TextField(
        help_text='Pesan feedback dari user'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Waktu feedback dibuat'
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text='Apakah feedback sudah ditangani'
    )
    reply = models.TextField(
        blank=True,
        null=True,
        help_text='Balasan dari admin'
    )
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replied_feedbacks',
        help_text='Admin yang membalas feedback'
    )
    replied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Waktu admin membalas feedback'
    )
    
    def __str__(self):
        return f"Feedback from {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']


# Model untuk Kerjasama dan Sponsorship
class Partnership(models.Model):
    """
    Model untuk menyimpan logo dan informasi kerjasama/sponsorship yang ditampilkan di footer.
    """
    PARTNERSHIP_TYPE_CHOICES = [
        ('partnership', 'Kerjasama'),
        ('sponsorship', 'Sponsorship'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Nama instansi/organisasi'
    )
    logo = models.ImageField(
        upload_to='partnerships/',
        help_text='Logo instansi/organisasi'
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL website instansi (opsional)'
    )
    partnership_type = models.CharField(
        max_length=20,
        choices=PARTNERSHIP_TYPE_CHOICES,
        default='partnership',
        help_text='Jenis kerjasama'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Apakah logo ditampilkan di footer'
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Urutan tampilan (0 = pertama)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_partnerships',
        help_text='Admin yang menambahkan kerjasama'
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_partnership_type_display()})"
    
    class Meta:
        verbose_name = 'Partnership/Sponsorship'
        verbose_name_plural = 'Partnerships/Sponsorships'
        ordering = ['display_order', 'name']


