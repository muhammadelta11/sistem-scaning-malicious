"""
Context processors untuk menyediakan data global ke semua template.
"""
import logging
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def quota_status(request):
    """
    Menambahkan quota_status ke context untuk user client.
    """
    context = {}
    
    try:
        if request.user.is_authenticated:
            # Hanya untuk user client (bukan admin/staff)
            # Cek dengan cara yang lebih eksplisit
            is_admin = getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False)
            
            if not is_admin:
                try:
                    from scanner.services import QuotaService
                    quota_status_data = QuotaService.check_quota(request.user)
                    context['quota_status'] = quota_status_data
                    logger.debug(f"Quota status loaded for {request.user.username}: {quota_status_data}")
                except Exception as e:
                    # Log error tapi jangan crash
                    logger.warning(f"Error loading quota status for {request.user.username}: {e}", exc_info=True)
                    context['quota_status'] = None
            else:
                context['quota_status'] = None
        else:
            context['quota_status'] = None
    except Exception as e:
        # Fallback jika ada error lain
        logger.error(f"Error in quota_status context processor: {e}", exc_info=True)
        context['quota_status'] = None
    
    return context


def partnerships(request):
    """
    Menambahkan partnerships/sponsorships ke context untuk ditampilkan di footer.
    """
    context = {}
    
    try:
        from scanner.models import Partnership
        # Get all active partnerships
        partnerships_list = Partnership.objects.filter(is_active=True).order_by('display_order', 'name')
        context['partnerships'] = partnerships_list
    except Exception as e:
        # Log error tapi jangan crash
        logger.warning(f"Error loading partnerships: {e}", exc_info=True)
        context['partnerships'] = []
    
    return context
