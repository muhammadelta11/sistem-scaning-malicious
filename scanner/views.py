# scanner/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings # Untuk akses settings.py
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.html import escape
import json
import threading
import time # <-- Tambahkan import time
import os # <-- Tambahkan import os
import logging # <-- Tambahkan import logging
import sqlite3
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
import html
from django.contrib.auth.views import LoginView as DjangoLoginView


# --- Import fungsi inti dari modul lokal (gunakan relative import) ---
from . import core_scanner
from . import data_manager
from .models import ActivityLog, ScanHistory, MaliciousKeyword, SistemConfig
from .forms import ScanForm, KeywordForm, CustomUserCreationForm, CustomUserChangeForm, UserPasswordResetForm
from django.contrib.auth import get_user_model
from . import job_runner
from .services import ScanService, KeywordService, UserService, TrainingService
from .exceptions import DomainValidationError, ScanProcessingError, ResourceNotFound

User = get_user_model()

# Setup logger untuk file ini
logger = logging.getLogger(__name__)

# --- Helper Functions for PDF Export ---

def sanitize_string_for_pdf(value):
    """
    Sanitasi string untuk digunakan di PDF (escape HTML dan handle None).
    ReportLab menggunakan XML-like markup, jadi perlu escape karakter khusus.
    """
    if value is None:
        return 'N/A'
    
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception:
            return 'N/A'
    
    # Strip whitespace
    value = value.strip()
    
    if not value:
        return 'N/A'
    
    # Escape HTML entities untuk ReportLab Paragraph
    # ReportLab menggunakan subset XML, jadi perlu escape &, <, >
    value = html.escape(value, quote=False)
    
    # Replace karakter kontrol yang tidak valid
    value = ''.join(char if ord(char) >= 32 or char in '\n\t\r' else '' for char in value)
    
    return value

def safe_get_value(data_dict, key, default='N/A', sanitize=True):
    """
    Helper untuk mendapatkan nilai dari dictionary dengan handling None yang aman.
    """
    if not isinstance(data_dict, dict):
        return default
    
    value = data_dict.get(key)
    
    if value is None:
        return default
    
    if sanitize:
        return sanitize_string_for_pdf(value)
    
    return value if isinstance(value, str) else str(value)

# --- View Functions ---

@login_required
def dashboard(request):
    """
    Dashboard view untuk menampilkan statistik dan ringkasan aktivitas
    """
    import pandas as pd
    from datetime import datetime

    # Handle CSV import request
    if request.method == 'POST' and 'import_csv' in request.POST:
        from .services import DashboardService
        scanner_csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scanner', 'dashboard_ranking.csv')
        
        result = DashboardService.import_csv_to_database(scanner_csv_path)
        
        if result['success']:
            messages.success(request, f"CSV berhasil diimpor: {result['imported']} baru, {result['updated']} diperbarui")
        else:
            messages.error(request, f"Gagal mengimpor CSV: {result['message']}")
        
        return redirect('scanner:dashboard')

    # Load from CSV first, fallback to Database if CSV not available
    try:
        # Convert Path to string for os.path.join
        base_dir = str(settings.BASE_DIR) if hasattr(settings.BASE_DIR, '__str__') else settings.BASE_DIR
        csv_path = os.path.join(base_dir, 'dashboard_ranking.csv')
        
        logger.info(f"Checking CSV at path: {csv_path}")
        
        # Priority 1: Try loading from CSV file
        if os.path.exists(csv_path):
            logger.info("Loading dashboard data from CSV file")
            df = pd.read_csv(csv_path)
            df['last_scan'] = pd.to_datetime(df['last_scan'])
            
            stats = {
                'total_domains': len(df),
                'total_cases': int(df['jumlah_kasus'].sum()),
                'infected_domains': int(df[df['jumlah_kasus'] > 0]['jumlah_kasus'].count()),
                'max_cases': int(df['jumlah_kasus'].max())
            }
            
            ranking_data = []
            for _, row in df.iterrows():
                hack_judol_val = row.get('hack judol')
                if pd.isna(hack_judol_val):
                    hack_judol_val = row.get('hack_judol', 0)
                pornografi = row.get('pornografi', 0)
                hacked = row.get('hacked', 0)
                
                def safe_int_convert(value):
                    if pd.isna(value) or value == '':
                        return 0
                    try:
                        return int(float(value))
                    except (ValueError, TypeError):
                        return 0
                
                ranking_data.append({
                    'domain': row['domain'],
                    'jumlah_kasus': safe_int_convert(row['jumlah_kasus']),
                    'hack_judol': safe_int_convert(hack_judol_val),
                    'pornografi': safe_int_convert(pornografi),
                    'hacked': safe_int_convert(hacked),
                    'last_scan': row['last_scan']
                })
            
            ranking_data.sort(key=lambda x: x['jumlah_kasus'], reverse=True)
            
            # Prepare chart data from CSV
            chart_data = None
            if len(df) > 0:
                df['scan_month'] = df['last_scan'].dt.to_period('M').dt.strftime('%Y-%m')
                monthly_scans = df.groupby('scan_month').size().reset_index(name='count')
                monthly_scans = monthly_scans.sort_values('scan_month')
                
                # Calculate pie chart data (by category)
                # CSV has 'hack judol' (with space) column
                hack_judol_col = df.get('hack judol', 0)
                if isinstance(hack_judol_col, int):
                    hack_judol_col = df.get('hack_judol', 0)
                total_hack_judol = int(hack_judol_col.sum()) if hasattr(hack_judol_col, 'sum') else int(df['jumlah_kasus'].sum())
                total_pornografi = int(df['pornografi'].sum()) if 'pornografi' in df.columns else 0
                total_hacked = int(df['hacked'].sum()) if 'hacked' in df.columns else 0
                
                chart_data = {
                    'activity_chart': {
                        'labels': monthly_scans['scan_month'].tolist(),
                        'datasets': [{
                            'label': 'Jumlah Domain',
                            'data': monthly_scans['count'].tolist(),
                            'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                            'borderColor': 'rgba(54, 162, 235, 1)',
                            'borderWidth': 1
                        }]
                    },
                    'pie_chart': {
                        'labels': ['Hack Judol', 'Pornografi', 'Hacked'],
                        'datasets': [{
                            'data': [total_hack_judol, total_pornografi, total_hacked],
                            'backgroundColor': ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)'],
                            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
                            'borderWidth': 1
                        }]
                    }
                }
        else:
            # Priority 2: Fallback to Database if CSV not found
            logger.info("CSV not found, falling back to Database")
            from .models import DomainScanSummary
            summaries = DomainScanSummary.objects.all()
            
            if summaries.count() > 0:
                logger.info(f"Loading {summaries.count()} domain summaries from database")
                
                # Calculate stats
                stats = {
                    'total_domains': summaries.count(),
                    'total_cases': sum(s.total_cases for s in summaries),
                    'infected_domains': summaries.filter(total_cases__gt=0).count(),
                    'max_cases': max([s.total_cases for s in summaries], default=0)
                }
                
                # Prepare ranking data
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
                
                # Prepare chart data from DB (group by month)
                chart_data = None
                if summaries.exists():
                    from django.db.models.functions import TruncMonth
                    from django.db.models import Count
                    monthly_counts = summaries.annotate(
                        scan_month=TruncMonth('last_scan')
                    ).values('scan_month').annotate(
                        count=Count('id')
                    ).order_by('scan_month')
                    
                    chart_data = {
                        'labels': [m['scan_month'].strftime('%Y-%m') for m in monthly_counts],
                        'data': [m['count'] for m in monthly_counts]
                    }
            else:
                # No data in CSV or DB
                stats = {'total_domains': 0, 'total_cases': 0, 'infected_domains': 0, 'max_cases': 0}
                ranking_data = []
                chart_data = None

    except Exception as e:
        logger.error(f"Error loading dashboard data: {e}", exc_info=True)
        stats = {
            'total_domains': 0,
            'total_cases': 0,
            'infected_domains': 0,
            'max_cases': 0
        }
        ranking_data = []
        chart_data = None

    # Get system configuration info
    try:
        from .models import SistemConfig
        system_config = SistemConfig.get_active_config()
        
        # Get API key status
        from django.conf import settings as django_settings
        api_key_configured = bool(getattr(django_settings, 'ADMIN_SERPAPI_KEY', None))
        
        # Calculate estimated API usage
        estimated_api_calls = 0
        if system_config.use_comprehensive_query:
            estimated_api_calls += 1  # Google search
        else:
            estimated_api_calls += 4
        
        if system_config.enable_bing_search:
            estimated_api_calls += 1
        
        if system_config.enable_subdomain_search:
            estimated_api_calls += 2
        
        if system_config.enable_subdomain_content_scan:
            estimated_api_calls += system_config.max_subdomains_to_scan
        
        if system_config.enable_backlink_analysis:
            estimated_api_calls += 1
            
        # Get ML model status
        try:
            import joblib
            model_path = os.path.join(django_settings.BASE_DIR, 'seo_poisoning_best_model.joblib')
            if os.path.exists(model_path):
                ml_model = joblib.load(model_path)
                model_available = True
            else:
                model_available = False
        except:
            model_available = False
        
        # Get recent scan history - filtered by user if not admin
        from .models import ScanHistory
        if request.user.is_admin:
            # Admin: Show all scan history
            recent_scans = ScanHistory.objects.all().order_by('-start_time')[:10]
            total_scans = ScanHistory.objects.all().count()
            completed_scans = ScanHistory.objects.filter(status='COMPLETED').count()
            failed_scans = ScanHistory.objects.filter(status='FAILED').count()
        else:
            # Regular user: Show only their own scan history
            recent_scans = ScanHistory.objects.filter(user=request.user).order_by('-start_time')[:10]
            total_scans = ScanHistory.objects.filter(user=request.user).count()
            completed_scans = ScanHistory.objects.filter(user=request.user, status='COMPLETED').count()
            failed_scans = ScanHistory.objects.filter(user=request.user, status='FAILED').count()
        
    except Exception as e:
        logger.warning(f"Error loading system info: {e}")
        system_config = None
        api_key_configured = False
        estimated_api_calls = 0
        model_available = False
        recent_scans = []
        total_scans = 0
        completed_scans = 0
        failed_scans = 0
    
    # Convert chart_data to JSON if it exists
    chart_data_json = None
    if chart_data:
        try:
            chart_data_json = json.dumps(chart_data)
        except Exception as e:
            logger.error(f"Error serializing chart_data: {e}")
            chart_data_json = None
    
    # Get limit from request parameter or use default (None = all data)
    ranking_limit = request.GET.get('ranking_limit', None)
    if ranking_limit:
        try:
            ranking_limit = int(ranking_limit)
            if ranking_limit <= 0:
                ranking_limit = None  # Show all if invalid
        except (ValueError, TypeError):
            ranking_limit = None  # Show all if invalid
    
    # Apply limit if specified, otherwise show all data
    if ranking_limit:
        ranking_data_display = ranking_data[:ranking_limit]
    else:
        ranking_data_display = ranking_data  # Show all data
    
    context = {
        'user': request.user,  # Add user to context for template
        'stats': stats,
        'ranking_data': ranking_data_display,  # All data or limited based on parameter
        'ranking_data_all': ranking_data,  # Keep all data for reference
        'ranking_limit': ranking_limit,  # Current limit (None = all)
        'total_ranking_count': len(ranking_data),  # Total count for display
        'chart_data': chart_data,
        'chart_data_json': chart_data_json,  # Add JSON string version
        'system_config': system_config,
        'api_key_configured': api_key_configured,
        'estimated_api_calls': estimated_api_calls,
        'model_available': model_available,
        'recent_scans': recent_scans,
        'total_scans': total_scans,
        'completed_scans': completed_scans,
        'failed_scans': failed_scans,
    }
    return render(request, 'scanner/dashboard.html', context)

