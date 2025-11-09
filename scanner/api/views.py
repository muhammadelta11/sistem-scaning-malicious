"""
API views untuk aplikasi scanner menggunakan Django REST Framework.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
import json
import logging

from scanner.models import (
    ScanHistory, MaliciousKeyword, ActivityLog, DomainScanSummary, 
    SistemConfig, ApiKey, ProductionSettings
)
from scanner.services import ScanService, KeywordService, UserService
from scanner.api.serializers import (
    ScanHistorySerializer, ScanResultSerializer, MaliciousKeywordSerializer,
    ActivityLogSerializer, ScanCreateSerializer, ProgressSerializer,
    UserSerializer, DomainScanSummarySerializer, SistemConfigSerializer,
    ApiKeySerializer, ProductionSettingsSerializer, QuotaStatusSerializer,
    UserProfileSerializer
)
from scanner.exceptions import (
    DomainValidationError, ScanProcessingError, ResourceNotFound,
    PermissionDenied
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


class ScanHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola scan history.
    
    list: Daftar semua scan milik user
    retrieve: Detail scan tertentu
    create: Buat scan baru
    """
    serializer_class = ScanHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter scan history berdasarkan user."""
        return ScanHistory.objects.filter(user=self.request.user).order_by('-start_time')
    
    def create(self, request, *args, **kwargs):
        """Membuat scan baru."""
        serializer = ScanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            scan_obj = ScanService.create_scan(
                user=request.user,
                domain=serializer.validated_data['domain'],
                scan_type=serializer.validated_data['scan_type'],
                enable_verification=serializer.validated_data.get('enable_verification', True),
                show_all_results=serializer.validated_data.get('show_all_results', False)
            )
            
            response_serializer = ScanHistorySerializer(scan_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except DomainValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ScanProcessingError as e:
            error_msg = str(e)
            # Check if it's a quota error
            if 'kuota' in error_msg.lower() or 'quota' in error_msg.lower():
                return Response(
                    {'error': error_msg, 'detail': error_msg, 'quota_exceeded': True},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {'error': error_msg, 'detail': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Mendapatkan hasil scan."""
        scan = self.get_object()
        
        if scan.status != 'COMPLETED':
            return Response(
                {'error': 'Scan belum selesai'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Coba ambil dari scan_results_json terlebih dahulu
            results = None
            if scan.scan_results_json:
                try:
                    results = json.loads(scan.scan_results_json)
                    # Normalisasi hasil scan
                    from scanner.utils.normalizers import normalize_scan_results
                    results = normalize_scan_results(results)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing scan_results_json for scan {scan.scan_id}: {e}")
                    results = None
            
            # Untuk premium user: jika scan_results_json kosong atau None, coba ambil dari permanent storage
            if not results and hasattr(request.user, 'is_premium') and request.user.is_premium:
                try:
                    from scanner.services import PermanentStorageService
                    permanent_results = PermanentStorageService.get_scan_result(scan)
                    if permanent_results:
                        results = permanent_results
                        # Normalisasi hasil scan
                        from scanner.utils.normalizers import normalize_scan_results
                        results = normalize_scan_results(results)
                        logger.info(f"Retrieved scan results from permanent storage for premium user {request.user.username} (scan_id: {scan.scan_id})")
                except Exception as e:
                    logger.warning(f"Error retrieving permanent storage for scan {scan.scan_id}: {e}")
            
            # Jika masih tidak ada results, return error
            if not results:
                return Response(
                    {'error': 'Hasil scan tidak ditemukan'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ScanResultSerializer(results)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in results endpoint for scan {scan.scan_id}: {e}", exc_info=True)
            return Response(
                {'error': f'Gagal memparse hasil scan: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Mendapatkan progress scan."""
        scan = self.get_object()
        
        progress_data = ScanService.get_scan_progress(scan.scan_id)
        serializer = ProgressSerializer(progress_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_scans(self, request):
        """Daftar semua scan milik user yang sedang diproses."""
        user_scans = ScanService.get_user_scans(request.user)
        return Response(user_scans)


class MaliciousKeywordViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola malicious keywords.
    Hanya admin yang bisa mengakses.
    """
    serializer_class = MaliciousKeywordSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MaliciousKeyword.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by saat membuat keyword."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle status aktif/nonaktif keyword."""
        keyword = self.get_object()
        updated_keyword = KeywordService.toggle_keyword(keyword.id)
        serializer = self.get_serializer(updated_keyword)
        return Response(serializer.data)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet untuk melihat activity logs.
    Hanya admin yang bisa mengakses.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ActivityLog.objects.all().order_by('-timestamp')


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola users.
    Hanya admin yang bisa mengakses.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get queryset untuk users."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.all().order_by('-date_joined')
    
    def create(self, request, *args, **kwargs):
        """Membuat user baru."""
        password = request.data.get('password')
        if not password:
            return Response(
                {'error': 'Password diperlukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = UserService.create_user(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=password,
                organization_name=request.data.get('organization_name', ''),
                role=request.data.get('role', 'user')
            )
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset password user."""
        new_password = request.data.get('password')
        if not new_password:
            return Response(
                {'error': 'Password baru diperlukan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = UserService.reset_password(pk, new_password)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except ResourceNotFound as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile with quota and premium status."""
        from scanner.services import QuotaService
        
        user = request.user
        quota_status = None
        
        # Get quota status if not admin/staff
        if not (user.is_superuser or user.is_staff):
            quota_status_data = QuotaService.check_quota(user)
            quota_status = {
                'quota_limit': quota_status_data['quota_limit'],
                'used_quota': quota_status_data['used_quota'],
                'remaining_quota': quota_status_data['remaining_quota'],
                'is_unlimited': quota_status_data['is_unlimited'],
                'can_scan': quota_status_data['can_scan'],
                'reset_period': quota_status_data['reset_period'],
                'next_reset': quota_status_data['next_reset'],
                'last_reset': quota_status_data['last_reset'],
            }
        
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
            'organization_name': getattr(user, 'organization_name', ''),
            'role': getattr(user, 'role', 'user'),
            'is_active': user.is_active,
            'is_premium': getattr(user, 'is_premium', False),
            'quota_status': quota_status,
            'date_joined': user.date_joined,
        }
        
        serializer = UserProfileSerializer(profile_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def quota_status(self, request):
        """Get quota status for current user."""
        from scanner.services import QuotaService
        
        user = request.user
        
        # Admin/staff have unlimited quota
        if user.is_superuser or user.is_staff:
            return Response({
                'quota_limit': 0,
                'used_quota': 0,
                'remaining_quota': -1,
                'is_unlimited': True,
                'can_scan': True,
                'reset_period': 'never',
                'next_reset': None,
                'last_reset': None,
            })
        
        quota_status_data = QuotaService.check_quota(user)
        serializer = QuotaStatusSerializer(quota_status_data)
        return Response(serializer.data)


class DomainScanSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet untuk melihat domain scan summary.
    """
    serializer_class = DomainScanSummarySerializer
    permission_classes = [IsAuthenticated]
    queryset = DomainScanSummary.objects.all().order_by('-last_scan')


class SistemConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola konfigurasi sistem.
    Hanya admin yang bisa mengakses dan mengubah.
    """
    serializer_class = SistemConfigSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Hanya satu record konfigurasi sistem."""
        return SistemConfig.objects.all()
    
    def get_object(self):
        """
        Mengembalikan instance konfigurasi aktif (yang pertama).
        Override untuk mendukung singleton pattern.
        """
        return SistemConfig.get_active_config()
    
    def list(self, request, *args, **kwargs):
        """
        List semua konfigurasi (hanya akan ada satu).
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Mendapatkan konfigurasi aktif.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        Update konfigurasi sistem.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Set updated_by
        serializer.save(updated_by=request.user)
        
        # Log activity
        try:
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE_SYSTEM_CONFIG',
                details=f'Updated system configuration: {", ".join(request.data.keys())}'
            )
        except Exception as e:
            pass  # Don't fail if logging fails
        
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create di-disable karena hanya boleh ada satu konfigurasi.
        Gunakan update() untuk mengubah konfigurasi.
        """
        config = SistemConfig.get_active_config()
        serializer = self.get_serializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Endpoint khusus untuk mendapatkan konfigurasi aktif.
        Lebih user-friendly dari retrieve.
        """
        instance = SistemConfig.get_active_config()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reset_to_default(self, request):
        """
        Reset konfigurasi ke default values.
        Hanya untuk admin.
        """
        try:
            # Create new config dengan default values
            SistemConfig.objects.all().delete()
            default_config = SistemConfig.objects.create(updated_by=request.user)
            
            ActivityLog.objects.create(
                user=request.user,
                action='RESET_SYSTEM_CONFIG',
                details='Reset system configuration to default values'
            )
            
            serializer = self.get_serializer(default_config)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Gagal reset konfigurasi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola API Keys.
    Hanya admin yang bisa mengakses.
    """
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get all API keys ordered by creation date."""
        return ApiKey.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by saat membuat API key."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle status aktif/nonaktif API key."""
        apikey = self.get_object()
        apikey.is_active = not apikey.is_active
        apikey.save()
        
        ActivityLog.objects.create(
            user=request.user,
            action='TOGGLE_API_KEY',
            details=f'Toggled API key {apikey.key_name} to {"active" if apikey.is_active else "inactive"}'
        )
        
        serializer = self.get_serializer(apikey)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update API key dengan logging."""
        instance = self.get_object()
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
    """
    ViewSet untuk mengelola Production Settings.
    Hanya admin yang bisa mengakses dan mengubah.
    Singleton pattern - hanya ada satu record.
    """
    serializer_class = ProductionSettingsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Hanya ada satu record production settings."""
        return ProductionSettings.objects.all()
    
    def get_object(self):
        """
        Mengembalikan instance settings aktif (yang pertama).
        Override untuk mendukung singleton pattern.
        """
        return ProductionSettings.get_active_settings()
    
    def list(self, request, *args, **kwargs):
        """List semua settings (hanya akan ada satu)."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Mendapatkan production settings aktif."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, pk=None, *args, **kwargs):
        """Update production settings."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Set updated_by
        serializer.save(updated_by=request.user)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE_PRODUCTION_SETTINGS',
            details=f'Updated production settings'
        )
        
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create settings baru jika belum ada, atau update yang existing.
        """
        settings_obj = ProductionSettings.get_active_settings()
        serializer = self.get_serializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Endpoint khusus untuk mendapatkan settings aktif."""
        instance = ProductionSettings.get_active_settings()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reset_to_default(self, request):
        """Reset settings ke default values."""
        try:
            ProductionSettings.objects.all().delete()
            default_settings = ProductionSettings.objects.create(updated_by=request.user)
            
            ActivityLog.objects.create(
                user=request.user,
                action='RESET_PRODUCTION_SETTINGS',
                details='Reset production settings to default values'
            )
            
            serializer = self.get_serializer(default_settings)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Gagal reset settings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

