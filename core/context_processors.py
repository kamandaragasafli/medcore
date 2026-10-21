"""
Context processors for templates
"""
from django.conf import settings


def system_branding(request):
    """
    Add system branding information to all templates
    """
    return {
        'SYSTEM_NAME': getattr(settings, 'SYSTEM_NAME', 'MedCore'),
        'SYSTEM_SUBTITLE': getattr(settings, 'SYSTEM_SUBTITLE', ''),
        'SYSTEM_LOGO': getattr(settings, 'SYSTEM_LOGO', 'img/icon.png'),
        'SYSTEM_FAVICON': getattr(settings, 'SYSTEM_FAVICON', 'img/icon.png'),
        'CHATBOT_ENABLED': getattr(settings, 'CHATBOT_ENABLED', False),
    }
