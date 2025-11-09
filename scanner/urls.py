# scanner/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # Import view dari aplikasi scanner kita

app_name = 'scanner' # Namespace untuk URL aplikasi scanner

urlpatterns = [
    # URL Autentikasi
    path('login/', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='scanner:scanner_page'), name='logout'),

    # URL Aplikasi Scanner
    path('dashboard/', views.dashboard, name='dashboard'),
    path('scan/', views.scanner_view, name='scanner_page'),
    path('profile/', views.profile_view, name='profile'),

    # URL root aplikasi scanner (misal: arahkan ke halaman scan)
    path('', views.scanner_view, name='index'),

    # Separate pages for admin features
    path('config/', views.config_view, name='config'),
    path('audit/', views.audit_view, name='audit'),
    path('users/', views.users_view, name='users'),
    path('training/', views.training_view, name='training'),

    # User management URLs
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active_view, name='user_toggle_active'),
    path('users/<int:user_id>/quota/', views.user_manage_quota_view, name='user_manage_quota'),
    path('users/<int:user_id>/reset-password/', views.user_reset_password_view, name='user_reset_password'),

    # API endpoints untuk AJAX calls (opsional, untuk future enhancement)
    path('api/scan-status/<str:scan_id>/', views.get_scan_status, name='scan_status'),
    path('api/validate-result/', views.validate_scan_result, name='validate_result'),

    # Scan detail URL
    path('scan/<int:scan_pk>/details/', views.scan_detail_view, name='scan_detail'),

    # Keyword management URLs
    path('keywords/', views.keywords_view, name='keywords'),
    path('keywords/create/', views.keyword_create_view, name='keyword_create'),
    path('keywords/<int:keyword_id>/edit/', views.keyword_edit_view, name='keyword_edit'),
    path('keywords/<int:keyword_id>/delete/', views.keyword_delete_view, name='keyword_delete'),
    path('keywords/<int:keyword_id>/toggle/', views.keyword_toggle_view, name='keyword_toggle'),
    path('scan-progress/<str:scan_id>/', views.get_scan_progress, name='get_scan_progress'),
    
    # Dashboard management URLs
    path('scan/<int:scan_pk>/add-to-dashboard/', views.add_to_dashboard_view, name='add_to_dashboard'),
    
    # Dataset management URLs (admin only)
    path('scan/<int:scan_pk>/add-to-dataset/', views.add_to_dataset_view, name='add_to_dataset'),
    
    # Item analysis URLs
    path('scan/<int:scan_pk>/item/<int:item_index>/analysis/', views.item_analysis_view, name='item_analysis'),
    
    # Export PDF URLs
    path('export-history-pdf/', views.export_scan_history_pdf, name='export_history_pdf'),
    
    # Feedback URLs
    path('feedback/', views.feedback_view, name='feedback'),
    
    # Partnership/Sponsorship URLs (Admin only)
    path('partnerships/', views.partnerships_view, name='partnerships'),
]