@login_required
def scanner_view(request):
    """
    Halaman utama scanner untuk melakukan scanning domain
    """
    if request.method == 'POST':
        form = ScanForm(request.POST)
        if form.is_valid():
            domain = form.cleaned_data['domain']
            scan_type = form.cleaned_data['scan_type']
            enable_verification = form.cleaned_data.get('enable_verification', True)
            show_all_results = form.cleaned_data.get('show_all_results', False)

            try:
                scan_obj = ScanService.create_scan(
                    user=request.user,
                    domain=domain,
                    scan_type=scan_type,
                    enable_verification=enable_verification,
                    show_all_results=show_all_results
                )
                messages.success(request, f'Scanning untuk domain {domain} dimulai di background.')
            except DomainValidationError as e:
                messages.error(request, f'Domain tidak valid: {str(e)}')
            except ScanProcessingError as e:
                messages.error(request, f'Error saat memulai scanning: {str(e)}')
            except Exception as e:
                logger.error(f"Unexpected error in scanner_view: {e}", exc_info=True)
                messages.error(request, f'Terjadi kesalahan: {str(e)}')

            return redirect('scanner:scanner_page')
    else:
        form = ScanForm()
        
        # Get quota status - semua user (kecuali superuser) bisa melihat quota mereka
        quota_status = None
        if not request.user.is_superuser:
            from .services import QuotaService
            quota_status = QuotaService.check_quota(request.user)

    user_scans = ScanService.get_user_scans(request.user, limit=None)

    context = {
        'form': form,
        'user_scans': user_scans,
        'quota_status': quota_status,
        'is_premium': request.user.is_premium if hasattr(request.user, 'is_premium') else False,
    }
    return render(request, 'scanner/scanner_page.html', context)

@login_required
def profile_view(request):
    """Halaman profil pengguna"""
    from .models import ScanHistory
    
    # Get user statistics
    user_scans = ScanHistory.objects.filter(user=request.user)
    total_scans = user_scans.count()
    completed_scans = user_scans.filter(status='COMPLETED').count()
    failed_scans = user_scans.filter(status='FAILED').count()
    pending_scans = user_scans.filter(status='PENDING').count()
    
    # Calculate total domains scanned (unique)
    unique_domains = user_scans.values('domain').distinct().count()
    
    # Get recent scans
    recent_scans = user_scans.order_by('-start_time')[:5]
    
    # Get quota status - semua user (kecuali superuser) bisa melihat quota mereka
    quota_status = None
    if not request.user.is_superuser:
        from .services import QuotaService
        quota_status = QuotaService.check_quota(request.user)
    
    # Get premium status
    is_premium = request.user.is_premium if hasattr(request.user, 'is_premium') else False
    
    context = {
        'total_scans': total_scans,
        'completed_scans': completed_scans,
        'failed_scans': failed_scans,
        'pending_scans': pending_scans,
        'unique_domains': unique_domains,
        'recent_scans': recent_scans,
        'quota_status': quota_status,
        'is_premium': is_premium,
    }
    
    return render(request, 'scanner/profile.html', context)

@login_required
def config_view(request):
    """Halaman konfigurasi sistem"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    # Get or create system config
    config = SistemConfig.get_active_config()

    if request.method == 'POST':
        # Handle old native flow checkbox (backward compatibility)
        if 'use_native_flow' in request.POST:
            use_native = request.POST.get('use_native_flow') == 'on'
            cache.set('scanner_use_native_flow', use_native, timeout=86400)
            messages.success(request, f"Mode scan diubah ke: {'Native' if use_native else 'Verified'}")
            return redirect('scanner:config')
        
        # Handle system config update
        if 'update_config' in request.POST:
            # Update all config fields
            config.enable_api_cache = request.POST.get('enable_api_cache') == 'on'
            config.api_cache_ttl_days = int(request.POST.get('api_cache_ttl_days', 7))
            config.use_comprehensive_query = request.POST.get('use_comprehensive_query') == 'on'
            config.max_search_results = int(request.POST.get('max_search_results', 100))
            config.enable_bing_search = request.POST.get('enable_bing_search') == 'on'
            config.enable_duckduckgo_search = request.POST.get('enable_duckduckgo_search') == 'on'
            config.enable_subdomain_dns_lookup = request.POST.get('enable_subdomain_dns_lookup') == 'on'
            config.enable_subdomain_search = request.POST.get('enable_subdomain_search') == 'on'
            config.enable_subdomain_content_scan = request.POST.get('enable_subdomain_content_scan') == 'on'
            config.max_subdomains_to_scan = int(request.POST.get('max_subdomains_to_scan', 10))
            config.enable_deep_crawling = request.POST.get('enable_deep_crawling') == 'on'
            config.enable_sitemap_analysis = request.POST.get('enable_sitemap_analysis') == 'on'
            config.enable_path_discovery = request.POST.get('enable_path_discovery') == 'on'
            config.enable_graph_analysis = request.POST.get('enable_graph_analysis') == 'on'
            config.max_crawl_pages = int(request.POST.get('max_crawl_pages', 50))
            config.enable_realtime_verification = request.POST.get('enable_realtime_verification') == 'on'
            config.use_tiered_verification = request.POST.get('use_tiered_verification') == 'on'
            config.enable_illegal_content_detection = request.POST.get('enable_illegal_content_detection') == 'on'
            config.enable_hidden_content_detection = request.POST.get('enable_hidden_content_detection') == 'on'
            config.enable_injection_detection = request.POST.get('enable_injection_detection') == 'on'
            config.enable_unindexed_discovery = request.POST.get('enable_unindexed_discovery') == 'on'
            config.enable_backlink_analysis = request.POST.get('enable_backlink_analysis') == 'on'
            config.notes = request.POST.get('notes', '')
            config.updated_by = request.user
            config.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE_SYSTEM_CONFIG',
                details='Updated system configuration via web interface'
            )
            
            messages.success(request, 'Konfigurasi sistem berhasil diperbarui!')
            return redirect('scanner:config')
        
        # Handle API key management
        if 'manage_api_key' in request.POST:
            key_id = request.POST.get('key_id')
            key_name = request.POST.get('key_name')
            key_value = request.POST.get('key_value')
            description = request.POST.get('description', '')
            
            try:
                from .models import ApiKey
                if key_id and key_id != 'new':
                    # Update existing
                    apikey = ApiKey.objects.get(id=key_id)
                    apikey.key_name = key_name
                    apikey.key_value = key_value
                    apikey.description = description
                    apikey.save()
                    messages.success(request, 'API key berhasil diperbarui!')
                else:
                    # Create new
                    ApiKey.objects.create(
                        key_name=key_name,
                        key_value=key_value,
                        description=description,
                        created_by=request.user
                    )
                    messages.success(request, 'API key baru berhasil ditambahkan!')
                
                ActivityLog.objects.create(
                    user=request.user,
                    action='MANAGE_API_KEY',
                    details=f'{"Updated" if key_id else "Created"} API key: {key_name}'
                )
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:config')
        
        # Handle API key delete
        if 'delete_api_key' in request.POST:
            key_id = request.POST.get('key_id')
            try:
                from .models import ApiKey
                apikey = ApiKey.objects.get(id=key_id)
                key_name = apikey.key_name
                apikey.delete()
                messages.success(request, f'API key {key_name} berhasil dihapus!')
                
                ActivityLog.objects.create(
                    user=request.user,
                    action='DELETE_API_KEY',
                    details=f'Deleted API key: {key_name}'
                )
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:config')
        
        # Handle API key toggle active
        if 'toggle_api_key' in request.POST:
            key_id = request.POST.get('key_id')
            try:
                from .models import ApiKey
                apikey = ApiKey.objects.get(id=key_id)
                apikey.is_active = not apikey.is_active
                apikey.save()
                status = 'diaktifkan' if apikey.is_active else 'dinonaktifkan'
                messages.success(request, f'API key {apikey.key_name} berhasil {status}!')
                
                ActivityLog.objects.create(
                    user=request.user,
                    action='TOGGLE_API_KEY',
                    details=f'Toggled API key {apikey.key_name} to {"active" if apikey.is_active else "inactive"}'
                )
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:config')
        
        # Handle production settings update
        if 'update_production_settings' in request.POST:
            try:
                from .models import ProductionSettings
                prod_settings = ProductionSettings.get_active_settings()
                
                # Django settings
                prod_settings.debug_mode = request.POST.get('debug_mode') == 'on'
                prod_settings.allowed_hosts = request.POST.get('allowed_hosts', '')
                
                # Security settings
                prod_settings.csrf_cookie_secure = request.POST.get('csrf_cookie_secure') == 'on'
                prod_settings.session_cookie_secure = request.POST.get('session_cookie_secure') == 'on'
                prod_settings.secure_ssl_redirect = request.POST.get('secure_ssl_redirect') == 'on'
                
                # Email settings
                prod_settings.email_enabled = request.POST.get('email_enabled') == 'on'
                prod_settings.email_host = request.POST.get('email_host', '')
                prod_settings.email_port = int(request.POST.get('email_port', 587))
                prod_settings.email_use_tls = request.POST.get('email_use_tls') == 'on'
                
                # Mobile API settings
                prod_settings.mobile_api_enabled = request.POST.get('mobile_api_enabled') == 'on'
                prod_settings.mobile_api_rate_limit = int(request.POST.get('mobile_api_rate_limit', 100))
                
                # Backup settings
                prod_settings.auto_backup_enabled = request.POST.get('auto_backup_enabled') == 'on'
                prod_settings.backup_frequency_days = int(request.POST.get('backup_frequency_days', 1))
                
                prod_settings.updated_by = request.user
                prod_settings.save()
                
                ActivityLog.objects.create(
                    user=request.user,
                    action='UPDATE_PRODUCTION_SETTINGS',
                    details='Updated production settings via web interface'
                )
                
                messages.success(request, 'Production settings berhasil diperbarui!')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:config')

    try:
        import joblib
        model = joblib.load('seo_poisoning_best_model.joblib')
        model_available = True
    except:
        model = None
        model_available = False

    keywords = MaliciousKeyword.objects.all().order_by('-created_at')
    total_domains = 0

    use_native_flow = cache.get('scanner_use_native_flow')
    if use_native_flow is None:
        use_native_flow = getattr(settings, 'USE_NATIVE_FLOW', True)

    # Determine which preset is currently active
    active_preset = 'custom'
    
    # Check if config matches any preset
    if (config.enable_api_cache and config.api_cache_ttl_days == 14 and 
        config.use_comprehensive_query and config.max_search_results == 100 and
        not config.enable_bing_search and config.enable_duckduckgo_search and
        config.enable_subdomain_dns_lookup and not config.enable_subdomain_search and
        not config.enable_subdomain_content_scan and config.max_subdomains_to_scan == 5 and
        config.enable_deep_crawling and config.enable_sitemap_analysis and
        config.enable_path_discovery and not config.enable_graph_analysis and
        config.max_crawl_pages == 30 and config.enable_realtime_verification and
        config.use_tiered_verification and config.enable_illegal_content_detection and
        config.enable_hidden_content_detection and config.enable_injection_detection and
        not config.enable_unindexed_discovery and not config.enable_backlink_analysis):
        active_preset = 'hemat'
    elif (config.enable_api_cache and config.api_cache_ttl_days == 7 and
          config.use_comprehensive_query and config.max_search_results == 100 and
          not config.enable_bing_search and config.enable_duckduckgo_search and
          config.enable_subdomain_dns_lookup and not config.enable_subdomain_search and
          not config.enable_subdomain_content_scan and config.max_subdomains_to_scan == 10 and
          config.enable_deep_crawling and config.enable_sitemap_analysis and
          config.enable_path_discovery and config.enable_graph_analysis and
          config.max_crawl_pages == 50 and config.enable_realtime_verification and
          config.use_tiered_verification and config.enable_illegal_content_detection and
          config.enable_hidden_content_detection and config.enable_injection_detection and
          config.enable_unindexed_discovery and not config.enable_backlink_analysis):
        active_preset = 'balance'
    elif (config.enable_api_cache and config.api_cache_ttl_days == 7 and
          config.use_comprehensive_query and config.max_search_results == 200 and
          config.enable_bing_search and config.enable_duckduckgo_search and
          config.enable_subdomain_dns_lookup and config.enable_subdomain_search and
          config.enable_subdomain_content_scan and config.max_subdomains_to_scan == 20 and
          config.enable_deep_crawling and config.enable_sitemap_analysis and
          config.enable_path_discovery and config.enable_graph_analysis and
          config.max_crawl_pages == 100 and config.enable_realtime_verification and
          config.use_tiered_verification and config.enable_illegal_content_detection and
          config.enable_hidden_content_detection and config.enable_injection_detection and
          config.enable_unindexed_discovery and config.enable_backlink_analysis):
        active_preset = 'lengkap'
    
    # Get API key status
    from django.conf import settings as django_settings
    api_key_configured = bool(getattr(django_settings, 'ADMIN_SERPAPI_KEY', None))
    api_key_preview = ''
    if api_key_configured:
        key_value = getattr(django_settings, 'ADMIN_SERPAPI_KEY', '')
        if len(key_value) > 10:
            api_key_preview = f"{key_value[:6]}...{key_value[-4:]}"
    
    # Get API Keys from database
    try:
        from .models import ApiKey, ProductionSettings
        api_keys = ApiKey.objects.all().order_by('-created_at')
        production_settings = ProductionSettings.get_active_settings()
    except:
        api_keys = []
        production_settings = None
    
    context = {
        'model': model_available,
        'keywords': keywords,
        'stats': {'total_domains': total_domains},
        'use_native_flow': use_native_flow,
        'username': request.user.username,
        'organization': getattr(request.user, 'organization_name', 'N/A'),
        'config': config,  # Add config to context
        'active_preset': active_preset,  # Add active preset
        'api_key_configured': api_key_configured,  # Add API key status
        'api_key_preview': api_key_preview,  # Add API key preview
        'api_keys': api_keys,  # Add API keys from DB
        'production_settings': production_settings,  # Add production settings
    }
    return render(request, 'scanner/config.html', context)

@login_required
def audit_view(request):
    """Halaman audit log"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    audit_logs = ActivityLog.objects.all().order_by('-timestamp')
    context = {'audit_logs': audit_logs}
    return render(request, 'scanner/audit.html', context)

