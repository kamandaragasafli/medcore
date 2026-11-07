"""
Context processors for subscription app
"""
from .models import Notification


def notifications(request):
    """Add unread notification count and subscription info to template context"""
    unread_count = 0
    subscription = None
    plan_type = None
    company = None
    
    if request.user.is_authenticated:
        # Get company from request if available
        if hasattr(request, 'company') and request.company:
            company = request.company
        else:
            # Try to get company from user profile
            try:
                company = request.user.profile.company
            except:
                company = None
        
        if company:
            try:
                unread_count = Notification.objects.filter(
                    company=company,
                    is_read=False
                ).count()
            except:
                unread_count = 0
            
            # Get subscription info
            try:
                subscription = company.active_subscription
                if subscription and subscription.plan:
                    plan_type = subscription.plan.plan_type
                else:
                    # Default to basic if no subscription found
                    plan_type = 'basic'
                    subscription = None  # Ensure subscription is None if not found
            except Exception as e:
                # Log error but default to basic
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error getting subscription for context: {e}")
                plan_type = 'basic'
                subscription = None
    
    return {
        'unread_notification_count': unread_count,
        'subscription': subscription,
        'plan_type': plan_type,
        'company': company,
    }

