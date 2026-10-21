"""
Decorators for chatbot feature - only available for Professional and Enterprise plans
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def chatbot_required(view_func):
    """
    Decorator to ensure chatbot is enabled and user has Professional or Enterprise plan
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from django.conf import settings
        if not getattr(settings, 'CHATBOT_ENABLED', False):
            messages.info(request, 'AI Chatbot hazırda deaktivdir.')
            return redirect('core:dashboard')

        if not hasattr(request, 'company') or not request.company:
            messages.error(request, 'Şirkət məlumatı tapılmadı.')
            return redirect('core:login')
        
        subscription = request.company.active_subscription
        if not subscription or not subscription.plan:
            messages.error(request, 'Aktiv abunəlik tapılmadı.')
            return redirect('subscription:plans')
        
        plan_type = subscription.plan.plan_type
        if plan_type not in ['professional', 'enterprise']:
            messages.warning(
                request, 
                'AI Chatbot xüsusiyyəti yalnız Professional və Enterprise planlar üçün mövcuddur. '
                'Planınızı yüksəltmək üçün abunəlik səhifəsinə baxın.'
            )
            return redirect('subscription:plans')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