@login_required
def users_view(request):
    """Halaman manajemen pengguna"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    users = UserService.get_all_users()
    
    # Get quota info for each user
    from .services import QuotaService
    users_with_quota = []
    for user in users:
        # Get or create quota (will auto-fix if quota_limit=0 for client users)
        quota = QuotaService.get_or_create_quota(user)
        # Refresh quota from DB to ensure we have latest values
        quota.refresh_from_db()
        quota_status = QuotaService.check_quota(user)
        users_with_quota.append({
            'user': user,
            'quota': quota,
            'quota_status': quota_status
        })
    
    context = {
        'all_users': users,
        'users_with_quota': users_with_quota,
    }
    return render(request, 'scanner/users.html', context)

@login_required
def training_view(request):
    """Halaman training model ML"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')
    
    # Check dataset and model status
    dataset_exists, dataset_msg, dataset_rows = TrainingService.check_dataset()
    model_exists, model_msg, model_info = TrainingService.check_model()
    
    # Training result (if just trained)
    training_result = None
    if request.method == 'POST' and 'train_model' in request.POST:
        # Perform training
        dataset_path = TrainingService.get_dataset_path()
        training_result = TrainingService.train_model(dataset_path)
        
        if training_result['success']:
            messages.success(request, training_result['message'])
            # Recheck model status after training
            model_exists, model_msg, model_info = TrainingService.check_model()
        else:
            messages.error(request, training_result['message'])
    
    context = {
        'dataset_exists': dataset_exists,
        'dataset_msg': dataset_msg,
        'dataset_rows': dataset_rows,
        'model_exists': model_exists,
        'model_msg': model_msg,
        'model_info': model_info,
        'training_result': training_result,
    }
    
    return render(request, 'scanner/training.html', context)

@login_required
def user_create_view(request):
    """View untuk membuat pengguna baru"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna berhasil dibuat.')
            return redirect('scanner:users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'scanner/user_form.html', {'form': form})

@login_required
def user_edit_view(request, user_id):
    """View untuk mengedit pengguna"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna berhasil diperbarui.')
            return redirect('scanner:users')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'scanner/user_form.html', {'form': form})

@login_required
def user_delete_view(request, user_id):
    """View untuk menghapus pengguna"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Pengguna berhasil dihapus.')
        return redirect('scanner:users')
    return render(request, 'scanner/user_delete.html', {'user': user})

@login_required
@require_POST
def user_toggle_active_view(request, user_id):
    """View untuk toggle status aktif/non-aktif user"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    user = get_object_or_404(User, id=user_id)
    
    # Prevent deactivating yourself
    if user.id == request.user.id:
        messages.error(request, 'Anda tidak dapat menonaktifkan akun sendiri.')
        return redirect('scanner:users')
    
    # Toggle status
    old_status = user.is_active
    user.is_active = not user.is_active
    user.save()
    
    # Log aktivitas
    from .models import ActivityLog
    ActivityLog.objects.create(
        user=request.user,
        action='TOGGLE_USER_ACTIVE',
        details=f'{"Mengaktifkan" if user.is_active else "Menonaktifkan"} user: {user.username} (Status: {old_status} → {user.is_active})'
    )
    
    status_text = "diaktifkan" if user.is_active else "dinonaktifkan"
    messages.success(request, f'User {user.username} berhasil {status_text}.')
    return redirect('scanner:users')

@login_required
def user_manage_quota_view(request, user_id):
    """View untuk mengelola kuota user"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    user = get_object_or_404(User, id=user_id)
    
    from .services import QuotaService
    
    if request.method == 'POST':
        quota_limit = request.POST.get('quota_limit')
        reset_period = request.POST.get('reset_period')
        
        try:
            # Validate and convert
            quota_limit = int(quota_limit) if quota_limit and quota_limit.strip() else None
            
            # Validate quota_limit >= 0
            if quota_limit is not None and quota_limit < 0:
                messages.error(request, 'Batas kuota tidak boleh negatif.')
                quota_limit = None
            
            # Update quota (hanya quota_limit dan reset_period, tidak update used_quota)
            updated_quota = QuotaService.update_quota(
                user=user,
                quota_limit=quota_limit,
                reset_period=reset_period if reset_period else None,
                used_quota=None  # Tidak update used_quota, biarkan sistem yang update otomatis
            )
            
            # Log aktivitas
            from .models import ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE_QUOTA',
                details=f'Updated quota for {user.username}: limit={updated_quota.quota_limit} (unlimited={updated_quota.is_unlimited}), reset={updated_quota.reset_period}, used={updated_quota.used_quota}'
            )
            
            messages.success(request, f'Kuota untuk {user.username} berhasil diperbarui: {updated_quota.quota_limit if updated_quota.quota_limit > 0 else "Unlimited"} ({updated_quota.used_quota} terpakai).')
            return redirect('scanner:users')
        except ValueError as e:
            messages.error(request, f'Format kuota tidak valid: {str(e)}')
        except Exception as e:
            logger.error(f"Error updating quota for user {user.username}: {e}", exc_info=True)
            messages.error(request, f'Terjadi kesalahan saat memperbarui kuota: {str(e)}')
    
    # GET request - show form
    quota = QuotaService.get_or_create_quota(user)
    quota_status = QuotaService.check_quota(user)
    
    context = {
        'target_user': user,
        'quota': quota,
        'quota_status': quota_status,
    }
    return render(request, 'scanner/user_manage_quota.html', context)

@login_required
def user_reset_password_view(request, user_id):
    """View untuk reset password pengguna"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    user = UserService.get_user(user_id)
    if not user:
        messages.error(request, 'User tidak ditemukan.')
        return redirect('scanner:users')
    
    if request.method == 'POST':
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Password untuk {user.username} berhasil direset.')
            return redirect('scanner:users')
    else:
        form = UserPasswordResetForm()

    context = {'form': form, 'user': user}
    return render(request, 'scanner/user_reset_password.html', context)

