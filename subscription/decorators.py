from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import ContractAgreement


def contract_required(view_func):
    """
    Decorator to require contract agreement
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        # Superusers can bypass contract check
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Skip contract check for contract view itself and subscription pages
        if (request.path.startswith('/subscription/contract') or 
            request.path.startswith('/subscription/plans') or
            request.path.startswith('/subscription/register')):
            return view_func(request, *args, **kwargs)
        
        try:
            user_profile = request.user.profile
            company = user_profile.company
            
            # Check if contract is agreed (refresh from DB to get latest value)
            try:
                contract = ContractAgreement.objects.get(company=company, user=request.user)
                if not contract.agreed:
                    messages.info(request, 'Xidmət şərtləri ilə razılaşmalısınız.')
                    return redirect('subscription:contract')
            except ContractAgreement.DoesNotExist:
                # Contract not created yet, redirect to contract
                messages.info(request, 'Xidmət şərtləri ilə razılaşmalısınız.')
                return redirect('subscription:contract')
        except:
            # Profile doesn't exist, allow through (will be caught by subscription_required)
            pass
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def subscription_required(view_func):
    """
    Decorator to require active subscription
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        # Superusers can bypass subscription check, but still try to get company
        if request.user.is_superuser:
            # Try to get company from user profile
            if hasattr(request.user, 'profile') and request.user.profile and hasattr(request.user.profile, 'company'):
                request.company = request.user.profile.company
            return view_func(request, *args, **kwargs)
        
        if not hasattr(request, 'company') or not request.company:
            messages.error(request, 'No company associated with your account. Please contact support.')
            return redirect('core:login')
        
        # Get subscription (including pending ones)
        subscription = request.company.subscriptions.filter(
            status__in=['active', 'pending']
        ).order_by('-created_at').first()
        
        if not subscription:
            messages.warning(request, 'No active subscription. Please subscribe to continue.')
            return redirect('core:login')
        
        # If pending, check if contract is agreed and activate subscription
        if subscription.status == 'pending':
            try:
                contract = ContractAgreement.objects.get(
                    company=request.company,
                    user=request.user
                )
                if contract.agreed:
                    # Contract agreed, activate subscription
                    subscription.status = 'active'
                    subscription.save()
                else:
                    # Contract not agreed yet, redirect to contract
                    return redirect('subscription:contract')
            except ContractAgreement.DoesNotExist:
                # Contract not created yet, redirect to contract
                return redirect('subscription:contract')
        
        # Removed trial check since we're requiring payment now
        if subscription.status == 'expired':
            messages.error(request, 'Your subscription has expired. Please renew to continue.')
            return redirect('core:login')
        
        if subscription.status == 'suspended':
            messages.error(request, 'Your subscription has been suspended. Please contact support.')
            return redirect('core:login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def owner_required(view_func):
    """
    Decorator to require company owner role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if not hasattr(request, 'user_role') or request.user_role != 'owner':
            messages.error(request, 'Only company owners can access this page.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_or_owner_required(view_func):
    """
    Decorator to require admin or owner role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if not hasattr(request, 'user_role') or request.user_role not in ['owner', 'admin']:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

