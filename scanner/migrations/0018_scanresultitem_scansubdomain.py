# Generated manually for structured scan result storage

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0017_partnership'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScanResultItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(help_text='URL yang ditemukan', max_length=2048)),
                ('title', models.TextField(blank=True, help_text='Title dari halaman', null=True)),
                ('description', models.TextField(blank=True, help_text='Description/snippet dari halaman', null=True)),
                ('label', models.CharField(help_text='Label yang terdeteksi (hack judol, pornografi, dll)', max_length=100)),
                ('category_code', models.CharField(blank=True, help_text='Kode kategori (0=aman, 1=hack judol, 2=pornografi, 3=hacked)', max_length=10, null=True)),
                ('category_name', models.CharField(blank=True, help_text='Nama kategori', max_length=100, null=True)),
                ('verification_status', models.CharField(choices=[('LIVE', 'Live Malicious'), ('CACHE_ONLY', 'Cache Only'), ('VERIFIED_SAFE', 'Verified Safe'), ('UNVERIFIED', 'Unverified'), ('ERROR', 'Error')], default='UNVERIFIED', help_text='Status verifikasi halaman', max_length=20)),
                ('is_live', models.BooleanField(default=False, help_text='Apakah halaman masih live/aktif')),
                ('is_cache_only', models.BooleanField(default=False, help_text='Apakah hanya ditemukan di cache')),
                ('keywords_found', models.JSONField(blank=True, default=list, help_text='List keywords yang ditemukan di halaman')),
                ('confidence_score', models.FloatField(blank=True, help_text='Confidence score dari model', null=True)),
                ('risk_score', models.IntegerField(blank=True, help_text='Risk score (0-100)', null=True)),
                ('source', models.CharField(blank=True, help_text='Sumber data (Google, Bing, dll)', max_length=100, null=True)),
                ('discovered_at', models.DateTimeField(auto_now_add=True, help_text='Waktu item ditemukan')),
                ('js_analysis', models.JSONField(blank=True, default=dict, help_text='Hasil analisis JavaScript jika tersedia')),
                ('scan_history', models.ForeignKey(help_text='Scan history yang terkait', on_delete=django.db.models.deletion.CASCADE, related_name='result_items', to='scanner.scanhistory')),
            ],
            options={
                'verbose_name': 'Scan Result Item',
                'verbose_name_plural': 'Scan Result Items',
                'ordering': ['-discovered_at', '-risk_score'],
            },
        ),
        migrations.CreateModel(
            name='ScanSubdomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subdomain', models.CharField(help_text='Nama subdomain (contoh: www.example.com)', max_length=255)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address subdomain', null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Aktif'), ('INACTIVE', 'Tidak Aktif'), ('UNKNOWN', 'Tidak Diketahui')], default='UNKNOWN', help_text='Status subdomain', max_length=20)),
                ('discovery_method', models.CharField(blank=True, help_text='Teknik yang digunakan untuk menemukan subdomain (dns_lookup, web_search, certificate_transparency)', max_length=100, null=True)),
                ('discovered_at', models.DateTimeField(auto_now_add=True, help_text='Waktu subdomain ditemukan')),
                ('scan_history', models.ForeignKey(help_text='Scan history yang terkait', on_delete=django.db.models.deletion.CASCADE, related_name='subdomains', to='scanner.scanhistory')),
            ],
            options={
                'verbose_name': 'Scan Subdomain',
                'verbose_name_plural': 'Scan Subdomains',
                'ordering': ['subdomain'],
                'unique_together': {('scan_history', 'subdomain')},
            },
        ),
        migrations.AddIndex(
            model_name='scanresultitem',
            index=models.Index(fields=['scan_history', 'label'], name='scanner_sca_scan_hi_idx'),
        ),
        migrations.AddIndex(
            model_name='scanresultitem',
            index=models.Index(fields=['scan_history', 'verification_status'], name='scanner_sca_scan_hi_ver_idx'),
        ),
        migrations.AddIndex(
            model_name='scanresultitem',
            index=models.Index(fields=['url'], name='scanner_sca_url_idx'),
        ),
        migrations.AddIndex(
            model_name='scanresultitem',
            index=models.Index(fields=['is_live', 'label'], name='scanner_sca_is_live_idx'),
        ),
        migrations.AddIndex(
            model_name='scansubdomain',
            index=models.Index(fields=['scan_history', 'status'], name='scanner_sca_scan_hi_sta_idx'),
        ),
        migrations.AddIndex(
            model_name='scansubdomain',
            index=models.Index(fields=['subdomain'], name='scanner_sca_subdoma_idx'),
        ),
    ]