@login_required
def get_scan_status(request, scan_id):
    """API endpoint untuk mengambil status scan"""
    progress_data = ScanService.get_scan_progress(scan_id)
    return JsonResponse(progress_data)

@csrf_exempt
@require_POST
@login_required
def validate_scan_result(request):
    """API endpoint untuk menambahkan hasil scan ke dataset (admin only)"""
    from .services import DatasetService
    from .exceptions import PermissionDenied

    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Hanya admin yang dapat menambahkan data ke dataset.'}, status=403)

    try:
        import json
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            url = data.get('url')
            title = data.get('title', '')
            description = data.get('description', '')
            label_status = data.get('label_status', 'malicious')
        else:
            url = request.POST.get('url')
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            label_status = request.POST.get('label_status', 'malicious')

        if not url:
            return JsonResponse({'success': False, 'error': 'URL diperlukan.'}, status=400)

        success = DatasetService.add_to_dataset(url, title, description, label_status, request.user)
        
        if success:
            ActivityLog.objects.create(
                user=request.user,
                action='ADD_TO_DATASET',
                details=f'Added URL to dataset via API: {url} ({label_status})'
            )
            return JsonResponse({'success': True, 'message': f'URL "{url}" berhasil ditambahkan ke dataset.'})
        else:
            return JsonResponse({'success': False, 'error': 'URL mungkin sudah ada di dataset atau terjadi kesalahan.'}, status=400)
            
    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        logger.error(f"Error in validate_scan_result: {e}", exc_info=True)
        error_msg = str(e)
        if 'ScannerException' in error_msg:
            error_msg = error_msg.replace('ScannerException: ', '').replace('ScannerException(', '').replace(')', '')
        return JsonResponse({'success': False, 'error': error_msg or 'Terjadi kesalahan saat menambahkan data.'}, status=500)

@login_required
def scan_detail_view(request, scan_pk):
    """View untuk detail scan"""
    from .services import DashboardService
    from .utils.formatters import format_domain_info
    from .models import ScanResultItem, ScanSubdomain
    from .services.scan_result_storage_service import ScanResultStorageService

    scan = get_object_or_404(ScanHistory, pk=scan_pk, user=request.user)

    results = None
    formatted_domain_info = None
    subdomain_results = None

    # Prioritas utama: Ambil dari permanent storage untuk semua user
    permanent_results_used = False
    try:
        from .services import PermanentStorageService
        permanent_results = PermanentStorageService.get_scan_result(scan)
        if permanent_results:
            results = permanent_results
            # Normalisasi hasil scan
            from .utils.normalizers import normalize_scan_results
            results = normalize_scan_results(results)
            # Set domain_info
            if results.get('domain_info'):
                formatted_domain_info = format_domain_info(results.get('domain_info', {}))
            subdomain_results = results.get('subdomain_results', {})
            permanent_results_used = True
            logger.info(f"Using permanent storage for scan detail {scan.scan_id}")
    except Exception as e:
        logger.warning(f"Error retrieving permanent storage for scan detail {scan.scan_id}: {e}")

    # Jika tidak ada permanent storage, gunakan model terstruktur atau JSON
    if not permanent_results_used:
        # Prioritas: Ambil dari model terstruktur (ScanResultItem & ScanSubdomain) jika ada
        # Fallback: Ambil dari JSON jika model belum ada (backward compatibility)
        has_structured_data = ScanResultItem.objects.filter(scan_history=scan).exists()
    
    # Jika tidak ada structured data tapi ada JSON, coba backfill (lazy backfill)
    if not has_structured_data and scan.scan_results_json and scan.status == 'COMPLETED':
        try:
            # Lazy backfill: otomatis convert JSON ke structured data saat diakses
            from .services.scan_result_storage_service import ScanResultStorageService
            backfill_stats = ScanResultStorageService.backfill_scan_from_json(scan)
            if backfill_stats['items_saved'] > 0 or backfill_stats['subdomains_saved'] > 0:
                logger.info(f"Auto-backfilled scan {scan.scan_id} from JSON")
                has_structured_data = True
        except Exception as e:
            logger.warning(f"Failed to auto-backfill scan {scan.scan_id}: {e}", exc_info=True)
    
    if has_structured_data:
        # Ambil data dari model terstruktur
        try:
            # Ambil semua items dari database
            result_items = ScanResultItem.objects.filter(scan_history=scan).order_by('-discovered_at', '-risk_score')
            subdomains = ScanSubdomain.objects.filter(scan_history=scan).order_by('subdomain')
            
            # Reconstruct results structure dari database
            results = {
                'categories': {},
                'total_pages': result_items.count(),
                'verified_scan': scan.ran_with_verification,
                'timed_out': False,
            }
            
            # Group items by category
            for item in result_items:
                cat_code = item.category_code or '0'
                cat_name = item.category_name or item.label
                
                if cat_code not in results['categories']:
                    results['categories'][cat_code] = {
                        'name': cat_name,
                        'items': []
                    }
                
                # Convert ScanResultItem ke format yang diharapkan template
                item_dict = {
                    'url': item.url,
                    'title': item.title or 'No Title',
                    'snippet': item.description or '',
                    'description': item.description or '',
                    'label': item.label,
                    'category_code': cat_code,
                    'category_name': cat_name,
                    'verification_status': item.verification_status,
                    'is_live': item.is_live,
                    'is_cache_only': item.is_cache_only,
                    'keywords_found': item.keywords_found or [],
                    'confidence': item.confidence_score,
                    'risk_score': item.risk_score,
                    'source': item.source,
                    'js_analysis': item.js_analysis or {},
                    'verification': {
                        'is_live': item.is_live,
                        'is_cache_only': item.is_cache_only,
                    }
                }
                results['categories'][cat_code]['items'].append(item_dict)
            
            # Convert subdomains ke format yang diharapkan
            subdomain_results = {
                'total_subdomains': subdomains.count(),
                'subdomains': [
                    {
                        'subdomain': sub.subdomain,
                        'ip': sub.ip_address,
                        'ip_address': sub.ip_address,
                        'status': sub.status,
                        'discovery_method': sub.discovery_method or 'unknown'
                    }
                    for sub in subdomains
                ],
                'techniques_used': list(set([s.discovery_method for s in subdomains if s.discovery_method]))
            }
            
            # Ambil domain_info dari JSON jika ada (untuk backward compatibility)
            if scan.scan_results_json:
                try:
                    json_results = json.loads(scan.scan_results_json)
                    if json_results.get('domain_info'):
                        results['domain_info'] = json_results['domain_info']
                        formatted_domain_info = format_domain_info(results['domain_info'])
                    if json_results.get('final_conclusion'):
                        results['final_conclusion'] = json_results['final_conclusion']
                    if json_results.get('graph_analysis'):
                        results['graph_analysis'] = json_results['graph_analysis']
                except:
                    pass
            
            # Add global_index untuk setiap item (untuk kompatibilitas dengan item_analysis_view)
            global_index = 0
            for cat_code, category in results.get('categories', {}).items():
                for item in category.get('items', []):
                    item['global_index'] = global_index
                    global_index += 1
            
        except Exception as e:
            logger.error(f"Error loading structured scan data: {e}", exc_info=True)
            has_structured_data = False
    
    # Fallback: Ambil dari JSON jika model belum ada (backward compatibility)
    if not has_structured_data and scan.scan_results_json:
        try:
            results = json.loads(scan.scan_results_json)
            # Normalisasi hasil scan untuk memastikan struktur lengkap
            from .utils.normalizers import normalize_scan_results
            results = normalize_scan_results(results)
            
            if results.get('domain_info'):
                formatted_domain_info = format_domain_info(results.get('domain_info', {}))
            subdomain_results = results.get('subdomain_results', {})
            
            global_index = 0
            for cat_code, category in results.get('categories', {}).items():
                for item in category.get('items', []):
                    item['global_index'] = global_index
                    item['category_code'] = cat_code
                    item['category_name'] = category.get('name', 'Unknown')
                    global_index += 1
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing scan results JSON: {e}", exc_info=True)
            results = None
    
    dashboard_summary = DashboardService.get_dashboard_summary(scan.domain)
    
    scan_duration = None
    if scan.end_time and scan.start_time:
        duration = scan.end_time - scan.start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            scan_duration = f"{hours} jam {minutes} menit {seconds} detik"
        elif minutes > 0:
            scan_duration = f"{minutes} menit {seconds} detik"
        else:
            scan_duration = f"{seconds} detik"
    
    context = {
        'scan': scan,
        'results': results,
        'domain_info': formatted_domain_info,
        'subdomain_results': subdomain_results,
        'dashboard_summary': dashboard_summary,
        'scan_duration': scan_duration,
        'has_structured_data': has_structured_data,  # Flag untuk template
    }
    return render(request, 'scanner/scan_detail.html', context)

@login_required
def keywords_view(request):
    """View untuk menampilkan daftar keywords"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    keywords = KeywordService.get_all_keywords()
    context = {'keywords': keywords}
    return render(request, 'scanner/keywords.html', context)

@login_required
def keyword_create_view(request):
    """View untuk membuat keyword baru"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    if request.method == 'POST':
        form = KeywordForm(request.POST)
        if form.is_valid():
            try:
                keyword = KeywordService.create_keyword(
                    keyword=form.cleaned_data['keyword'],
                    category=form.cleaned_data['category'],
                    is_active=form.cleaned_data.get('is_active', True),
                    created_by=request.user
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action='CREATE_KEYWORD',
                    details=f'Created keyword: {keyword.keyword} ({keyword.category})'
                )
                messages.success(request, f'Keyword "{keyword.keyword}" berhasil ditambahkan.')
                return redirect('scanner:keywords')
            except Exception as e:
                logger.error(f"Error creating keyword: {e}", exc_info=True)
                messages.error(request, f'Error: {str(e)}')
    else:
        form = KeywordForm()

    context = {'form': form, 'title': 'Tambah Keyword Baru'}
    return render(request, 'scanner/keyword_form.html', context)

