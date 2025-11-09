"""
URL routing untuk API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scanner.api import views
from scanner.api import auth_views

router = DefaultRouter()
router.register(r'scans', views.ScanHistoryViewSet, basename='scan')
router.register(r'keywords', views.MaliciousKeywordViewSet, basename='keyword')
router.register(r'activity-logs', views.ActivityLogViewSet, basename='activity-log')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'domain-summaries', views.DomainScanSummaryViewSet, basename='domain-summary')
router.register(r'config', views.SistemConfigViewSet, basename='config')
router.register(r'apikeys', views.ApiKeyViewSet, basename='apikey')
router.register(r'production', views.ProductionSettingsViewSet, basename='production')

urlpatterns = [
    # Public endpoints (no authentication required)
    path('health/', auth_views.health_check_view, name='api-health'),
    # Authentication endpoint
    path('auth/login/', auth_views.login_view, name='api-login'),
    # REST Framework router
    path('', include(router.urls)),
]

