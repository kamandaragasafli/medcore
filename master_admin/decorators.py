"""
Decorators for Master Admin Panel
- Ensures only superusers can access
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def superuser_required(view_func):
    """
    Decorator to ensure only superusers can access Master Admin Panel.
    Regular users and staff are denied access.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(
                request,
                'Bu bölməyə yalnız sistem administratoru daxil ola bilər.'
            )
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