@login_required
def keyword_edit_view(request, keyword_id):
    """View untuk mengedit keyword"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    keyword = KeywordService.get_keyword(keyword_id)
    if not keyword:
        messages.error(request, 'Keyword tidak ditemukan.')
        return redirect('scanner:keywords')

    if request.method == 'POST':
        form = KeywordForm(request.POST, instance=keyword)
        if form.is_valid():
            try:
                old_keyword = keyword.keyword
                keyword = KeywordService.update_keyword(
                    keyword_id=keyword_id,
                    keyword=form.cleaned_data.get('keyword'),
                    category=form.cleaned_data.get('category'),
                    is_active=form.cleaned_data.get('is_active')
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action='UPDATE_KEYWORD',
                    details=f'Updated keyword: {old_keyword} -> {keyword.keyword} ({keyword.category})'
                )
                messages.success(request, f'Keyword "{keyword.keyword}" berhasil diperbarui.')
                return redirect('scanner:keywords')
            except Exception as e:
                logger.error(f"Error updating keyword: {e}", exc_info=True)
                messages.error(request, f'Error: {str(e)}')
    else:
        form = KeywordForm(instance=keyword)

    context = {'form': form, 'keyword': keyword, 'title': 'Edit Keyword'}
    return render(request, 'scanner/keyword_form.html', context)

@login_required
def keyword_delete_view(request, keyword_id):
    """View untuk menghapus keyword"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    keyword = KeywordService.get_keyword(keyword_id)
    if not keyword:
        messages.error(request, 'Keyword tidak ditemukan.')
        return redirect('scanner:keywords')

    if request.method == 'POST':
        try:
            keyword_name = keyword.keyword
            ActivityLog.objects.create(
                user=request.user,
                action='DELETE_KEYWORD',
                details=f'Deleted keyword: {keyword_name} ({keyword.category})'
            )
            KeywordService.delete_keyword(keyword_id)
            messages.success(request, f'Keyword "{keyword_name}" berhasil dihapus.')
            return redirect('scanner:keywords')
        except Exception as e:
            logger.error(f"Error deleting keyword: {e}", exc_info=True)
            messages.error(request, f'Error: {str(e)}')

    context = {'keyword': keyword}
    return render(request, 'scanner/keyword_delete.html', context)

@login_required
def keyword_toggle_view(request, keyword_id):
    """View untuk toggle status aktif/nonaktif keyword"""
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    try:
        keyword = KeywordService.toggle_keyword(keyword_id)
        status_text = "activated" if keyword.is_active else "deactivated"
        ActivityLog.objects.create(
            user=request.user,
            action='TOGGLE_KEYWORD',
            details=f'{status_text.capitalize()} keyword: {keyword.keyword} ({keyword.category})'
        )
        status_message = "diaktifkan" if keyword.is_active else "dinonaktifkan"
        messages.success(request, f'Keyword "{keyword.keyword}" berhasil {status_message}.')
    except ResourceNotFound:
        messages.error(request, 'Keyword tidak ditemukan.')
    except Exception as e:
        logger.error(f"Error toggling keyword: {e}", exc_info=True)
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('scanner:keywords')

@login_required
def get_scan_progress(request, scan_id):
    """API endpoint untuk mengambil progres scan dari cache"""
    progress_data = ScanService.get_scan_progress(scan_id)
    return JsonResponse(progress_data)

@login_required
def add_to_dashboard_view(request, scan_pk):
    """View untuk menambahkan hasil scan ke dashboard"""
    from .services import DashboardService
    
    scan = get_object_or_404(ScanHistory, pk=scan_pk, user=request.user)
    
    if scan.status != 'COMPLETED':
        messages.error(request, 'Scan belum selesai. Tidak dapat menambahkan ke dashboard.')
        return redirect('scanner:scan_detail', scan_pk=scan_pk)
    
    try:
        if not scan.scan_results_json:
            messages.error(request, 'Hasil scan tidak tersedia.')
            return redirect('scanner:scan_detail', scan_pk=scan_pk)
        
        results = json.loads(scan.scan_results_json)
        summary = DashboardService.update_dashboard_from_scan_results(scan.domain, results)
        
        ActivityLog.objects.create(
            user=request.user,
            action='ADD_TO_DASHBOARD',
            details=f'Added scan results for {scan.domain} to dashboard'
        )
        
        messages.success(request, f'Hasil scan untuk {scan.domain} berhasil ditambahkan ke dashboard.')
    except Exception as e:
        logger.error(f"Error adding to dashboard: {e}", exc_info=True)
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('scanner:scan_detail', scan_pk=scan_pk)

@login_required
def add_to_dataset_view(request, scan_pk):
    """View untuk menambahkan hasil scan ke dataset (admin only)"""
    from .services import DatasetService
    from .exceptions import PermissionDenied
    
    if not request.user.is_admin:
        messages.error(request, 'Hanya admin yang dapat menambahkan data ke dataset.')
        return redirect('scanner:scan_detail', scan_pk=scan_pk)
    
    scan = get_object_or_404(ScanHistory, pk=scan_pk)
    
    if request.method == 'POST':
        url = request.POST.get('url')
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        label_status = request.POST.get('label_status', 'malicious')
        
        if not url:
            messages.error(request, 'URL diperlukan.')
            return redirect('scanner:scan_detail', scan_pk=scan_pk)
        
        try:
            success = DatasetService.add_to_dataset(url, title, description, label_status, request.user)
            
            if success:
                ActivityLog.objects.create(
                    user=request.user,
                    action='ADD_TO_DATASET',
                    details=f'Added URL to dataset: {url} ({label_status})'
                )
                messages.success(request, f'URL "{url}" berhasil ditambahkan ke dataset.')
            else:
                messages.warning(request, f'URL "{url}" mungkin sudah ada di dataset.')
        except PermissionDenied as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error adding to dataset: {e}", exc_info=True)
            error_msg = str(e)
            if 'ScannerException' in error_msg:
                error_msg = error_msg.replace('ScannerException: ', '').replace('ScannerException(', '').replace(')', '')
            elif not error_msg:
                error_msg = 'Terjadi kesalahan saat menambahkan data ke dataset.'
            messages.error(request, f'Error: {error_msg}')
    
    return redirect('scanner:scan_detail', scan_pk=scan_pk)

@login_required
def item_analysis_view(request, scan_pk, item_index):
    """View untuk menampilkan analisis mendalam dari item tertentu"""
    from .models import ScanResultItem
    
    scan = get_object_or_404(ScanHistory, pk=scan_pk, user=request.user)
    
    item_index_int = int(item_index)
    item = None
    item_category = {}
    
    # Prioritas: Ambil dari model terstruktur (ScanResultItem) jika ada
    has_structured_data = ScanResultItem.objects.filter(scan_history=scan).exists()
    
    # Jika tidak ada structured data tapi ada JSON, coba backfill (lazy backfill)
    if not has_structured_data and scan.scan_results_json and scan.status == 'COMPLETED':
        try:
            from .services.scan_result_storage_service import ScanResultStorageService
            backfill_stats = ScanResultStorageService.backfill_scan_from_json(scan)
            if backfill_stats['items_saved'] > 0:
                has_structured_data = True
        except Exception as e:
            logger.warning(f"Failed to auto-backfill scan {scan.scan_id}: {e}", exc_info=True)
    
    if has_structured_data:
        # Ambil dari model terstruktur
        try:
            result_items = list(ScanResultItem.objects.filter(scan_history=scan).order_by('-discovered_at', '-risk_score'))
            
            if item_index_int < 0 or item_index_int >= len(result_items):
                messages.error(request, 'Item tidak ditemukan.')
                return redirect('scanner:scan_detail', scan_pk=scan_pk)
            
            db_item = result_items[item_index_int]
            
            # Convert ScanResultItem ke format yang diharapkan template
            item = {
                'url': db_item.url,
                'title': db_item.title or 'No Title',
                'snippet': db_item.description or '',
                'description': db_item.description or '',
                'label': db_item.label,
                'category_code': db_item.category_code or '0',
                'category_name': db_item.category_name or db_item.label,
                'verification_status': db_item.verification_status,
                'is_live': db_item.is_live,
                'is_cache_only': db_item.is_cache_only,
                'keywords_found': db_item.keywords_found or [],
                'confidence': db_item.confidence_score,
                'risk_score': db_item.risk_score,
                'source': db_item.source,
                'js_analysis': db_item.js_analysis or {},
                'verification': {
                    'is_live': db_item.is_live,
                    'is_cache_only': db_item.is_cache_only,
                    'verification_status': db_item.verification_status,
                }
            }
            
            item_category = {
                'category_code': db_item.category_code or '0',
                'category_name': db_item.category_name or db_item.label,
            }
            
            # Deep analysis bisa dari js_analysis atau perlu diambil dari JSON
            deep_analysis = db_item.js_analysis or {}
            verification = item['verification']
            js_analysis = db_item.js_analysis or {}
            
            # Coba ambil deep_analysis dari JSON jika ada
            if scan.scan_results_json:
                try:
                    json_results = json.loads(scan.scan_results_json)
                    # Cari item yang sama di JSON untuk deep_analysis
                    for cat_code, category in json_results.get('categories', {}).items():
                        for json_item in category.get('items', []):
                            if json_item.get('url') == db_item.url:
                                if json_item.get('deep_analysis'):
                                    deep_analysis = json_item.get('deep_analysis', {})
                                break
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error loading structured item data: {e}", exc_info=True)
            has_structured_data = False
    
    # Fallback: Ambil dari JSON jika model belum ada (backward compatibility)
    if not has_structured_data:
        if not scan.scan_results_json:
            messages.error(request, 'Hasil scan tidak tersedia.')
            return redirect('scanner:scan_detail', scan_pk=scan_pk)
        
        try:
            results = json.loads(scan.scan_results_json)
            
            all_items = []
            category_map = {}
            current_index = 0
            
            for cat_code, category in results.get('categories', {}).items():
                for json_item in category.get('items', []):
                    all_items.append(json_item)
                    category_map[current_index] = {
                        'category_code': cat_code,
                        'category_name': category.get('name', 'Unknown'),
                    }
                    current_index += 1
            
            if item_index_int < 0 or item_index_int >= len(all_items):
                messages.error(request, 'Item tidak ditemukan.')
                return redirect('scanner:scan_detail', scan_pk=scan_pk)
            
            item = all_items[item_index_int]
            item_category = category_map.get(item_index_int, {})
            
            deep_analysis = item.get('deep_analysis', {})
            verification = item.get('verification', {})
            js_analysis = verification.get('js_analysis', {}) if isinstance(verification, dict) else item.get('js_analysis', {})
            
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing scan results: {e}", exc_info=True)
            messages.error(request, 'Error memparse hasil scan.')
            return redirect('scanner:scan_detail', scan_pk=scan_pk)
    
    context = {
        'scan': scan,
        'item': item,
        'item_index': item_index_int,
        'item_category': item_category,
        'deep_analysis': deep_analysis,
        'verification': verification,
        'js_analysis': js_analysis,
    }
    
    return render(request, 'scanner/item_analysis.html', context)


class CustomLoginView(DjangoLoginView):
    """Custom login view dengan partnership data"""
    template_name = 'scanner/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tambahkan partnership dan sponsorship
        from .models import Partnership
        partnerships = Partnership.objects.filter(is_active=True).order_by('display_order', 'name')
        context['partnerships'] = partnerships
        return context

def custom_login_view(request):
    """Wrapper untuk custom login view"""
    view = CustomLoginView.as_view()
    return view(request)

@login_required
def export_scan_history_pdf(request):
    """
    View untuk export semua scan history ke PDF sebagai bahan pelaporan penemuan.
    Menggunakan data dari cache dan database (sama seperti UI history).
    """
    try:
        # Gunakan ScanService untuk mendapatkan data yang sama dengan UI
        # Ini menggabungkan data dari cache dan database
        user_scans = ScanService.get_user_scans(request.user, limit=100)
    except Exception as e:
        logger.error(f"Error getting user scans for PDF export: {e}", exc_info=True)
        messages.error(request, f'Error: Gagal mengambil data scan history. {str(e)}')
        return redirect('scanner:scanner_page')
    
    # Filter hanya scan yang completed dan convert ke list untuk iterasi
    completed_scans = []
    for scan_id, scan_data in user_scans.items():
        if scan_data.get('status') == 'completed' and scan_data.get('results'):
            completed_scans.append({
                'scan_id': scan_id,
                'scan_pk': scan_data.get('scan_pk'),
                'domain': scan_data.get('domain'),
                'start_time': scan_data.get('start_time'),
                'status': scan_data.get('status'),
                'results': scan_data.get('results'),
                'scan_type': scan_data.get('scan_type', 'N/A'),
                'ran_with_verification': scan_data.get('ran_with_verification', True),
            })
    
    # Jika tidak ada scan data dari service, coba ambil dari database langsung
    if not completed_scans:
        db_scans = ScanHistory.objects.filter(
            user=request.user,
            status='COMPLETED'
        ).order_by('-start_time')[:100]
        
        for scan in db_scans:
            results = None
            if scan.scan_results_json:
                try:
                    results = json.loads(scan.scan_results_json)
                    from .utils.normalizers import normalize_scan_results
                    # Normalisasi data dari database juga
                    results = normalize_scan_results(results)
                    
                    # Log untuk debugging
                    logger.debug(f"PDF Export - Loaded from DB: scan {scan.scan_id}, has categories: {bool(results.get('categories'))}")
                    if results.get('categories'):
                        for cat_code, cat_data in results['categories'].items():
                            if isinstance(cat_data, dict) and cat_data.get('items'):
                                items = cat_data['items']
                                if items and len(items) > 0:
                                    first_item = items[0]
                                    logger.debug(f"PDF Export - First item from DB: url={first_item.get('url')}, title={first_item.get('title')}")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"PDF Export - Error parsing scan results from DB: {e}", exc_info=True)
                    results = None
            
            # Untuk premium user: coba ambil dari permanent storage jika results kosong
            if not results and hasattr(request.user, 'is_premium') and request.user.is_premium:
                try:
                    from .services import PermanentStorageService
                    permanent_results = PermanentStorageService.get_scan_result(scan)
                    if permanent_results:
                        results = permanent_results
                        from .utils.normalizers import normalize_scan_results
                        results = normalize_scan_results(results)
                        logger.info(f"PDF Export - Retrieved from permanent storage for scan {scan.scan_id}")
                except Exception as e:
                    logger.warning(f"PDF Export - Error retrieving permanent storage for scan {scan.scan_id}: {e}")
            
            if results:
                completed_scans.append({
                    'scan_id': scan.scan_id,
                    'scan_pk': scan.pk,
                    'domain': scan.domain,
                    'start_time': scan.start_time.isoformat() if scan.start_time else None,
                    'status': 'completed',
                    'results': results,
                    'scan_type': scan.scan_type,
                    'ran_with_verification': scan.ran_with_verification,
                    'end_time': scan.end_time,
                })
    
    if not completed_scans:
        messages.warning(request, 'Tidak ada scan history yang dapat diekspor.')
        return redirect('scanner:scanner_page')
    
    # Create PDF buffer
    buffer = None
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    except Exception as e:
        logger.error(f"Error creating PDF buffer: {e}", exc_info=True)
        messages.error(request, f'Error: Gagal membuat dokumen PDF. {str(e)}')
        return redirect('scanner:scanner_page')
    
    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 10

    # LETTERHEAD SECTION
    # Organization Header
    org_name_style = ParagraphStyle(
        'OrgName',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    org_info_style = ParagraphStyle(
        'OrgInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        spaceAfter=2
    )

    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#e74c3c'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Organization Information (Kop Surat)
    elements.append(Paragraph("KEMENTERIAN KOMUNIKASI DAN INFORMATIKA", org_name_style))
    elements.append(Paragraph("REPUBLIK INDONESIA", org_name_style))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("DIREKTORAT JENDERAL APLIKASI INFORMATIKA", org_info_style))
    elements.append(Paragraph("BADAN PENGAWASAN KEAMANAN DAN SIBER", org_info_style))
    elements.append(Paragraph("Jl. Medan Merdeka Barat No. 9, Jakarta Pusat 10110", org_info_style))
    elements.append(Paragraph("Telp: (021) 3451234 | Email: info@bssn.go.id | Website: www.bssn.go.id", org_info_style))
    elements.append(Spacer(1, 0.3*inch))

    # Decorative line
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[2]))
    elements.append(Spacer(1, 0.2*inch))

    # Report Title
    elements.append(Paragraph("LAPORAN HASIL SCAN DOMAIN", report_title_style))
    elements.append(Paragraph("SISTEM DETEKSI MALICIOUS DOMAIN", org_info_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Meta information
    user_full_name = request.user.get_full_name() or request.user.username or 'N/A'
    user_email = request.user.email or 'N/A'
    export_date = timezone.now().strftime('%d %B %Y, %H:%M:%S')
    
    meta_data = [
        ['Dibuat oleh:', sanitize_string_for_pdf(user_full_name)],
        ['Email:', sanitize_string_for_pdf(user_email)],
        ['Tanggal Export:', sanitize_string_for_pdf(export_date)],
        ['Total Scan:', str(len(completed_scans))],
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Process each scan
    for idx, scan_data in enumerate(completed_scans, 1):
        try:
            # Scan Header
            domain_display = sanitize_string_for_pdf(scan_data.get('domain', 'N/A'))
            scan_title = f"Scan #{idx}: {domain_display}"
            elements.append(Paragraph(scan_title, heading_style))
            
            # Parse start_time untuk display
            start_time_display = 'N/A'
            try:
                if scan_data.get('start_time'):
                    if isinstance(scan_data['start_time'], str):
                        from datetime import datetime
                        start_time_obj = datetime.fromisoformat(scan_data['start_time'].replace('Z', '+00:00'))
                    else:
                        start_time_obj = scan_data['start_time']
                    start_time_display = start_time_obj.strftime('%d %B %Y, %H:%M:%S')
            except Exception:
                start_time_display = 'N/A'
            
            # Scan Information Table
            scan_duration = 'N/A'
            try:
                if scan_data.get('end_time') and scan_data.get('start_time'):
                    if isinstance(scan_data['start_time'], str):
                        from datetime import datetime
                        start_time_obj = datetime.fromisoformat(scan_data['start_time'].replace('Z', '+00:00'))
                    else:
                        start_time_obj = scan_data['start_time']
                    duration = scan_data['end_time'] - start_time_obj
                    total_seconds = int(duration.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    if hours > 0:
                        scan_duration = f"{hours} jam {minutes} menit {seconds} detik"
                    elif minutes > 0:
                        scan_duration = f"{minutes} menit {seconds} detik"
                    else:
                        scan_duration = f"{seconds} detik"
            except Exception:
                scan_duration = 'N/A'
            
            scan_info = [
                ['Scan ID:', sanitize_string_for_pdf(scan_data.get('scan_id', 'N/A'))],
                ['Domain:', sanitize_string_for_pdf(scan_data.get('domain', 'N/A'))],
                ['Tipe Scan:', sanitize_string_for_pdf(scan_data.get('scan_type', 'N/A'))],
                ['Tanggal Scan:', sanitize_string_for_pdf(start_time_display)],
                ['Durasi:', sanitize_string_for_pdf(scan_duration)],
                ['Verifikasi Real-Time:', 'Ya' if scan_data.get('ran_with_verification', True) else 'Tidak'],
            ]
            
            scan_info_table = Table(scan_info, colWidths=[2*inch, 4*inch])
            scan_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(scan_info_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Parse scan results - data sudah dari cache/service, langsung pakai
            results = scan_data.get('results')
            if results:
                try:
                    # Debug: log raw data untuk troubleshooting
                    logger.debug(f"PDF Export - Using data from cache/service for scan {scan_data.get('scan_id')}")
                    logger.debug(f"  - Has categories: {bool(results.get('categories'))}")
                    logger.debug(f"  - Has subdomain_results: {bool(results.get('subdomain_results'))}")
                    if results.get('subdomain_results'):
                        subdomains_raw = results['subdomain_results'].get('subdomains', [])
                        logger.debug(f"  - Subdomains count: {len(subdomains_raw)}")
                        if subdomains_raw and len(subdomains_raw) > 0:
                            first_sub_raw = subdomains_raw[0]
                            logger.debug(f"  - First subdomain raw: {first_sub_raw}")
                    if results.get('categories'):
                        for cat_code, cat_data in results['categories'].items():
                            items_count = len(cat_data.get('items', [])) if isinstance(cat_data, dict) else 0
                            logger.debug(f"  - Category {cat_code}: {items_count} items")
                            if items_count > 0 and isinstance(cat_data, dict):
                                first_item_raw = cat_data['items'][0] if cat_data.get('items') else {}
                                logger.debug(f"  - First item raw: keys={list(first_item_raw.keys()) if isinstance(first_item_raw, dict) else 'N/A'}, url={first_item_raw.get('url') if isinstance(first_item_raw, dict) else 'N/A'}, title={first_item_raw.get('title') if isinstance(first_item_raw, dict) else 'N/A'}")
                    
                    # Final Conclusion
                    if results.get('final_conclusion'):
                        fc = results['final_conclusion']
                        if not isinstance(fc, dict):
                            fc = {}
                        
                        # Get status - handle None
                        status_val = fc.get('status')
                        if status_val is None or status_val == '':
                            status_val = 'N/A'
                        else:
                            status_val = str(status_val)
                        
                        # Get message - handle None
                        message_val = fc.get('message')
                        if message_val is None or message_val == '':
                            message_val = 'N/A'
                        else:
                            message_val = str(message_val)
                        
                        # Get risk_score - handle None
                        risk_score_val = fc.get('risk_score')
                        if risk_score_val is None:
                            risk_score_val = 0
                        else:
                            try:
                                risk_score_val = int(risk_score_val)
                            except (ValueError, TypeError):
                                risk_score_val = 0
                        
                        conclusion_text = f"<b>Status:</b> {status_val}<br/>" \
                                        f"<b>Pesan:</b> {message_val}<br/>" \
                                        f"<b>Risk Score:</b> {risk_score_val}/100"
                        
                        # Get stats - handle None
                        stats = fc.get('stats', {})
                        if isinstance(stats, dict):
                            live_malicious = stats.get('live_malicious')
                            cache_only = stats.get('cache_only')
                            clean = stats.get('clean')
                            
                            # Handle None values
                            live_malicious = live_malicious if live_malicious is not None else 0
                            cache_only = cache_only if cache_only is not None else 0
                            clean = clean if clean is not None else 0
                            
                            conclusion_text += f"<br/><b>Statistik:</b> Live: {live_malicious}, " \
                                            f"Cache Only: {cache_only}, " \
                                            f"Clean: {clean}"
                        
                        elements.append(Paragraph("<b>Kesimpulan Scan:</b>", normal_style))
                        elements.append(Paragraph(conclusion_text, normal_style))
                        elements.append(Spacer(1, 0.2*inch))
                    
                    # Cek apakah ada formatted_items (format CSV-like) - prioritas utama
                    formatted_items = results.get('formatted_items', [])
                    formatted_subdomains = results.get('formatted_subdomains', [])
                    
                    # Jika ada formatted_items, gunakan format CSV-like
                    if formatted_items and len(formatted_items) > 0:
                        elements.append(Paragraph("<b>Konten Malicious Ditemukan:</b>", normal_style))
                        
                        # Group items by label_status
                        items_by_label = {}
                        for item in formatted_items:
                            if isinstance(item, dict):
                                label = item.get('label_status', 'unknown')
                                if label not in items_by_label:
                                    items_by_label[label] = []
                                items_by_label[label].append(item)
                        
                        # Tampilkan items per label_status
                        for label_status, items_list in items_by_label.items():
                            label_display = label_status.replace('_', ' ').title()
                            elements.append(Paragraph(f"<b>{label_display}</b> ({len(items_list)} item):", normal_style))
                            
                            # Create table for items in this label
                            item_data = [['No', 'URL', 'Title', 'Description', 'Label Status']]
                            
                            item_count = 0
                            for item in items_list[:50]:  # Limit to 50 items per label
                                if not isinstance(item, dict):
                                    continue
                                
                                # Get values dari formatted_item (sudah terformat dengan benar)
                                url = item.get('url', '')
                                title = item.get('title', 'No Title')
                                description = item.get('description', '')
                                label = item.get('label_status', 'unknown')
                                
                                # Sanitize untuk PDF
                                url = sanitize_string_for_pdf(url) if url else 'N/A'
                                title = sanitize_string_for_pdf(title) if title else 'No Title'
                                description = sanitize_string_for_pdf(description) if description else ''
                                label = sanitize_string_for_pdf(label) if label else 'unknown'
                                
                                # Truncate untuk display
                                if url != 'N/A' and isinstance(url, str) and len(url) > 50:
                                    url_display = url[:50] + '...'
                                else:
                                    url_display = url
                                
                                if title != 'No Title' and isinstance(title, str) and len(title) > 60:
                                    title_display = title[:60] + '...'
                                else:
                                    title_display = title
                                
                                if description and isinstance(description, str) and len(description) > 80:
                                    description_display = description[:80] + '...'
                                else:
                                    description_display = description if description else 'N/A'
                                
                                item_count += 1
                                item_data.append([
                                    str(item_count),
                                    sanitize_string_for_pdf(url_display),
                                    sanitize_string_for_pdf(title_display),
                                    sanitize_string_for_pdf(description_display),
                                    sanitize_string_for_pdf(label)
                                ])
                            
                            # Create table only if we have items (more than just header)
                            if len(item_data) > 1:
                                items_table = Table(item_data, colWidths=[0.4*inch, 2.5*inch, 2.0*inch, 2.0*inch, 1.1*inch])
                                items_table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                                ]))
                                elements.append(items_table)
                                elements.append(Spacer(1, 0.2*inch))
                            else:
                                elements.append(Paragraph(f"<i>Tidak ada item valid dalam kategori {label_display}.</i>", normal_style))
                                elements.append(Spacer(1, 0.1*inch))
                    
                    # Fallback: jika tidak ada formatted_items, gunakan categories (format lama)
                    elif results.get('categories', {}):
                        categories = results.get('categories', {})
                        if categories and isinstance(categories, dict):
                            elements.append(Paragraph("<b>Kategori Terdeteksi:</b>", normal_style))
                            
                            for cat_code, category in categories.items():
                                if not isinstance(category, dict):
                                    continue
                                
                                # Get category name - handle None
                                cat_name = category.get('name')
                                if cat_name is None or cat_name == '':
                                    cat_name = 'Unknown'
                                else:
                                    cat_name = str(cat_name)
                                
                                items = category.get('items', [])
                                if not isinstance(items, list):
                                    items = []
                                
                                if not items:
                                    continue
                                
                                elements.append(Paragraph(f"<b>{cat_name}</b> ({len(items)} item):", normal_style))
                                
                                # Create table for items in this category
                                item_data = [['No', 'URL', 'Title', 'Status']]
                                
                                item_count = 0
                                for item in items[:50]:  # Limit to 50 items per category
                                    # Ensure item is a dict
                                    if not isinstance(item, dict):
                                        logger.warning(f"Item is not a dict: {type(item)}")
                                        continue
                                    
                                    # Get URL - try multiple possible keys and methods
                                    url = item.get('url') or item.get('link') or ''
                                    if not url:
                                        deep_analysis = item.get('deep_analysis', {})
                                        if isinstance(deep_analysis, dict):
                                            url = deep_analysis.get('url') or ''
                                    
                                    # Get title - try multiple possible keys
                                    title_raw = item.get('title') or item.get('headline') or ''
                                    if not title_raw:
                                        snippet = item.get('snippet')
                                        if snippet and isinstance(snippet, str) and snippet.strip():
                                            title_raw = snippet[:100]
                                    if not title_raw:
                                        deep_analysis = item.get('deep_analysis', {})
                                        if isinstance(deep_analysis, dict):
                                            title_raw = deep_analysis.get('title') or ''
                                    if not title_raw:
                                        title_raw = 'No Title'
                                    
                                    # Sanitize dan handle None values
                                    url = sanitize_string_for_pdf(url) if url else 'N/A'
                                    title_raw = sanitize_string_for_pdf(title_raw) if title_raw else 'No Title'
                                    
                                    # Truncate title for display
                                    if title_raw != 'No Title' and isinstance(title_raw, str) and len(title_raw) > 60:
                                        title = title_raw[:60] + '...'
                                    else:
                                        title = title_raw
                                    
                                    # Get verification status
                                    verification = item.get('verification', {})
                                    status = 'N/A'
                                    if isinstance(verification, dict):
                                        v_status = verification.get('verification_status')
                                        if v_status:
                                            v_status = str(v_status).strip().lower()
                                            if v_status == 'live_malicious':
                                                status = 'LIVE MALICIOUS'
                                            elif v_status == 'cache_only':
                                                status = 'CACHE ONLY'
                                            elif v_status == 'clean':
                                                status = 'CLEAN'
                                    
                                    # Truncate URL for display
                                    if url != 'N/A' and isinstance(url, str) and len(url) > 50:
                                        url_display = url[:50] + '...'
                                    else:
                                        url_display = url
                                    
                                    item_count += 1
                                    item_data.append([
                                        str(item_count),
                                        sanitize_string_for_pdf(url_display),
                                        sanitize_string_for_pdf(title),
                                        sanitize_string_for_pdf(status)
                                    ])
                        
                        # Create table only if we have items (more than just header)
                        if len(item_data) > 1:
                            # Improved column widths for better readability
                            items_table = Table(item_data, colWidths=[0.4*inch, 3.0*inch, 2.8*inch, 1.0*inch])
                            items_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 8),
                                ('FONTSIZE', (0, 1), (-1, -1), 7),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                ('TOPPADDING', (0, 0), (-1, -1), 8),
                                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                            ]))
                            elements.append(items_table)
                            elements.append(Spacer(1, 0.2*inch))
                        else:
                            # If no valid items, show message
                            elements.append(Paragraph(f"<i>Tidak ada item valid dalam kategori ini.</i>", normal_style))
                            elements.append(Spacer(1, 0.1*inch))
                    
                    # Subdomain Results
                    # Prioritas: gunakan formatted_subdomains jika ada
                    if formatted_subdomains and len(formatted_subdomains) > 0:
                        subdomains = formatted_subdomains
                        elements.append(Paragraph(f"<b>Subdomain Ditemukan:</b> {len(subdomains)}", normal_style))
                        
                        subdomain_data = [['No', 'Subdomain', 'IP Address', 'Status']]
                        for i, sub in enumerate(subdomains[:50], 1):  # Limit to 50 subdomains
                            if not isinstance(sub, dict):
                                continue
                            
                            # Get values dari formatted_subdomain (sudah terformat dengan benar)
                            subdomain_val = sub.get('subdomain', '')
                            ip_val = sub.get('ip', '')
                            status_val = sub.get('status', 'unknown')
                            
                            # Sanitize untuk PDF
                            subdomain_val = sanitize_string_for_pdf(subdomain_val) if subdomain_val else 'N/A'
                            ip_val = sanitize_string_for_pdf(ip_val) if ip_val else 'N/A'
                            status_val = sanitize_string_for_pdf(status_val) if status_val else 'unknown'
                            
                            subdomain_data.append([
                                str(i),
                                sanitize_string_for_pdf(subdomain_val),
                                sanitize_string_for_pdf(ip_val),
                                sanitize_string_for_pdf(status_val)
                            ])
                        
                        # Create table only if we have subdomains (more than just header)
                        if len(subdomain_data) > 1:
                            subdomain_table = Table(subdomain_data, colWidths=[0.4*inch, 2.5*inch, 2.0*inch, 1.1*inch])
                            subdomain_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 8),
                                ('FONTSIZE', (0, 1), (-1, -1), 7),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                ('TOPPADDING', (0, 0), (-1, -1), 8),
                                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                            ]))
                            elements.append(subdomain_table)
                            elements.append(Spacer(1, 0.2*inch))
                        else:
                            elements.append(Paragraph("<i>Tidak ada subdomain yang ditemukan.</i>", normal_style))
                            elements.append(Spacer(1, 0.1*inch))
                    # Fallback: gunakan subdomain_results (format lama)
                    else:
                        subdomain_results = results.get('subdomain_results', {})
                        if subdomain_results and isinstance(subdomain_results, dict):
                            subdomains = subdomain_results.get('subdomains', [])
                            if subdomains and isinstance(subdomains, list):
                                elements.append(Paragraph(f"<b>Subdomain Ditemukan:</b> {len(subdomains)}", normal_style))
                                
                                subdomain_data = [['No', 'Subdomain', 'IP Address', 'Status']]
                                for i, sub in enumerate(subdomains[:50], 1):  # Limit to 50 subdomains
                                    if not isinstance(sub, dict):
                                        logger.warning(f"Subdomain item #{i} in PDF is not a dict: {type(sub)}")
                                        continue
                                    
                                    # Get subdomain - handle None
                                    subdomain_val = sub.get('subdomain') or sub.get('name') or ''
                                    
                                    # Get IP - handle None
                                    ip_val = sub.get('ip') or ''
                                    
                                    # Get status - handle None
                                    status_value = sub.get('status')
                                    if status_value is None:
                                        status_value = 'INACTIVE'
                                    elif isinstance(status_value, str):
                                        status_value = status_value.strip().upper()
                                    else:
                                        status_value = str(status_value).strip().upper() if status_value else 'INACTIVE'
                                    
                                    # Sanitize untuk PDF
                                    subdomain_val = sanitize_string_for_pdf(subdomain_val) if subdomain_val else 'N/A'
                                    ip_val = sanitize_string_for_pdf(ip_val) if ip_val else 'N/A'
                                    status_value = sanitize_string_for_pdf(status_value) if status_value else 'INACTIVE'
                                    
                                    subdomain_data.append([
                                        str(i),
                                        sanitize_string_for_pdf(subdomain_val),
                                        sanitize_string_for_pdf(ip_val),
                                        sanitize_string_for_pdf(status_value)
                                    ])
                                
                                # Create table only if we have subdomains (more than just header)
                                if len(subdomain_data) > 1:
                                    subdomain_table = Table(subdomain_data, colWidths=[0.4*inch, 2.5*inch, 2.0*inch, 1.1*inch])
                                    subdomain_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                                    ]))
                                    elements.append(subdomain_table)
                                    elements.append(Spacer(1, 0.2*inch))
                                else:
                                    elements.append(Paragraph("<i>Tidak ada subdomain yang ditemukan.</i>", normal_style))
                                    elements.append(Spacer(1, 0.1*inch))
                    
                except Exception as e:
                    logger.error(f"Error processing scan results: {e}", exc_info=True)
                    error_msg = sanitize_string_for_pdf(f"Error: Tidak dapat memproses hasil scan untuk scan #{idx}")
                    elements.append(Paragraph(f"<b>{error_msg}</b>", normal_style))
            else:
                elements.append(Paragraph("Tidak ada hasil scan tersedia.", normal_style))
        
        except Exception as e:
            logger.error(f"Error processing scan #{idx}: {e}", exc_info=True)
            try:
                error_msg = sanitize_string_for_pdf(f"Error memproses scan #{idx}: {str(e)[:100]}")
                elements.append(Paragraph(f"<b>Error:</b> {error_msg}", normal_style))
            except Exception:
                # Jika bahkan error message tidak bisa dibuat, skip scan ini
                logger.error(f"Critical error in PDF export for scan #{idx}", exc_info=True)
        
        # Page break between scans (except last)
        if idx < len(completed_scans):
            elements.append(PageBreak())
    
    # Build PDF dengan error handling yang komprehensif
    try:
        doc.build(elements)
    except Exception as e:
        logger.error(f"Error building PDF document: {e}", exc_info=True)
        if buffer:
            try:
                buffer.close()
            except:
                pass
        messages.error(request, f'Error: Gagal membuat dokumen PDF. {str(e)}')
        return redirect('scanner:scanner_page')
    
    # Get PDF value from buffer dengan error handling
    try:
        buffer.seek(0)
        pdf_value = buffer.getvalue()
        buffer.close()
    except Exception as e:
        logger.error(f"Error reading PDF buffer: {e}", exc_info=True)
        if buffer:
            try:
                buffer.close()
            except:
                pass
        messages.error(request, f'Error: Gagal membaca dokumen PDF. {str(e)}')
        return redirect('scanner:scanner_page')
    
    # Create HTTP response dengan error handling
    try:
        response = HttpResponse(content_type='application/pdf')
        filename = f"scan_history_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf_value)
    except Exception as e:
        logger.error(f"Error creating HTTP response for PDF: {e}", exc_info=True)
        messages.error(request, f'Error: Gagal membuat response PDF. {str(e)}')
        return redirect('scanner:scanner_page')
    
    # Log activity dengan error handling
    try:
        ActivityLog.objects.create(
            user=request.user,
            action='EXPORT_PDF',
            details=f'Exported {len(completed_scans)} scan history to PDF'
        )
    except Exception as e:
        logger.warning(f"Error logging PDF export activity: {e}", exc_info=True)
        # Jangan gagal export jika hanya logging yang error
    
    return response


@login_required
def feedback_view(request):
    """
    Halaman feedback untuk user client/staff dan admin.
    - Client/Staff: Dapat melihat semua feedback dan submit feedback baru
    - Admin: Dapat melihat semua feedback, submit feedback, dan membalas feedback
    """
    from scanner.models import Feedback
    from django.utils import timezone
    
    # Get all feedbacks
    feedbacks = Feedback.objects.all().select_related('user', 'replied_by')
    
    # Handle POST requests
    if request.method == 'POST':
        if 'submit_feedback' in request.POST:
            # Submit feedback baru
            message = request.POST.get('message', '').strip()
            if not message:
                messages.error(request, 'Pesan feedback tidak boleh kosong.')
            else:
                feedback = Feedback.objects.create(
                    user=request.user,
                    message=message
                )
                messages.success(request, 'Feedback berhasil dikirim!')
                return redirect('scanner:feedback')
        
        elif 'reply_feedback' in request.POST and request.user.is_admin:
            # Admin membalas feedback
            feedback_id = request.POST.get('feedback_id')
            reply_message = request.POST.get('reply', '').strip()
            
            if not reply_message:
                messages.error(request, 'Balasan tidak boleh kosong.')
            else:
                try:
                    feedback = Feedback.objects.get(id=feedback_id)
                    feedback.reply = reply_message
                    feedback.replied_by = request.user
                    feedback.replied_at = timezone.now()
                    feedback.is_resolved = True
                    feedback.save()
                    messages.success(request, 'Balasan berhasil dikirim!')
                except Feedback.DoesNotExist:
                    messages.error(request, 'Feedback tidak ditemukan.')
            
            return redirect('scanner:feedback')
    
    # Pagination
    paginator = Paginator(feedbacks, 10)  # 10 feedback per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedbacks': page_obj,
        'is_admin': request.user.is_admin,
    }
    
    return render(request, 'scanner/feedback.html', context)


@login_required
def partnerships_view(request):
    """
    Halaman untuk admin mengelola kerjasama dan sponsorship.
    """
    from scanner.models import Partnership
    from django.core.files.storage import default_storage
    import os
    
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')
    
    partnerships = Partnership.objects.all().order_by('display_order', 'name')
    
    # Handle POST requests
    if request.method == 'POST':
        if 'add_partnership' in request.POST:
            # Tambah kerjasama baru
            name = request.POST.get('name', '').strip()
            partnership_type = request.POST.get('partnership_type', 'partnership')
            website_url = request.POST.get('website_url', '').strip()
            display_order = request.POST.get('display_order', '0')
            logo_file = request.FILES.get('logo')
            
            if not name:
                messages.error(request, 'Nama instansi tidak boleh kosong.')
            elif not logo_file:
                messages.error(request, 'Logo harus diupload.')
            else:
                try:
                    display_order_int = int(display_order)
                    partnership = Partnership.objects.create(
                        name=name,
                        partnership_type=partnership_type,
                        website_url=website_url if website_url else None,
                        display_order=display_order_int,
                        logo=logo_file,
                        created_by=request.user
                    )
                    messages.success(request, f'Kerjasama "{name}" berhasil ditambahkan!')
                except ValueError:
                    messages.error(request, 'Urutan tampilan harus berupa angka.')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:partnerships')
        
        elif 'edit_partnership' in request.POST:
            # Edit kerjasama
            partnership_id = request.POST.get('partnership_id')
            name = request.POST.get('name', '').strip()
            partnership_type = request.POST.get('partnership_type', 'partnership')
            website_url = request.POST.get('website_url', '').strip()
            display_order = request.POST.get('display_order', '0')
            logo_file = request.FILES.get('logo')
            
            if not name:
                messages.error(request, 'Nama instansi tidak boleh kosong.')
            else:
                try:
                    partnership = Partnership.objects.get(id=partnership_id)
                    partnership.name = name
                    partnership.partnership_type = partnership_type
                    partnership.website_url = website_url if website_url else None
                    partnership.display_order = int(display_order)
                    
                    if logo_file:
                        # Hapus logo lama jika ada
                        if partnership.logo:
                            try:
                                if os.path.exists(partnership.logo.path):
                                    os.remove(partnership.logo.path)
                            except:
                                pass
                        partnership.logo = logo_file
                    
                    partnership.save()
                    messages.success(request, f'Kerjasama "{name}" berhasil diupdate!')
                except Partnership.DoesNotExist:
                    messages.error(request, 'Kerjasama tidak ditemukan.')
                except ValueError:
                    messages.error(request, 'Urutan tampilan harus berupa angka.')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:partnerships')
        
        elif 'delete_partnership' in request.POST:
            # Hapus kerjasama
            partnership_id = request.POST.get('partnership_id')
            try:
                partnership = Partnership.objects.get(id=partnership_id)
                partnership_name = partnership.name
                # Hapus logo file
                if partnership.logo:
                    try:
                        if os.path.exists(partnership.logo.path):
                            os.remove(partnership.logo.path)
                    except:
                        pass
                partnership.delete()
                messages.success(request, f'Kerjasama "{partnership_name}" berhasil dihapus!')
            except Partnership.DoesNotExist:
                messages.error(request, 'Kerjasama tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            
            return redirect('scanner:partnerships')
        
        elif 'toggle_partnership' in request.POST:
            # Toggle aktif/nonaktif
            partnership_id = request.POST.get('partnership_id')
            try:
                partnership = Partnership.objects.get(id=partnership_id)
                partnership.is_active = not partnership.is_active
                partnership.save()
                status = 'diaktifkan' if partnership.is_active else 'dinonaktifkan'
                messages.success(request, f'Kerjasama "{partnership.name}" berhasil {status}!')
            except Partnership.DoesNotExist:
                messages.error(request, 'Kerjasama tidak ditemukan.')
            
            return redirect('scanner:partnerships')
    
    context = {
        'partnerships': partnerships,
    }
    
    return render(request, 'scanner/partnerships.html', context)
